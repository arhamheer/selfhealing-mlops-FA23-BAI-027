pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USER = 'arhamheer'
        IMAGE_UNSTABLE = "${DOCKERHUB_USER}/sentiment-api:unstable"
        IMAGE_STABLE   = "${DOCKERHUB_USER}/sentiment-api:stable"
        APP_CONTAINER  = "sentiment-app-test"
        APP_PORT       = "5000"
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh """
                    # Stop any existing test container
                    docker rm -f ${APP_CONTAINER} || true

                    # Build the unstable image
                    docker build -t ${IMAGE_UNSTABLE} .

                    # Run the container
                    docker run -d --name ${APP_CONTAINER} \
                        -p ${APP_PORT}:5000 \
                        -v /tmp/app-logs:/app/logs \
                        ${IMAGE_UNSTABLE}

                    # Wait for app to start
                    sleep 20

                    # Verify it's running
                    curl -f http://localhost:${APP_PORT}/health || exit 1
                """
            }
        }

        stage('Unit Test') {
            steps {
                sh """
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:${APP_PORT} \
                        -v \$(pwd)/tests:/tests \
                        ${IMAGE_UNSTABLE} \
                        bash -c "pip install pytest requests -q && pytest /tests/test_api.py -v --tb=short"
                """
            }
        }

        stage('UI Test') {
    steps {
        sh """
            docker run --rm \
                --network host \
                -v \$(pwd)/tests:/tests \
                -e APP_URL=http://100.50.10.159:32500 \
                --shm-size=2g \
                selenium/standalone-chrome:latest \
                bash -c "pip install selenium pytest requests -q && pytest /tests/test_ui.py -v --tb=short" || true
        """
    }
}

        stage('Build and Push') {
            steps {
                sh """
                    echo \${DOCKERHUB_CREDENTIALS_PSW} | docker login -u \${DOCKERHUB_CREDENTIALS_USR} --password-stdin

                    # Push unstable image
                    docker push ${IMAGE_UNSTABLE}

                    # Build stable image from stable-fallback branch
                    git stash || true
                    git fetch origin stable-fallback
                    git checkout origin/stable-fallback -- app.py || true
                    docker build -t ${IMAGE_STABLE} .
                    docker push ${IMAGE_STABLE}

                    # Restore main branch app.py
                    git checkout HEAD -- app.py || true
                """
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh """
                    export KUBECONFIG=/var/lib/jenkins/.kube/config

                    # Apply all Kubernetes manifests
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    # Wait for blue deployment to be ready
                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=120s

                    echo "Deployment complete. Service available at NodePort 32500"
                """
            }
        }

    }

    post {
        always {
            sh "docker rm -f ${APP_CONTAINER} || true"
            sh "docker logout || true"
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed. Check logs above."
        }
    }
}
