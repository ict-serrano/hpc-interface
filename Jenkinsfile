pipeline {
    environment {
        PROJECT_NAME = 'hpc-interface'
        DEPLOY = "${env.GIT_BRANCH == "origin/main" || env.GIT_BRANCH == "origin/develop" ? "true" : "false"}"
        NAME = "${env.GIT_BRANCH == "origin/main" ? "hpc-interface" : "hpc-interface-staging"}"
        DEPLOY_UVT = "${env.GIT_BRANCH == "origin/main" ? "true" : "false"}"
        CHART_NAME = "${env.GIT_BRANCH == "origin/main" ? "hpc-interface" : "hpc-interface-staging"}"
        VERSION = '0.1.0'
        DOMAIN = 'localhost'
        REGISTRY = 'serrano-harbor.rid-intrasoft.eu/serrano/hpc-interface'
        REGISTRY_URL = 'https://serrano-harbor.rid-intrasoft.eu/serrano'
        REGISTRY_CREDENTIAL = 'harbor-jenkins'
        UVT_KUBERNETES_PUBLIC_ADDRESS = 'k8s.serrano.cs.uvt.ro'
        INTEGRATION_OPERATOR_TOKEN = credentials('uvt-integration-operator-token')
    }
    agent {
        kubernetes {
            cloud 'kubernetes'
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
                    sh 'apt update -y && apt install -y default-jre wget gettext-base'
                    sh './generate.sh'
                }
            }
        }
        stage('Unit tests') {
            steps {
                container('python') {
                    withCredentials([\
                        file(\
                            credentialsId: 'test_infrastructure_fixture_excess_tmpl', \
                            variable: 'HPC_GATEWAY_TEST_INFRASTRUCTURE_FIXTURE_TMPL'\
                        ), \
                        sshUserPrivateKey(\
                            credentialsId: 'ssh-private-key-excess', \
                            keyFileVariable: 'HPC_GATEWAY_EXCESS_PRIVATE_KEY', \
                            passphraseVariable: 'HPC_GATEWAY_EXCESS_PRIVATE_KEY_PASSWORD', \
                            usernameVariable: 'HPC_GATEWAY_EXCESS_USERNAME')]) {
                        sh 'envsubst < $HPC_GATEWAY_TEST_INFRASTRUCTURE_FIXTURE_TMPL > src/tests/fixture.infrastructure.yaml'
                        sh 'pytest src/tests'
                    }
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
        stage('Deploy in INTRA Kubernetes') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('helm') {
                    sh "helm upgrade --install --force --wait --timeout 600s --namespace integration --set name=${CHART_NAME} --set image.tag=${VERSION} --set domain=${DOMAIN} ${CHART_NAME} ./helm"
                }
            }
        }
        stage('Integration Tests') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('java') {
                    script {
                        echo 'Running Integration Tests'
                        //sleep 20 // Sleep is not required if the readiness probe is enabled
                        try {
                            String testName = "1. Check that app is running - 200 response code"
                            String url = "http://${CHART_NAME}-${PROJECT_NAME}.integration:8080/services"
                            String responseCode = sh(label: testName, script: "curl -m 10 -sL -w '%{http_code}' $url -o /dev/null", returnStdout: true)

                            if (responseCode != '200') {
                                error("$testName: Returned status code = $responseCode when calling $url")
                            }

/*                            testName = '2. Create record - 201 response code'
                            url = "http://${CHART_NAME}-${PROJECT_NAME}.integration:8080/api/v1/puppies/"
                            responseCode = sh(label: testName, script: """curl -m 10 -s -w '%{http_code}' --request POST $url --header 'Content-Type: application/json' --data-raw '{"name":"Jack","age":3,"breed":"shepherd","color":"brown"}' -o /dev/null""", returnStdout: true)

                            if (responseCode != '201') {
                                 error("$testName: Returned status code = $responseCode when calling $url")
                            }

                            testName = '3. Validate stored records'
                            url = "http://${CHART_NAME}-${PROJECT_NAME}.integration:8080/api/v1/puppies"
                            String responseBody = sh(label: testName, script: """curl -m 10 -sL $url""", returnStdout: true)

                            if (responseBody != '[{"name":"Jack","age":3,"breed":"shepherd","color":"brown"}]') {
                                error("$testName: Unexpected response body = $responseBody when calling $url")
                            }*/

//                Other examples from CRUD methods can be found below:
//
//                testName = "4. Look for record that doesn't exist - 404 response code"
//                url = "http://integration-test-sample:8090/records/1"
//                responseCode = sh(label: testName, script: "curl -m 10 -sL -w '%{http_code}' $url -o /dev/null", returnStdout: true)
//
//                if (responseCode != '404') {
//                    error("$testName: Returned status code = $responseCode when calling $url")
//                }
//
//                testName = '5. Create record - 200 response code'
//                url = "http://integration-test-sample:8090/records"
//                responseCode = sh(label: testName, script: """curl -m 10 -s -w '%{http_code}' --request POST $url --header 'Content-Type: application/json' --data-raw '{"id":1,"balance":10.00}' -o /dev/null""", returnStdout: true)
//
//                if (responseCode != '200') {
//                    error("$testName: Returned status code = $responseCode when calling $url")
//                }
//
//                testName = '6. Retrieve record - JSON body'
//                url = "http://integration-test-sample:8090/records/1"
//                responseBody = sh(label: testName, script: """curl -m 10 -sL $url --header 'Content-Type: application/json'""", returnStdout: true)
//
//                if (responseBody != '{"id":1,"balance":10.00}') {
//                    error("$testName: Unexpected response body = $responseBody when calling $url")
//                }
//
//                testName = '7. Update record - 200 response code'
//                url = "http://integration-test-sample:8090/records/1/recharges"
//                responseCode = sh(label: testName, script: """curl -m 10 -s -w '%{http_code}' --request POST $url --header 'Content-Type: application/json' --data-raw '{"amount":10.00}' -o /dev/null""", returnStdout: true)
//
//                if (responseCode != '200') {
//                    error("$testName: Returned status code = $responseCode when calling $url")
//                }
//
//                testName = '8. Check updated record - JSON body'
//                url = "http://integration-test-sample:8090/records/1"
//                responseBody = sh(label: testName, script: """curl -m 10 -sL $url --header 'Content-Type: application/json'""", returnStdout: true)
//
//                if (responseBody != '{"id":1,"balance":20.00}') {
//                    error("$testName: Unexpected response body = $responseBody when calling $url")
//                }
                        } catch (ignored) {
                            currentBuild.result = 'FAILURE'
                            echo "Integration Tests failed"
                        }
                    }
                }
            }
        }
        stage('Cleanup INTRA Deployment') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('helm') {
                    sh "helm uninstall ${CHART_NAME} --namespace integration"
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