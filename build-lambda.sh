#!/bin/bash

# Put sensitive info here, which doesn't get imported into github
source ./secrets.bash

BUILD_DIR=${PWD};
lambda_function_VIRTUALENV=".";

echo "Rebuilding Deployment Package...";
cd ${lambda_function_VIRTUALENV}/lib/python3.7/site-packages
zip -r9 ${BUILD_DIR}/lambda_function.zip *
cd ${BUILD_DIR};

to_remove="astroid idna isort lazy-object-proxy mccabe pylint six wrapt pip setuptools";

# Remove unnecessary dev libraries from lambda upload package 
for i in ${to_remove}; do
    zip -d lambda_function.zip "${i}/*";
done 

zip -g lambda_function.zip lambda_function.py;
zip -g lambda_function.zip local_config.py;