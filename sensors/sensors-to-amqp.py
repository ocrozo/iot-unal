#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import time
import datetime
import json
import sys
#Libraries for sensors weather module
import tsl2561
import veml6070
import bme280

#Proton import for AMQP
# Don't forget to install proton
# apt-get install python-qpid-proton
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

class AmqpSender(MessagingHandler):
    def __init__(self, server, address, body):
        super(AmqpSender, self).__init__()
        self.server = server
        self.address = address
        self.body = body

    def on_start(self, event):
        conn = event.container.connect(self.server)
        event.container.create_sender(conn, self.address)

    def on_sendable(self, event):
        event.sender.send(Message(body=self.body))
        event.sender.close()
        event.connection.close()


# get hostname
hostname = open('/etc/hostname').read()



def sendMessage(temp):
        amqpMsgPayload = {}
        amqpMsgPayload["timestamp"] = int((time.time()*1000))
        amqpMsgPayload["id"] = '"'+hostname[:-1]+'"'
        amqpMsgPayload["value"] = temp

        print(json.dumps(amqpMsgPayload))
        # Don't forget to create the queue in ActiveMQ
        Container(AmqpSender("localhost:5672", "temperature", amqpMsgPayload)).run()
        print("Message with temperature sent to AMQP server")


def loop():

    while True:
        veml = veml6070.Veml6070()
        uv_raw = veml.get_uva_light_intensity_raw()
        uv = veml.get_uva_light_intensity()
        print ("UVA Light value : %f W/(m*m) from raw value %d" % (uv, uv_raw))

        temperature,pressure,humidity = bme280.readBME280All()

        print ("Temperature : ", temperature, "C")
        print ("Pressure : ", pressure, "hPa")
        print ("Humidity : ", humidity, "%")

        (light_ch0,light_ch1)= tsl2561.readValues()
        print ("Full Spectrum(IR + Visible) :%d lux" % light_ch0)
        print ("Infrared Value :%d lux" % light_ch1)
        print ("Visible Value :%d lux" % (light_ch0 - light_ch1))	
        sendMessage(temperature)
        time.sleep(10)



if __name__ == '__main__': # Program start from here
    try:
        loop()
    except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
        exit()

