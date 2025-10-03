#!/usr/bin/python3

import datetime
import time
import json
import pdb


#
# MQTT Defs
#
import paho.mqtt.client as mqtt 

#
# EMQX
#
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

GO = json.dumps({'control' : {'device':'car', 'set' : 'go'}})
BACK = json.dumps({'control' : {'device':'car', 'set' : 'back'}})
SPIN_L = json.dumps({'control' : {'device':'car', 'set' : 'spin_left'}})
SPIN_R = json.dumps({'control' : {'device':'car', 'set' : 'spin_right'}})
STOP = json.dumps({'control' : {'device':'car', 'set' : 'stop'}})

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected with result code " + str(reason_code))
    print('subscribe', "rep/maqueen01/report")
    client.subscribe("rep/maqueen01/report")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print("Unexpected disconnection.")

def on_publish(client, userdata, mid, reason_code, properties):
    print('-- on_publish()---')
    reason_code_value = reason_code.value
    print(f"Published message ID: {mid}, reason: {reason_code_value:02x} ({reason_code.getName()})")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload
    print('------------------')
    print("Received: ", topic )
    #print("Received: ", topic , '   ' , payload)


def MQTT_connect():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_publish = on_publish
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    return client


def main():
    client = MQTT_connect()
    while True:
        print('.')
        for msg in (GO, BACK, SPIN_L, SPIN_R):
            print(msg)
            result = client.publish("req/maqueen01/control", msg , qos=0)
            time.sleep(2)
            msg = STOP
            print(msg)
            result = client.publish("req/maqueen01/control", msg , qos=0)
            time.sleep(5)
    
main()
