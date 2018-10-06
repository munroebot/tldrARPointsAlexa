#!/bin/bash

# Put sensitive info here, which doesn't get imported into github
source ./secrets.bash

BUILD_DIR=${PWD};
lambda_function_VIRTUALENV=".";

echo "Rebuilding Deployment Package...";
cd ${lambda_function_VIRTUALENV}/lib/python3.7/site-packages
zip -r9 ${BUILD_DIR}/lambda_function.zip *
cd ${BUILD_DIR};
zip -d lambda_function.zip "pip/*";
zip -d lambda_function.zip "setuptools/*";
zip -g lambda_function.zip lambda_function.py;
zip -g lambda_function.zip local_config.py;