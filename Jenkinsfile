@Library("shared-jenkins")_
pipeline {

    agent any

    options {
        // Pipeline options
        ansiColor('xterm')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: "25", artifactNumToKeepStr: "25"))
        disableConcurrentBuilds()
    }

    stages {
        stage('Building packages') {
            steps {
                sh '''\
                    set -ex
                    rm -f lastfm-* 
                    docker run -e OWNER="$(id -u $USER):$(id -g $USER)" --rm -w /app-src -v $(pwd):/app-src gcr.io/i-lastfm-tools/ubuntu-trusty-buildenv ./pybuild.sh
                '''.stripIndent()
                script {
                    if (env.BRANCH_NAME == 'master') {
                        println("Uploading artifacts to the nexus")
                        findFiles(glob: './*.deb').each {
                            utilities.uploadDebian(it.path)
                        }
                    }
                    
                }
            }
        }
    }

    post {
        always {
            cleanWs cleanWhenFailure: false
        }
    }
}
