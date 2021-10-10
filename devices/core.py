import argparse
import datetime
import logging
import os
import random
import ssl
import time
import json
import jwt
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

        print(self.private_key_file )

        # Publish to the events or state topic based on the flag.
        sub_topic = 'events' if self.message_type == 'event' else 'state'

        self.client = self.get_client(
            self.project_id, self.cloud_region, self.registry_id,
            self.device_id, self.private_key_file, self.algorithm,
            self.ca_certs, self.mqtt_bridge_hostname, self.mqtt_bridge_port)

        # Process network events.
        self.client.loop_start()


    def create_jwt(self, project_id, private_key_file, algorithm):
        token = {
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=20),
            'aud': project_id
        }

        with open(private_key_file, 'r') as f:
            private_key = f.read()

        print('Creating JWT using {} from private key file {}'.format(algorithm, private_key_file))

        return jwt.encode(token, private_key, algorithm=algorithm)

    def error_str(rc):
        return '{}: {}'.format(rc, mqtt.error_string(rc))


    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        print('on_connect', mqtt.connack_string(rc))
        global should_backoff
        global minimum_backoff_time
        should_backoff = False
        minimum_backoff_time = 1
        if (mqtt.connack_string(rc).contains('bad user name or password')):
            self.client.username_pw_set(
                username='unused',
                password=self.create_jwt(
                        self.project_id, self.private_key_file, self.algorithm))
            


    def on_disconnect(self, unused_client, unused_userdata, rc):
        print('on_disconnect', error_str(rc))
        global should_backoff
        should_backoff = True


    def on_publish(self, unused_client, unused_userdata, unused_mid):
        print('on_publish')


    def on_message(self, unused_client, unused_userdata, message):
        payload = str(message.payload.decode('utf-8'))
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
                payload, message.topic, str(message.qos)))


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

        client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

        # Subscribe 
        mqtt_config_topic  = '/devices/{}/config'.format(device_id)
        mqtt_command_topic = '/devices/{}/commands/#'.format(device_id)
        print('Subscribing to {}'.format(mqtt_config_topic))
        client.subscribe(mqtt_config_topic, qos=1)
        print('Subscribing to {}'.format(mqtt_command_topic))
        client.subscribe(mqtt_command_topic, qos=0)

        return client


    def publish_message(self, payload):
        print('Publishing message {}'.format(payload))
        # Publish to the events or state topic based on the flag.
        sub_topic = 'events' if self.message_type == 'event' else 'state'
        mqtt_topic = '/devices/{}/{}'.format(self.device_id, sub_topic)
        self.client.publish(mqtt_topic, payload, qos=1)




# def mqtt_device_demo(args):
#     global minimum_backoff_time
#     global MAXIMUM_BACKOFF_TIME

#     # Publish to the events or state topic based on the flag.
#     sub_topic = 'events' if args.message_type == 'event' else 'state'

#     mqtt_topic = '/devices/{}/{}'.format(args.device_id, sub_topic)

#     jwt_iat = datetime.datetime.utcnow()
#     jwt_exp_mins = args.jwt_expires_minutes
#     client = get_client(
#         args.project_id, args.cloud_region, args.registry_id,
#         args.device_id, args.private_key_file, args.algorithm,
#         args.ca_certs, args.mqtt_bridge_hostname, args.mqtt_bridge_port)

#     # Publish num_messages messages to the MQTT bridge once per second.
#     for i in range(1, args.num_messages + 1):
#         # Process network events.
#         client.loop()

#         # Wait if backoff is required.
#         if should_backoff:
#             # If backoff time is too large, give up.
#             if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
#                 print('Exceeded maximum backoff time. Giving up.')
#                 break

#             # Otherwise, wait and connect again.
#             delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
#             print('Waiting for {} before reconnecting.'.format(delay))
#             time.sleep(delay)
#             minimum_backoff_time *= 2
#             client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)
#         payload = dict()
#         payload['deviceId'] = args.device_id
#         payload['timestamp'] = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S')
#         payload['temperature'] = random.randint(-5, 20)
#         payload = json.dumps(payload)

#         # payload = '{"deviceId": "{0}", "timestamp": {1}, "temperature": {2}}'.format(
#         #     args.device_id, datetime.datetime.utcnow(), random.randint(-5, 20)
#         # )
#         print('Publishing message {}/{}: \'{}\''.format(
#                 i, args.num_messages, payload))

#         seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
#         if seconds_since_issue > 60 * jwt_exp_mins:
#             print('Refreshing token after {}s'.format(seconds_since_issue))
#             jwt_iat = datetime.datetime.utcnow()
#             client.loop()
#             client.disconnect()
#             client = get_client(
#                 args.project_id, args.cloud_region,
#                 args.registry_id, args.device_id, args.private_key_file,
#                 args.algorithm, args.ca_certs, args.mqtt_bridge_hostname,
#                 args.mqtt_bridge_port)
#         # Publish "payload" to the MQTT topic. qos=1 means at least once
#         # delivery. Cloud IoT Core also supports qos=0 for at most once
#         # delivery.
#         client.publish(mqtt_topic, payload, qos=1)

#         # Send events every second. State should not be updated as often
#         for i in range(0, 60):
#             time.sleep(1)
#             client.loop()





