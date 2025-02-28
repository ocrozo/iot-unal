# Program to control passerelle between Android application
# and micro-controller through USB tty
import time
import argparse
import signal
import sys
import datetime 
import io
import os
import httplib2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import threading 
import tsl2561
import RPi.GPIO as GPIO

# CSE params
host = "192.168.2.1" # Computer IP address
httpPort = 8080

# AE params
aeIP = "192.168.2.7" #Raspberry IP address
aePort   = "80"
origin   = "Cae_device1"

KEEP_RUNNING = True

def keepRunning():
    return KEEP_RUNNING


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        # self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        # self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        self._set_headers()
        # self.wfile.write("<html><body><h1>POST!</h1></body></html>")
        content_len = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_len)
        self.end_headers()
        if "ON" in post_body:
                print "LED on"
                GPIO.output(4,GPIO.HIGH)
        else:
                print "LED off"
                GPIO.output(4,GPIO.LOW)
        data = json.loads(post_body)

        self.wfile.write(data['foo'])
        return
        
def runWebServer(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    while KEEP_RUNNING:
        #httpd.serve_forever()
        httpd.handle_request()

def push_data(luxURL):

    while True:
        # Read luminosity values
        
        (light_ch0,light_ch1)= tsl2561.readValues()
        print ("Full Spectrum(IR + Visible) :%d lux" % light_ch0)
        data = "{\"m2m:cin\":{\"con\":\"" + str(light_ch0) + "\"}}"
        send(luxURL,4,data)
        time.sleep(5)


# Set output mode for GPIO 4 to OUT
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(4,GPIO.OUT)

def setup_ae():
    # Create AE resource
    resultDevice = send("/server",2,"{\"m2m:ae\":{\"rn\":\"mydevice1\",\"api\":\"mydevice1.company.com\",\"rr\":\"true\",\"poa\":[\"http://"+aeIP+":"+aePort+"\"]}}")
    resp_lux=""  
    if resultDevice["status"]=="201":
        # Create Container resource
        resp_lux = send(resultDevice["content-location"],3,"{\"m2m:cnt\":{\"rn\":\"luminosity\"}}")
        
        #Create ContentInstance resource
        send(resp_lux["content-location"],4,"{\"m2m:cin\":{\"con\":\"0\"}}")

        # Create Container resource
        resp_led = send(resultDevice["content-location"],3,"{\"m2m:cnt\":{\"rn\":\"led\"}}")

        # Create ContentInstance resource
        resp_ledstate = send(resp_led["content-location"],4,"{\"m2m:cin\":{\"con\":\"OFF\"}}")

        # Create Subscription resource
        resp_suscription = send(resp_led["content-location"],23,"{\"m2m:sub\":{\"rn\":\"led_sub\",\"nu\":[\"Cae_device1\"],\"nct\":1}}")
    return resp_lux["content-location"]

# Method in charge of sending request to the CSE
def send(url, ty, rep):

    heads = {"Host":host,
        "X-M2M-Origin":origin,
        "Content-Type": "application/json;ty="+str(ty)}
    
    h = httplib2.Http(".cache")
    (resp, content) = h.request("http://" + host + ":" + str(httpPort) + "/~" + url, "POST", headers=heads, body=rep)
    print(resp)
    return resp


# Main program logic follows:
if __name__ == '__main__':
    # Setup pins
    setup_gpio()

    # Start web server
    thread= threading.Thread(target=runWebServer)
    thread.start()

    # Setup AE ressources
    luxURL = setup_ae()
    if luxURL == "":
        print("Error while creating ressources")
        exit()
    print ('Press Ctrl-C to quit.')
    try:
        push_data(luxURL)
    except (KeyboardInterrupt, SystemExit):
        KEEP_RUNNING=False
        thread.kill_received=True                 
        # os._exit(1)
        exit()
