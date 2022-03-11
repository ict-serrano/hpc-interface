pipeline {
    environment {
        PROJECT_NAME = 'hpc-interface'
        DEPLOY = "${env.GIT_BRANCH == "origin/main" || env.GIT_BRANCH == "origin/develop" ? "true" : "false"}"
        NAME = "${env.GIT_BRANCH == "origin/main" ? "hpc-interface" : "hpc-interface-staging"}"
        VERSION = '0.0.1'
        DOMAIN = 'localhost'
        REGISTRY = 'serrano-harbor.rid-intrasoft.eu/serrano/hpc-interface'
        REGISTRY_URL = 'https://serrano-harbor.rid-intrasoft.eu/serrano'
        REGISTRY_CREDENTIAL = 'harbor-jenkins'
    }
    agent {
        kubernetes {
            defaultContainer 'jnlp'
            yamlFile 'build.yaml'
        }
    }
    stages {
        stage('Install requirements') {
            steps {
                container('python') {
                    sh '/usr/local/bin/python -m pip install --upgrade pip'
                    sh 'pip install -r requirements.txt'
                    sh 'apt update -y && apt install -y default-jre wget'
                    sh './generate.sh'
                }
            }
        }
        stage('Unit tests') {
            steps {
                container('python') {
                    sh 'pytest src/tests'
                }
            }
        }
        stage('Sonarqube') {
            environment {
                scannerHome = tool 'SonarQubeScanner'
            }
            steps {
                container('java') {
                    withSonarQubeEnv('sonarqube') {
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=${PROJECT_NAME}"
                    }
                    timeout(time: 10, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }
        stage('Docker Build') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('docker') {
                    sh "docker build -t ${REGISTRY}:${VERSION} ."
                }
            }
        }
        stage('Docker Publish') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('docker') {
                    withDockerRegistry([credentialsId: "${REGISTRY_CREDENTIAL}", url: "${REGISTRY_URL}"]) {
                        sh "docker push ${REGISTRY}:${VERSION}"
                    }
                }
            }
        }
        stage('Docker Deploy') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('docker') {
                    sh "docker run -ti --rm -p 8080:8080 --name ${NAME}-${VERSION} ${REGISTRY}:${VERSION}"
                }
            }
        }
        stage('Integration Tests') {
            steps {
                script {
                    echo 'Run your Integration Tests here'
                    sleep 50
                    try {
                        String testName = "1. Check that app is running - 200 response code"
                        String url = "http://localhost:8080/services"
                        String responseCode = sh(label: testName, script: "curl -m 10 -sLI -w '%{http_code}' $url -o /dev/null", returnStdout: true)

                        if (responseCode != '200') {
                            error("$testName: Returned status code = $responseCode when calling $url")
                        }
                    } catch (ignored) {
                        currentBuild.result = 'FAILURE'
                        echo "Integration Tests failed"
                    }
                }
            }
        }
        stage('Docker Undeploy') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('docker') {
                    // don't fail if container was already stopped
                    sh "docker stop ${NAME}-${VERSION} || true"
                }
            }
        }

// TODO: Clear any redundant services

//         stage('Kubernetes Deploy') {
//             when {
//                 environment name: 'DEPLOY', value: 'true'
//             }
//             steps {
//                 container('helm') {
//                     sh "helm upgrade --install --force  --namespace integration --set name=${NAME} --set image.tag=${VERSION} --set domain=${DOMAIN} ${NAME} ./helm"
//                 }
//             }
//         }
//        stage('Integration Tests') {
//            echo 'Run your Integration Tests here'
//            sleep 50
//            try {
//                String testName = "1. Check that app is running - 200 response code"
//                String url = "http://integration-test-sample:8090/"
//                String responseCode = sh(label: testName, script: "curl -m 10 -sLI -w '%{http_code}' $url -o /dev/null", returnStdout: true)
//
//                if (responseCode != '200') {
//                    error("$testName: Returned status code = $responseCode when calling $url")
//                }
//
//                testName = "2. Look for record that doesn't exist - 404 response code"
//                url = "http://integration-test-sample:8090/records/1"
//                responseCode = sh(label: testName, script: "curl -m 10 -sLI -w '%{http_code}' $url -o /dev/null", returnStdout: true)
//
//                if (responseCode != '404') {
//                    error("$testName: Returned status code = $responseCode when calling $url")
//                }
//
//                testName = '3. Create record - 200 response code'
//                url = "http://integration-test-sample:8090/records"
//                responseCode = sh(label: testName, script: """curl -m 10 -s -w '%{http_code}' --request POST $url --header 'Content-Type: application/json' --data-raw '{"id":1,"balance":10.00}' -o /dev/null""", returnStdout: true)
//
//                if (responseCode != '200') {
//                    error("$testName: Returned status code = $responseCode when calling $url")
//                }
//
//                testName = '4. Retrieve record - JSON body'
//                url = "http://integration-test-sample:8090/records/1"
//                String responseBody = sh(label: testName, script: """curl -m 10 -sL $url --header 'Content-Type: application/json'""", returnStdout: true)
//
//                if (responseBody != '{"id":1,"balance":10.00}') {
//                    error("$testName: Unexpected response body = $responseBody when calling $url")
//                }
//
//                testName = '5. Update record - 200 response code'
//                url = "http://integration-test-sample:8090/records/1/recharges"
//                responseCode = sh(label: testName, script: """curl -m 10 -s -w '%{http_code}' --request POST $url --header 'Content-Type: application/json' --data-raw '{"amount":10.00}' -o /dev/null""", returnStdout: true)
//
//                if (responseCode != '200') {
//                    error("$testName: Returned status code = $responseCode when calling $url")
//                }
//
//                testName = '6. Check updated record - JSON body'
//                url = "http://integration-test-sample:8090/records/1"
//                responseBody = sh(label: testName, script: """curl -m 10 -sL $url --header 'Content-Type: application/json'""", returnStdout: true)
//
//                if (responseBody != '{"id":1,"balance":20.00}') {
//                    error("$testName: Unexpected response body = $responseBody when calling $url")
//                }
//            } catch (ignored) {
//                currentBuild.result = 'FAILURE'
//                echo "Integration Tests failed"
//            }
//        }
    }
}