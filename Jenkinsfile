pipeline {
    agent any

    environment {
        FULL_DOCKER_IMAGE_NAME = 'thevirtualbrain/tvb-run'
        PY3_TAG = 'tvb-library-py3'
    }

    stages {

        stage ('Build Pypi package for Python 3') {
            agent {
                docker {
                    image '${FULL_DOCKER_IMAGE_NAME}:${PY3_TAG}'
                }
            }
            steps {
                sh '''#!/bin/bash
                      source activate tvb-run
                      python setup.py sdist
                      python setup.py bdist_wheel
                '''
                archiveArtifacts artifacts: 'dist/*'
            }
        }
    }

    post {
        changed {
            mail to: 'lia.domide@codemart.ro',
            subject: "Jenkins Pipeline ${currentBuild.fullDisplayName} changed status",
            body: """
                Result: ${currentBuild.result}
                Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'
                Check console output at ${env.BUILD_URL}"""
        }

        success {
            echo 'Build finished successfully'
        }
    }
}