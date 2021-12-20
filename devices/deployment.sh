#!/bin/bash

python -m venv env
source env/bin/activate
pip install -r requirements.txt
mkdir -p deployment
cd env/lib/python3.8/site-packages/
zip -r9 ${OLDPWD}/deployment/rpi-package.zip#$1 .
cd $OLDPWD
zip -g deployment/rpi-package.zip#$1 *.py config.ini resources/*.pem
echo "done creating deployment" && pwd