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
import waitress

# sets the frame rate of the video stream on the web app
IMAGE_FRAME_DELAY = 0.2

app = Flask(__name__)

subscriber = None
bridge = None
frame = None
kill_tag_id = 0
run_tag_id = 1

last_frame_encoded_time = None

def image_callback(image_message):
    global frame, last_frame_encoded_time

    if frame is None or (datetime.datetime.now() - last_frame_encoded_time).total_seconds() >= IMAGE_FRAME_DELAY:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        image = bridge.imgmsg_to_cv2(image_message)
        _, frame = cv2.imencode(".jpeg", image)

        last_frame_encoded_time = datetime.datetime.now()


@app.route('/do_run_program')
def do_run_program():
    pass


@app.route('/do_kill_program')
def do_kill_program():
    pass


@app.route('/')
def index():
    return render_template('index.html')


def get_video_stream_frames():
    while True:
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame.tostring() + b'\r\n')
        time.sleep(IMAGE_FRAME_DELAY)


@app.route('/video_feed')
def video_feed():
    return Response(get_video_stream_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    threading.Thread(target=lambda: rospy.init_node('example_node', disable_signals=True)).start()
    rospy.Subscriber("/cv_camera/image_raw", sensor_msgs.msg.Image, image_callback)
    bridge = cv_bridge.CvBridge()

    waitress.serve(app, host='0.0.0.0', port=12345)
