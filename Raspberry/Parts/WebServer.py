#Imports
from Parts import CarCamera,Utils
from Parts.CarCamera import CameraStream
from tornado.ioloop import PeriodicCallback
import tornado.websocket
import tornado.web
import webbrowser
import threading
import hashlib
import base64
import time
import io
import os

class LocalServer(tornado.web.Application):
    def __init__(self,params,_car):
        Utils.print_log("Init. server",1)
        self.cookie = params['cookie']
        self.port = params['port']
        self.car = _car

        self.camera = self.car.camera.picam
        root = Utils.get_root()
        path = os.path.join(root, '../pi')

        self.handlers = [
            (r"/", IndexHandler),
            (r"/websocket", WebSocket),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'})
        ]

    def stream(self):
       super(LocalServer,self).__init__(self.handlers)

       #Start camera stream
       CameraStream(self.car)

       self.listen(self.port)
       tornado.ioloop.IOLoop.instance().start()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("../server/index.html", port=self.application.port, mode=self.application.car.train_mode)

class ErrorHandler(tornado.web.RequestHandler):
    def get(self):
        self.send_error(status_code=403)

class WebSocket(tornado.websocket.WebSocketHandler):
    def on_message(self, message):
        # Start an infinite loop when this is called
        if message == "read_camera":
            self.camera_loop = PeriodicCallback(self.loop, 100) # 10 fps
            self.camera_loop.start()
        # Movement message
        elif (message in ["BACKWARDS","FORWARD","LEFT","RIGHT"]):
            direction = [message]
            if (message in ["LEFT","RIGHT"]):
                print("we are going left/right")
                direction = [message,'FORWARD']
                print(direction)

            if(self.application.car.train_mode):
                print("we are in train mode")
                self.application.car.log_and_move(direction)
            else:
                print("Drive mode")
                self.application.car.move(direction)

        # Stop message
        elif (message[5:] in ["BACKWARDS","FORWARD","LEFT","RIGHT"]):
            self.application.car.stop()

        elif (message == 'self_drive'):
            Utils.print_log("\nDrive, "+ self.application.car.name +"!!!",1)
            self.application.car.drive = True
            self.application.car.self_drive()

        elif (message == 'manual'):
            Utils.print_log("Manual drive",1)
            self.application.car.drive = False

        elif (message == 'save_frames'):
            Utils.print_log("Saving frames",1)
            self.application.car.train_data.save()
            self.application.car.drive = False


        else:
            Utils.print_log("Unsupported function: " + message,1)

    def loop(self):
       	#Sends images in infinite loop
        try:
            self.write_message(base64.b64encode(self.application.car.camera.last_img_bytes))
        except tornado.websocket.WebSocketClosedError:
            self.camera_loop.stop()
