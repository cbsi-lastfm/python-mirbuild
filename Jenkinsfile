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
            agent {
                docker { 
                    image 'gcr.io/i-lastfm-tools/ubuntu-trusty-buildenv' 
                    args '-u root:sudo -v /etc/passwd:/etc/passwd -v /etc/group:/etc/group'
                }
            }
            steps {
                script {
                    sh """
                        ./pybuild.sh
                        chown -R jenkins:jenkins .
                    """.stripIndent()
                }
                stash includes: '*.deb', name: 'deb_artifacts'
            }
        }
        stage("Upload artifacts to nexus"){
            when {
                branch 'master'
            }
            steps{
                script {
                    unstash 'deb_artifacts'
                    println("Uploading artifacts to the nexus")
                    findFiles(glob: './*.deb').each {
                        utilities.uploadDebian(it.path)
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
