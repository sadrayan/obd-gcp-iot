#!/bin/bash

pip install -r requirements.txt
cd env/lib/python3.7/site-packages/
zip -r9 ${OLDPWD}/deployment/rpi-package.zip .
cd $OLDPWD
zip -g deployment/rpi-package.zip *.py config.ini resources/*.pem