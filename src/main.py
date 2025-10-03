#
# test program for controll Maqueen via MQTT
#
#

#
# Maqueen control messages
#

#  ### Control Maqueen ###
#
#  TOPIC:  "req/maqueen01/control"
#  BODY:
#     GO = {'control' : {'device':'car', 'set' : 'go'}}
#     BACK = {'control' : {'device':'car', 'set' : 'back'}}
#     SPIN_L = {'control' : {'device':'car', 'set' : 'spin_left'}}
#     SPIN_R = {'control' : {'device':'car', 'set' : 'spin_right'}}
#     STOP = {'control' : {'device':'car', 'set' : 'stop'}}


import json
import time
from umqtt.simple import MQTTClient
from mylib import get_uniq_id
from mylib import timestamp

from maqueen import Maqueen
MAQUEEN_SERVO_ADDR = 0x10
maq01 = None

MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

def car_control(set):
   if set == 'go':
      print('car go')
      maq01.go()
   elif set == 'back':
      print('car back')
      maq01.back()
   elif set == 'spin_left':
      print('car spin left')
      maq01.rotate('L')
   elif set == 'spin_right':
      print('car spin right')
      maq01.rotate('R')
   elif set == 'stop':
      print('car stop')
      maq01.stop()

def receive_msg(topic, msg):

    payload = msg
    print('------------------')
    print("Received: ", topic , '   ' , payload)
    topic_str = topic.decode('utf-8')
    payload_str = payload.decode('utf-8')
    payload_dic = json.loads(payload_str)
    print(payload_dic)
    if 'control' in payload_dic:
          if 'device' in payload_dic['control']:
              device =  payload_dic['control']['device']
              set =  payload_dic['control']['set']
              if device == 'car':
                  car_control(set)


def MQTT_connect():

    mqtt_client_id = get_uniq_id('rpi_', length=8)
    client = MQTTClient(mqtt_client_id, MQTT_BROKER, MQTT_PORT)
    client.set_callback(receive_msg)
    client.connect()
    print('subscribe', "req/maqueen01/control")
    client.subscribe("req/maqueen01/control")
    return client


def main():
   global maq01
   client = MQTT_connect()

   i2c = I2C(0, scl=Pin(6), sda=Pin(5), freq=10_000)
   time.sleep(1)
   maq01 = Maqueen(i2c)

   while True:
      print('.')
      client.check_msg()
      time.sleep(1)


main()


#
#
#
