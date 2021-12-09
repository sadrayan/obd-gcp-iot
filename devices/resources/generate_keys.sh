#!/bin/bash

openssl req -x509 -newkey rsa:2048 -keyout resources/rsa_private.pem -nodes -out resources/rsa_cert.pem -subj "/CN=unused"