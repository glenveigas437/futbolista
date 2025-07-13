pipeline {
    agent any
    environment {
        VENV = 'venv'
    }
    stages {
        stage('Build') {
            steps {
                sh 'python3 -m venv $VENV'
                sh './venv/bin/pip install --upgrade pip'
                sh './venv/bin/pip install -r futbolista/requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh './venv/bin/pip install pytest'
                sh './venv/bin/pytest futbolista/tests'
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