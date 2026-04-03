pipeline {
  agent any

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }

  environment {
    APP_NAME = 'flask-demo'
    REGISTRY = 'nexus:8083'
    IMAGE_REPOSITORY = "${REGISTRY}/demo/${APP_NAME}"
    IMAGE_TAG = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
    GITOPS_REPO_URL = 'git@github.com:pouyaarjomandi/gitops.git'
    GITOPS_BRANCH = 'main'
    SLACK_CHANNEL = '#deployments'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Install Dependencies') {
      steps {
        sh 'python3 -m venv .venv'
        sh '. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt'
      }
    }

    stage('Run Unit Tests') {
      steps {
        sh 'mkdir -p reports'
        sh '. .venv/bin/activate && python -m pytest --junitxml=reports/junit.xml'
      }
      post {
        always {
          junit 'reports/junit.xml'
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        sh 'docker build -t ${IMAGE_REPOSITORY}:${IMAGE_TAG} .'
      }
    }

    stage('Push Image To Nexus') {
      when {
        anyOf {
          branch 'develop'
          branch 'staging'
          branch 'main'
        }
      }
      steps {
        withCredentials([usernamePassword(credentialsId: 'nexus-creds', usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASSWORD')]) {
          sh 'echo "$NEXUS_PASSWORD" | docker login ${REGISTRY} --username "$NEXUS_USER" --password-stdin'
          sh 'docker push ${IMAGE_REPOSITORY}:${IMAGE_TAG}'
        }
      }
    }

    stage('Update GitOps Repo') {
      when {
        anyOf {
          branch 'develop'
          branch 'staging'
          branch 'main'
        }
      }
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'gitops-ssh-key', keyFileVariable: 'SSH_KEY')]) {
          sh '''
            rm -rf gitops-workdir
            GIT_SSH_COMMAND="ssh -i $SSH_KEY -o StrictHostKeyChecking=no" git clone --branch ${GITOPS_BRANCH} ${GITOPS_REPO_URL} gitops-workdir

            if [ "${BRANCH_NAME}" = "develop" ]; then
              TARGET_FILE="gitops-workdir/apps/dev/values.yaml"
            elif [ "${BRANCH_NAME}" = "staging" ]; then
              TARGET_FILE="gitops-workdir/apps/staging/values.yaml"
            else
              TARGET_FILE="gitops-workdir/apps/prod/values.yaml"
            fi

            sed -i "s|tag: .*|tag: ${IMAGE_TAG}|" "$TARGET_FILE"

            cd gitops-workdir
            git config user.name "Jenkins CI"
            git config user.email "jenkins@example.local"
            git add .
            git commit -m "chore: promote ${APP_NAME} image to ${IMAGE_TAG}" || true
            GIT_SSH_COMMAND="ssh -i $SSH_KEY -o StrictHostKeyChecking=no" git push origin ${GITOPS_BRANCH}
          '''
        }
      }
    }
  }

  post {
    success {
      slackSend channel: "${SLACK_CHANNEL}", color: 'good', message: "SUCCESS: ${JOB_NAME} #${BUILD_NUMBER} (${BRANCH_NAME}) pushed ${IMAGE_REPOSITORY}:${IMAGE_TAG}"
    }
    failure {
      slackSend channel: "${SLACK_CHANNEL}", color: 'danger', message: "FAILED: ${JOB_NAME} #${BUILD_NUMBER} (${BRANCH_NAME})"
    }
    cleanup {
      sh 'docker rmi ${IMAGE_REPOSITORY}:${IMAGE_TAG} || true'
      cleanWs()
    }
  }
}