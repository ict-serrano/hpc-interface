#!/bin/sh

set -e
set -u

[ -f openapi-generator-cli-5.1.1.jar ] || wget https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/5.1.1/openapi-generator-cli-5.1.1.jar
rm -rf gen/
rm -rf src/hpc/api/controllers/openapi/
java -jar openapi-generator-cli-5.1.1.jar generate \
    --input-spec openapi-spec.yaml \
    --api-package api \
    --invoker-package invoker \
    --model-package models \
    --generator-name python-flask \
    --strict-spec true \
    --output gen/ \
    --config openapi-python-config.yaml
cp -r gen/hpc/api/openapi/ src/hpc/api/
rm -rf src/hpc/api/openapi/test/
rm -rf src/hpc/api/openapi/CONTROLLER_PACKAGE_MATCH_ANCHOR/
rm src/hpc/api/openapi/__main__.py
sed -i -E -e 's/(.*?) .*?CONTROLLER_PACKAGE_MATCH_ANCHOR.*$/\1 hpc.api.controllers.default/g' src/hpc/api/openapi/openapi/openapi.yaml