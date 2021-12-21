#!/bin/bash

python -m venv env
source env/bin/activate
pip install -r requirements.txt
mkdir -p deployment
cd env/lib/python3.8/site-packages/
date=$(date '+%Y_%m_%d_%H:%M:%S')
zip -r9 ${OLDPWD}/deployment/rpi-package.zip#$date .
cd $OLDPWD
zip -g deployment/rpi-package.zip#$date *.py config.ini resources/*.pem
echo "done creating deployment" && ls deployment/ && pwd