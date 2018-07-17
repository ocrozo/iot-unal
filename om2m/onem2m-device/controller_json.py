# Program to control passerelle between Android application
# and micro-controller through USB tty
import time
import argparse
import signal
import sys
import serial
import simplejson as json
import datetime 
import io
import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import threading 

FILENAME        = "/home/pi/values.json"
VALUES          = json.loads('{"values": []}')
MAX_FILE_LEN         = 45000

# send serial message 
SERIALPORT = "/dev/ttyUSB0"
BAUDRATE = 115200
ser = serial.Serial()

KEEP_RUNNING = True

def keepRunning():
    return KEEP_RUNNING

def initUART():        
        # ser = serial.Serial(SERIALPORT, BAUDRATE)
        ser.port=SERIALPORT
        ser.baudrate=BAUDRATE
        ser.bytesize = serial.EIGHTBITS #number of bits per bytes
        ser.parity = serial.PARITY_NONE #set parity check: no parity
        ser.stopbits = serial.STOPBITS_ONE #number of stop bits
        ser.timeout = None          #block read

        # ser.timeout = 0             #non-block read
        # ser.timeout = 2              #timeout block read
        ser.xonxoff = False     #disable software flow control
        ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
        #ser.writeTimeout = 0     #timeout for write
        print 'Starting Up Serial Monitor'
        try:
                ser.open()
        except serial.SerialException:
                print("Serial {} port not available".format(SERIALPORT))
                exit()

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        #self.wfile.write("<html><body><h1>hi!</h1></body></html>")
        saveJSON()
        with open(FILENAME) as data_file:
                self.wfile.write(data_file.read())
    
    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
        
def runWebServer(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    while KEEP_RUNNING:
        #httpd.serve_forever()
        httpd.handle_request()
def startupCheck():
    if os.path.isfile(FILENAME):
        print ("File exists and is readable")
    else:
        print ("File is missing, creating file...")
        with open(FILENAME, 'w') as db_file:
                db_file.write(json.dumps(VALUES))
                db_file.close()

def saveJSON():
        with open(FILENAME, 'w') as fout:
                        json.dump(VALUES, fout)
                        print("Saved " + str(len(VALUES["values"])) + "entries in json file.")
                        fout.close()

# Main program logic follows:
if __name__ == '__main__':
        initUART()
        startupCheck()
        thread= threading.Thread(target=runWebServer)
        thread.start()
        #f= open(FILENAME,"a")
        with open(FILENAME, 'r') as fin:
                VALUES = json.load(fin)
                fin.close()

        
        print ('Press Ctrl-C to quit.')
        try:
                while ser.isOpen() : 
                        # time.sleep(100)
                        if (ser.inWaiting() > 0): # if incoming bytes are waiting 
                                data_str = ser.readline().strip().strip('\x00').strip() 
                                # print(repr(data_str))
				json_data = json.loads(data_str)
                                json_data["date"] = unicode(datetime.datetime.now())
                                jstr = json.dumps(json_data, indent=4)
                                VALUES["values"].append(json_data)
                                if len(VALUES["values"]) > MAX_FILE_LEN :
                                        VALUES["values"].pop(0)
                                # f.write(jstr)
                                print(jstr)
        except (KeyboardInterrupt, SystemExit):
                saveJSON()
                ser.close()
                KEEP_RUNNING=False
                thread.kill_received=True                 
                # os._exit(1)
                exit()
