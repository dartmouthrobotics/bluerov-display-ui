#!/usr/bin/python2
from flask import Flask, render_template, Response
import rospy
import threading
import datetime
import sensor_msgs.msg
import cv_bridge
import time
import cv2
import threading

app = Flask(__name__)

current_frame = None
subscriber = None
bridge = None
frame = None


frame_lock = threading.Lock()

IMAGE_FRAME_DELAY = 0.2


def image_callback(image_message):
    global frame

    image = bridge.imgmsg_to_cv2(image_message)
    _, frame = cv2.imencode(".jpeg", image)


@app.route('/')
def index():
    return render_template('index.html')


def gen():
    while True:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame.tostring() + b'\r\n')
        time.sleep(IMAGE_FRAME_DELAY)


@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    threading.Thread(target=lambda: rospy.init_node('example_node', disable_signals=True)).start()
    rospy.Subscriber("/cv_camera/image_raw", sensor_msgs.msg.Image, image_callback)
    bridge = cv_bridge.CvBridge()

    app.run(host='127.0.0.1', port=12345, debug=True)
