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

def create_jwt(project_id, private_key_file, algorithm):
    token = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=20),
        'aud': project_id
    }

    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(
            algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    print('on_connect', mqtt.connack_string(rc))
    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1


def on_disconnect(unused_client, unused_userdata, rc):
    print('on_disconnect', error_str(rc))
    global should_backoff
    should_backoff = True


def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')


def on_message(unused_client, unused_userdata, message):
    payload = str(message.payload.decode('utf-8'))
    print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))


def get_client(
        project_id, cloud_region, registry_id, device_id, private_key_file,
        algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port):
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
            project_id, cloud_region, registry_id, device_id)
    print('Device client_id is \'{}\''.format(client_id))

    client = mqtt.Client(client_id=client_id)

    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    project_id, private_key_file, algorithm))

    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    client.subscribe(mqtt_config_topic, qos=1)

    mqtt_command_topic = '/devices/{}/commands/#'.format(device_id)

    print('Subscribing to {}'.format(mqtt_command_topic))
    client.subscribe(mqtt_command_topic, qos=0)

    return client


def detach_device(client, device_id):
    detach_topic = '/devices/{}/detach'.format(device_id)
    print('Detaching: {}'.format(detach_topic))
    client.publish(detach_topic, '{}', qos=1)



def attach_device(client, device_id, auth):
    attach_topic = '/devices/{}/attach'.format(device_id)
    attach_payload = '{{"authorization" : "{}"}}'.format(auth)
    client.publish(attach_topic, attach_payload, qos=1)


def listen_for_messages(
        service_account_json, project_id, cloud_region, registry_id, device_id,
        gateway_id, num_messages, private_key_file, algorithm, ca_certs,
        mqtt_bridge_hostname, mqtt_bridge_port, jwt_expires_minutes, duration,
        cb=None):

    global minimum_backoff_time

    jwt_iat = datetime.datetime.utcnow()
    jwt_exp_mins = jwt_expires_minutes
    client = get_client(
        project_id, cloud_region, registry_id, gateway_id,
        private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
        mqtt_bridge_port)

    attach_device(client, device_id, '')
    print('Waiting for device to attach.')
    time.sleep(5)

    device_config_topic = '/devices/{}/config'.format(device_id)
    client.subscribe(device_config_topic, qos=1)

    gateway_config_topic = '/devices/{}/config'.format(gateway_id)
    client.subscribe(gateway_config_topic, qos=1)

    error_topic = '/devices/{}/errors'.format(gateway_id)
    client.subscribe(error_topic, qos=0)

    for i in range(1, duration):
        client.loop()
        if cb is not None:
            cb(client)

        if should_backoff:
            # If backoff time is too large, give up.
            if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                print('Exceeded maximum backoff time. Giving up.')
                break

            delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
            time.sleep(delay)
            minimum_backoff_time *= 2
            client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

        seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
        if seconds_since_issue > 60 * jwt_exp_mins:
            print('Refreshing token after {}s'.format(seconds_since_issue))
            jwt_iat = datetime.datetime.utcnow()
            client.loop()
            client.disconnect()
            client = get_client(
                project_id, cloud_region, registry_id, gateway_id,
                private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
                mqtt_bridge_port)

        time.sleep(1)

    detach_device(client, device_id)

    print('Finished.')


def send_data_from_bound_device(
        service_account_json, project_id, cloud_region, registry_id, device_id,
        gateway_id, num_messages, private_key_file, algorithm, ca_certs,
        mqtt_bridge_hostname, mqtt_bridge_port, jwt_expires_minutes, payload):
    global minimum_backoff_time

    # Publish device events and gateway state.
    device_topic = '/devices/{}/{}'.format(device_id, 'state')
    gateway_topic = '/devices/{}/{}'.format(gateway_id, 'state')

    jwt_iat = datetime.datetime.utcnow()
    jwt_exp_mins = jwt_expires_minutes
    # Use gateway to connect to server
    client = get_client(
        project_id, cloud_region, registry_id, gateway_id,
        private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
        mqtt_bridge_port)

    attach_device(client, device_id, '')
    print('Waiting for device to attach.')
    time.sleep(5)

    # Publish state to gateway topic
    gateway_state = 'Starting gateway at: {}'.format(time.time())
    print(gateway_state)
    client.publish(gateway_topic, gateway_state, qos=1)

    # Publish num_messages messages to the MQTT bridge
    for i in range(1, num_messages + 1):
        client.loop()

        if should_backoff:
            # If backoff time is too large, give up.
            if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                print('Exceeded maximum backoff time. Giving up.')
                break

            delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
            time.sleep(delay)
            minimum_backoff_time *= 2
            client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

        # payload = f'{"deviceId": {device_id}, "timestamp": {datetime.datetime.utcnow()}, "temperature": {random.randint(-5,20)}}'

        print('Publishing message {}/{}: \'{}\' to {}'.format(
                i, num_messages, payload, device_topic))
        client.publish(
                device_topic, '{} : {}'.format(device_id, payload), qos=1)

        seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
        if seconds_since_issue > 60 * jwt_exp_mins:
            print('Refreshing token after {}s').format(seconds_since_issue)
            jwt_iat = datetime.datetime.utcnow()
            client = get_client(
                project_id, cloud_region, registry_id, gateway_id,
                private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
                mqtt_bridge_port)

        time.sleep(5)

    detach_device(client, device_id)

    print('Finished.')


def parse_command_line_args():

    algorithm = 'RS256', 'ES256'
    ca_certs='roots.pem'
    cloud_regiont='us-central1'
    device_id='device-id'
    gateway_id =''
    jwt_expires_minutes=20
    message_type=('event', 'state')
    mqtt_bridge_hostname='mqtt.googleapis.com'
    mqtt_bridge_port=(8883, 443)
    private_key_file=''
    project_id=''
    registry_id=''



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





