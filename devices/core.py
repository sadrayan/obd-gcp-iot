import argparse
import datetime
import logging
import os
import random
import ssl
import time
import json
import jwt
import threading
import paho.mqtt.client as mqtt

import configparser

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.CRITICAL)

minimum_backoff_time = 1

MAXIMUM_BACKOFF_TIME = 32

should_backoff = False

class Core:

    def __init__(self, config):
        self.project_id = config['project_id']
        self.registry_id = config['registry_id']
        self.cloud_region = config['cloud_region']
        self.cloud_zone = config['cloud_zone']
        
        self.device_id = config['device_id']
        self.gateway_id = config['gateway_id']
        self.jwt_expires_minutes = config['jwt_expires_minutes']
        self.message_type = config['message_type']
        self.mqtt_bridge_hostname = config['mqtt_bridge_hostname'] 
        self.mqtt_bridge_port = int(config['mqtt_bridge_port'])
        
        self.algorithm = config['algorithm']
        self.ca_certs = config['ca_certs']
        self.private_key_file = config['private_key_file']

        self.mqtt_config_topic  = '/devices/{}/config'.format(config['device_id'])
        self.mqtt_command_topic = '/devices/{}/commands/#'.format(config['device_id'])

        # Publish to the events or state topic based on the flag.
        self.sub_topic = 'events' if self.message_type == 'event' else 'state'
        self.mqtt_topic = '/devices/{}/{}'.format(self.device_id, self.sub_topic)

        self.lock = threading.Lock()

        self.client = self.get_client(
            self.project_id, self.cloud_region, self.registry_id,
            self.device_id, self.private_key_file, self.algorithm,
            self.ca_certs, self.mqtt_bridge_hostname, self.mqtt_bridge_port)

        # Process network events.
        self.client.loop_start()


    def create_jwt(self, project_id, private_key_file, algorithm):
        token = {
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
            'aud': project_id
        }

        with open(private_key_file, 'r') as f:
            private_key = f.read()

        print('Creating JWT using {} from private key file {}'.format(algorithm, private_key_file))

        return jwt.encode(token, private_key, algorithm=algorithm)

    def error_str(rc):
        return '{}: {}'.format(rc, mqtt.error_string(rc))

    def on_connect(self, client, unused_userdata, unused_flags, rc):
        print('on_connect', mqtt.connack_string(rc))
        # Subscribe 
        print('Subscribing to {}'.format(self.mqtt_config_topic))
        client.subscribe(self.mqtt_config_topic, qos=1)
        print('Subscribing to {}'.format(self.mqtt_command_topic))
        client.subscribe(self.mqtt_command_topic, qos=1)

    def on_disconnect(self, client, unused_userdata, rc):
        print('on_disconnect', error_str(rc))
        # re-connect
        self.client.connect(gateway_state.mqtt_bridge_hostname, gateway_state.mqtt_bridge_port)


    def on_publish(self, unused_client, unused_userdata, unused_mid):
        # print('on_publish')
        pass


    def on_message(self, unused_client, unused_userdata, message):
        payload = str(message.payload.decode('utf-8'))
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
                payload, message.topic, str(message.qos)))

    def on_subscribe(unused_client, unused_userdata, mid, granted_qos):
        print('on_subscribe: mid {}, qos {}'.format(mid, granted_qos))

    def get_client(
            self, project_id, cloud_region, registry_id, device_id, private_key_file,
            algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port):
        client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
                project_id, cloud_region, registry_id, device_id)
        print('Device client_id is \'{}\''.format(client_id))

        client = mqtt.Client(client_id=client_id)

        client.username_pw_set(
                username='unused',
                password=self.create_jwt(
                        project_id, private_key_file, algorithm))

        client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

        client.on_connect    = self.on_connect
        client.on_publish    = self.on_publish
        client.on_disconnect = self.on_disconnect
        client.on_message    = self.on_message
        client.on_subscribe  = self.on_subscribe

        client.connect(mqtt_bridge_hostname, mqtt_bridge_port)
        
        return client


    def publish_message(self, payload):
        with self.lock:
            print('Publishing message {}'.format(payload))
            infot = self.client.publish(self.mqtt_topic, payload, qos=1)
            infot.wait_for_publish()
