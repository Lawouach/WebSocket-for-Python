# -*- coding: utf-8 -*-
__doc__ = """
WebSocket client that pushes Android sensor metrics to the
websocket server it is connected to.

In order to set this up:

 1. Install SL4A http://code.google.com/p/android-scripting/
 2. Install the Python package for SL4A
 3. Build ws4py and copy the package built into a directory
    called com.googlecode.pythonforandroid/extras/python on
    your Android device.
 4. a. Either copy the droid_sensor.py module into the directory
       called sl4a/scripts on your Android device.
    b. Or set up the remote control so that you can run the
       module from your computer directly on your device:
       http://code.google.com/p/android-scripting/wiki/RemoteControl
 5. Setup the device so that it has an IP address on the same
    network as the computer running the server.
    
Run the example:

 1. Start the echo_cherrypy_server module:
    $ python example/droid_sensor_cherrypy_server.py
 2. From a local browser, go to:
    http://localhost:9000/
 3. Edit the droid_sensor module to set the appropriate
    IP address where your server is running.
 4. Run the droid_sensor module (from the device or
    your computer depending on your setup):
    $ python example/droid_sensor.py
 5. If your device isn't idled, just move ir around
    for the metrics to be sent to the server which
    will dispatch them to the browser's client.
 6. Profit???
 
"""
import time
import math

import android
from ws4py.client.threadedclient import WebSocketClient

class AirPongSensor(object):
    def __init__(self, host):
        self.droid = android.Android()
        #self.droid.startSensingThreshold(1, 0, 7)
        #self.droid.startSensingThreshold(2, 1, 2)
        self.droid.startSensingTimed(1, 100)

        self.running = False

        self.client = AirPongWebSocketClient(host)
        self.client.connect()
        
    def run(self):
        try:
            self.running = True
            last = [None, None, None]
            while self.running:
                azimuth, pitch, roll = self.droid.sensorsReadOrientation().result
                accel = x, y, z = self.droid.sensorsReadAccelerometer().result
                if azimuth is None:
                    continue
                
                c = lambda rad: rad * 360.0 / math.pi
                print c(azimuth), c(pitch), c(roll), x, y, z

                if self.client.terminated:
                    break

                if accel != [None, None, None] and accel != last:
                    last = accel
                    self.client.send("%s %s %s %s %s %s" % (c(azimuth), c(pitch), c(roll), x, y, z))

                time.sleep(0.15)
        finally:
            self.terminate()
            
    def terminate(self):
        if not self.droid:
            return
        
        self.running = False
        self.droid.stopSensing()
        self.droid = None
        
        if not self.client.terminated:
            self.client.close()
            self.client._th.join()
            self.client = None
        
class AirPongWebSocketClient(WebSocketClient):
        def received_message(self, m):
            pass

if __name__ == '__main__':
    aps = AirPongSensor(host='http://192.168.0.10:9000/ws')
    try:
        aps.run()
    except KeyboardInterrupt:
        aps.terminate()
