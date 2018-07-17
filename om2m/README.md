# onem2m-demo
oneM2M demonstration

## Raspberry configuration
You will connect the weather sensor as configured before and you will connect a LED to GPIO 4 with a resistor connected to a GND pin.
Test your connections with the code `demo.1.py`in the sensors folder.

### Install additional packages
To connect to om2m you need a http client library: 
```
sudo apt-get install python-httplib2
```

## Launch the script
Edit the file `onem2m-rasp.py to set the correct IP address corresponding to your configuration.
```
sudo python onem2m-rasp.py
```