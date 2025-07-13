pipeline {
    agent any
    environment {
        VENV = 'venv'
        PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    }
    stages {
        stage('Build') {
            steps {
                sh 'which /usr/local/bin/python3.11 || which python3'
                sh '/usr/local/bin/python3.11 --version || python3 --version'
                sh '/usr/local/bin/python3.11 -m venv $VENV || python3 -m venv $VENV'
                sh './venv/bin/pip install --upgrade pip'
                sh './venv/bin/pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh './venv/bin/pip install pytest'
                sh './venv/bin/pytest tests'
            }

        }
        stage('Deploy') {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                echo 'Deploy to staging or production here (customize as needed)'
            }
        }
    }
    post {
        success {
            mail to: 'glenveigas4@gmail.com',
                 subject: "SUCCESS: Jenkins Build ${env.BUILD_NUMBER}",
                 body: "The build was successful!"
        }
        failure {
            mail to: 'glenveigas4@gmail.com',
                 subject: "FAILURE: Jenkins Build ${env.BUILD_NUMBER}",
                 body: "The build failed!"
        }
    }
} 

