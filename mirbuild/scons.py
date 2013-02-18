# -*- coding: utf-8 -*-
#
# Copyright © 2011-2013 Last.fm Limited
#
# This file is part of python-mirbuild.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

r"""
SCons specific classes

This file contains SCons specific implementations of mirbuild classes.

"""

__author__ = 'Sven Over <sven@last.fm>'
__all__ = 'SConsProject'.split()

import os, stat
import mirbuild.project, mirbuild.test, mirbuild.environment, mirbuild.dependency
from mirbuild.tools import ScopedChdir, LazyFileWriter

class SConsWriter(LazyFileWriter):
    def __init__(self, name):
        super(SConsWriter, self).__init__(name)

    def comment(self, str):
        self.write('# {0}\n'.format(str))

    def set(self, var, value):
        self.write('{0} = {1!r}\n'.format(var, value))

    def setmany(self, dict):
        self.write("".join('{0} = {1!r}\n'.format(key, value) for key,value in dict.iteritems()))

class SConsEnvironment(mirbuild.environment.Environment):
    def build(self, *args):
        self.execute(self.tool('scons'), *args)

    def install(self, *args):
        self.execute(self.tool('scons'), 'install', *args)

    def clean(self):
        self.execute(self.tool('scons'), '-c')

    def realclean(self):
        self.run_clean()
        self.remove_files('scons-local-config.py')

class SConsTestBuilder(mirbuild.test.TestBuilder):
    def __init__(self, env, dir, *args):
        super(SConsTestBuilder, self).__init__(env, dir, *args)

    def build(self):
        if self.dir is not None:
            #self._env.build(self.dir)
            if not self.tests:
                self.__find_tests()

    def __find_tests(self):
        for filename in os.listdir(self.dir):
            e = os.path.join(self.dir, filename)
            if os.path.isfile(e) and os.stat(e).st_mode & stat.S_IXUSR:
                self.add_test(e)

    #def clean(self):
        #if self.dir is not None:
            #scd = ScopedChdir(self.dir)
            #self._env.clean()
            #self._env.realclean()

class SConsProject(mirbuild.project.Project):
    test_builder_class = SConsTestBuilder
    environment_class = SConsEnvironment
    default_dependency_class = mirbuild.dependency.CLibraryDependency

    def __init__(self, name, **opts):
        mirbuild.project.Project.__init__(self, name, **opts)
        self.__defines = {}
        self.__incpath = []
        self.__libpath = []

    def define(self, name, value = None):
        if isinstance(name, basestring):
            self.__defines[name] = value
        else:
            self.__defines.update(name)

    def add_include_path(self, *args):
        self.__incpath.append(*args)

    def add_library_path(self, *args):
        self.__libpath.append(*args)

    def configure_release(self, slc):
        slc['CCFLAGS'] += '-Wall -O2 -g -DNDEBUG -fPIC'.split() # `getconf LFS_CFLAGS`

    def configure_debug(self, slc):
        slc['CCFLAGS'] += '-Wall -Wextra -ggdb -fPIC'.split() # `getconf LFS_CFLAGS`

    def configure_coverage(self, slc):
        slc['CCFLAGS'] += '-Wall -Wextra -ggdb -fPIC -fprofile-arcs -ftest-coverage'.split() # `getconf LFS_CFLAGS`
        slc['LINKFLAGS'] += '-fprofile-arcs -ftest-coverage'.split()

    def do_configure(self):
        slc = {
            'CPPPATH': list(os.path.realpath(i) for i in self.__incpath),
            'LIBPATH': list(os.path.realpath(i) for i in self.__libpath),
            'CPPDEFINES': self.__defines,
            'CCFLAGS': ['-Wall'],
            'LINKFLAGS': {},
            'PREFIX' :self.opt.prefix,
            }
        if self.env.has_tool('cxx'):
            slc['CXX'] = self.env.tool('cxx')
        if self.env.has_tool('cc'):
            slc['CC'] = self.env.tool('cc')

        getattr(self, 'configure_' + self.build_config)(slc)

        slcfile = LazyFileWriter('scons-local-config.py')
        slcfile.create()
        slcfile.write('# build configuration for {0} (generated by {1})\n'.format(self.project_name, self.ident))
        slcfile.write("".join(("{0} = {1!r}\n".format(i, slc[i])) for i in sorted(slc)))
        slcfile.commit()

    def do_build(self):
        self.env.build()

    def do_install(self):
        args = []
        if self.opt.install_destdir is not None:
            args.append('DESTDIR=' + self.opt.install_destdir)
        self.env.install(*args)

    def do_clean(self):
        self.env.clean()

    def do_realclean(self):
        self.do_clean()
        self.env.realclean()

    def run_test(self):
        self.do_test()

    def do_test(self):
        test_directories = list(i.dir for i in self.tests)
        if test_directories:
            self.env.build(*test_directories)
        super(SConsProject, self).do_test()