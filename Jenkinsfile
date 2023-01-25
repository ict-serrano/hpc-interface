pipeline {
    environment {
        PROJECT_NAME = 'hpc-interface'
        DEPLOY = "${env.GIT_BRANCH == "origin/main" || env.GIT_BRANCH == "origin/develop" ? "true" : "false"}"
        NAME = "${env.GIT_BRANCH == "origin/main" ? "hpc-interface" : "hpc-interface-staging"}"
        DEPLOY_UVT = "${env.GIT_BRANCH == "origin/main" ? "true" : "false"}"
        CHART_NAME = "${env.GIT_BRANCH == "origin/main" ? "hpc-interface" : "hpc-interface-staging"}"
        VERSION = '0.2.0'
        DOMAIN = 'localhost'
        REGISTRY = 'serrano-harbor.rid-intrasoft.eu/serrano/hpc-interface'
        REGISTRY_URL = 'https://serrano-harbor.rid-intrasoft.eu/serrano'
        REGISTRY_CREDENTIAL = 'harbor-jenkins'
        UVT_KUBERNETES_PUBLIC_ADDRESS = 'api.k8s.cloud.ict-serrano.eu'
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
                    sh 'apt update -y && apt install -y default-jre wget curl jq gettext-base'
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
                    withCredentials([\
                        sshUserPrivateKey(\
                            credentialsId: 'ssh-private-key-excess', \
                            keyFileVariable: 'HPC_GATEWAY_EXCESS_PRIVATE_KEY')]) {
                        sh 'kubectl delete secret hpc-interface-ssh-keys --namespace="integration" || true'
                        sh 'kubectl create secret generic hpc-interface-ssh-keys --namespace="integration" --from-file="$HPC_GATEWAY_EXCESS_PRIVATE_KEY" || true'
                    }
                    sh "helm upgrade --install --force --wait --timeout 600s --namespace integration --set name=${CHART_NAME} --set image.tag=${VERSION} --set domain=${DOMAIN} ${CHART_NAME} ./helm"
                }
            }
        }
        stage('Integration Tests') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
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
                        
                        sh 'envsubst < $HPC_GATEWAY_TEST_INFRASTRUCTURE_FIXTURE_TMPL > fixture.infrastructure.yaml'
                        sh 'curl -L --output yq https://github.com/mikefarah/yq/releases/download/v4.25.2/yq_linux_amd64 && chmod 700 yq'
                        sh 'KEY_PATH="/etc/ssh/hpc-interface/ssh-key-HPC_GATEWAY_EXCESS_PRIVATE_KEY" ./yq -i ".[].ssh_key.path = strenv(KEY_PATH)" fixture.infrastructure.yaml'
                        script {
                            echo 'Running Integration Tests'
                            try {
                                String testName = ""
                                String fixture = ""
                                String url = ""
                                String responseCode = ""
                                String responseBody = ""

                                testName = "1. Check that app is running - 200 response code"
                                url = "http://${CHART_NAME}.integration:8080/services"
                                responseCode = sh(label: testName, script: "curl -m 10 -sL -w '%{http_code}' $url -o /dev/null", returnStdout: true)

                                if (responseCode != '200') {
                                    error("$testName: Returned status code = $responseCode when calling $url")
                                }

                                testName = '2. Create infrastructure - 201 response code'
                                fixture = "fixture.infrastructure.yaml"
                                String infrastructure_data = sh(label: testName, script: """./yq e '.[1]' -I=0 -o=json $fixture""", returnStdout: true)
                                url = "http://${CHART_NAME}.integration:8080/infrastructure"
                                responseCode = sh(label: testName, script: """curl -m 10 -s -w '%{http_code}' --request POST $url --header 'Content-Type: application/json' --data-raw \'$infrastructure_data\' -o /dev/null""", returnStdout: true)

                                if (responseCode != '201') {
                                    error("$testName: Returned status code = $responseCode when calling $url")
                                }

                                testName = "3. Check new infrastructure - 200 response code"
                                url = "http://${CHART_NAME}.integration:8080/infrastructure/excess_slurm"
                                responseCode = sh(label: testName, script: "curl -m 10 -sL -w '%{http_code}' $url -o /dev/null", returnStdout: true)

                                if (responseCode != '200') {
                                    error("$testName: Returned status code = $responseCode when calling $url")
                                }

                                testName = "4. Check infrastructure telemetry - 200 response code"
                                url = "http://${CHART_NAME}.integration:8080/infrastructure/excess_slurm/telemetry"
                                responseCode = sh(label: testName, script: "curl -m 10 -sL -w '%{http_code}' $url -o /dev/null", returnStdout: true)

                                if (responseCode != '200') {
                                    error("$testName: Returned status code = $responseCode when calling $url")
                                }

                                testName = '5. Submit a job - 201 response code'
                                url = "http://${CHART_NAME}.integration:8080/job"
                                responseCode = sh(label: testName, script: """curl -m 10 -s -w '%{http_code}' --request POST $url --header 'Content-Type: application/json' --data-raw '{"infrastructure": "excess_slurm", "params": {}, "services": [{ "name": "test_filter", "version": "0.0.1" }]}' -o /dev/null""", returnStdout: true)

                                if (responseCode != '201') {
                                    error("$testName: Returned status code = $responseCode when calling $url")
                                }

                                testName = '6. Validate execution'
                                url = "http://${CHART_NAME}.integration:8080/job"
                                responseBody = sh(label: testName, script: """curl -m 10 -sL --request POST $url --header 'Content-Type: application/json' --data-raw '{"infrastructure": "excess_slurm", "params": {}, "services": [{ "name": "test_filter", "version": "0.0.1" }]}'""", returnStdout: true)
                                job_uuid = sh(label: testName, script: """echo \'$responseBody\' | jq -r '.id'""", returnStdout: true)
                                
                                url = "http://${CHART_NAME}.integration:8080/job/$job_uuid"
                                responseCode = sh(label: testName, script: "curl -m 10 -sL -w '%{http_code}' -o /dev/null $url", returnStdout: true)
                                if (responseCode != '200') {
                                    error("$testName: Returned status code = $responseCode when calling $url")
                                }

                                testName = '7. Submit a file transfer request - 201 response code'
                                url = "http://${CHART_NAME}.integration:8080/data"
                                responseCode = sh(label: testName, script: """curl -m 10 -s -w '%{http_code}' --request POST $url --header 'Content-Type: application/json' --data-raw '{"infrastructure": "excess_slurm", "src": "https://raw.githubusercontent.com/Ovi/DummyJSON/master/package.json", "dst": "/tmp/package.json"}' -o /dev/null""", returnStdout: true)

                                if (responseCode != '201') {
                                    error("$testName: Returned status code = $responseCode when calling $url")
                                }

                                testName = '8. Validate file transfer'
                                url = "http://${CHART_NAME}.integration:8080/data"
                                responseBody = sh(label: testName, script: """curl -m 10 -sL --request POST $url --header 'Content-Type: application/json' --data-raw '{"infrastructure": "excess_slurm", "src": "https://raw.githubusercontent.com/Ovi/DummyJSON/master/package.json", "dst": "/tmp/package.json"}'""", returnStdout: true)
                                ft_uuid = sh(label: testName, script: """echo \'$responseBody\' | jq -r '.id'""", returnStdout: true)
                                
                                url = "http://${CHART_NAME}.integration:8080/data/$ft_uuid"
                                responseCode = sh(label: testName, script: "curl -m 10 -sL -w '%{http_code}' -o /dev/null $url", returnStdout: true)
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
        stage('Deploy in UVT Kubernetes') {
            when {
                environment name: 'DEPLOY_UVT', value: 'true'
            }
            steps {
                container('helm') {
                    withCredentials([\
                        sshUserPrivateKey(\
                            credentialsId: 'ssh-private-key-excess', \
                            keyFileVariable: 'HPC_GATEWAY_EXCESS_PRIVATE_KEY')]) {
                        sh "kubectl config set-cluster kubernetes-uvt --certificate-authority=uvt.cer --embed-certs=true --server=https://${UVT_KUBERNETES_PUBLIC_ADDRESS}:6443"
                        sh "kubectl config set-credentials integration-operator --token=${INTEGRATION_OPERATOR_TOKEN}"
                        sh "kubectl config set-context kubernetes-uvt --cluster=kubernetes-uvt --user=integration-operator"
                        sh 'kubectl delete secret hpc-interface-ssh-keys --context="kubernetes-uvt" --namespace="integration" || true'
                        sh 'kubectl create secret generic hpc-interface-ssh-keys --context="kubernetes-uvt" --namespace="integration" --from-file="$HPC_GATEWAY_EXCESS_PRIVATE_KEY" || true'
                    }
                    sh "helm upgrade --debug --cleanup-on-fail --install --force --wait --timeout 600s --kube-context=kubernetes-uvt --namespace integration --set name=${CHART_NAME} --set image.tag=${VERSION} --set domain=${DOMAIN} ${CHART_NAME} ./helm-uvt"
                }
            }
        }
    }
}