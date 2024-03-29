# Copyright 2023 The MediaPipe Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Main scripts to run object detection."""

import argparse
import sys
import time
import MDD10A as HBridge

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from utils import visualize

# Global variables to calculate FPS
COUNTER, FPS = 0, 0
START_TIME = time.time()

SPEED_MEDIUM = 0.2
SPEED_SLOW = 0.1

def run(model: str, max_results: int, score_threshold: float, 
        camera_id: int, width: int, height: int) -> None:
    """Continuously run inference on images acquired from the camera.

    Args:
        model: Name of the TFLite object detection model.
        max_results: Max number of detection results.
        score_threshold: The score threshold of detection results.
        camera_id: The camera id to be passed to OpenCV.
        width: The width of the frame captured from the camera.
        height: The height of the frame captured from the camera.
    """

    # Initialize variables
    position = "none"
    object_name = "none"
    object_width = 0
    object_height = 0
    center_x = 0
    adjustment = 0
    count_checkpoint = 1
    count_obstacle = 1

    # Start capturing video input from the camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Visualization parameters
    row_size = 50  # pixels
    left_margin = 24  # pixels
    text_color = (255, 255, 0)  # black
    font_size = 1
    font_thickness = 1
    fps_avg_frame_count = 10

    detection_frame = None
    detection_result_list = []

    # Initialize the PID controller
    pid = PID()


    def save_result(result: vision.ObjectDetectorResult, unused_output_image: mp.Image, timestamp_ms: int):
        global FPS, COUNTER, START_TIME

        # Calculate the FPS
        if COUNTER % fps_avg_frame_count == 0:
            FPS = fps_avg_frame_count / (time.time() - START_TIME)
            START_TIME = time.time()

        detection_result_list.append(result)
        COUNTER += 1

    # Initialize the object detection model
    base_options = python.BaseOptions(model_asset_path=model)
    options = vision.ObjectDetectorOptions(base_options=base_options,
                                            running_mode=vision.RunningMode.LIVE_STREAM,
                                            max_results=max_results, score_threshold=score_threshold,
                                            result_callback=save_result)
    detector = vision.ObjectDetector.create_from_options(options)


    # Continuously capture images from the camera and run inference
    while cap.isOpened():
        success, image = cap.read()
        image=cv2.resize(image,(640,480))
        if not success:
            sys.exit(
                'ERROR: Unable to read from webcam. Please verify your webcam settings.'
            )

        # Define the region of interest (ROI)
        roi_top = int(image.shape[0] * 0.25)  # 10% from the top
        roi_bottom = int(image.shape[0] * 0.75)  # 10% from the bottom
        roi_left = int(image.shape[1] * 0.25)  # 10% from the left
        roi_right = int(image.shape[1] * 0.75)  # 10% from the right

        # Crop the image
        image = image[roi_top:roi_bottom, roi_left:roi_right]

        # Resize the cropped image back to the original size
        image = cv2.resize(image, (width, height))

        #image = cv2.flip(image, 1)

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # Run object detection using the model.
        detector.detect_async(mp_image, time.time_ns() // 1_000_000)

        # Show the FPS
        fps_text = 'FPS = {:.1f}'.format(FPS)
        text_location = (left_margin, row_size)
        current_frame = image
        cv2.putText(current_frame, fps_text, text_location, cv2.FONT_HERSHEY_DUPLEX,
                    font_size, text_color, font_thickness, cv2.LINE_AA)
        
        # Set the setpoint to the center of the image
        pid.setSetPoint(image.shape[1] / 2)
        
        if detection_result_list:
            current_frame, position, object_name, object_width, object_height, center_x = visualize(current_frame, detection_result_list[0])
            detection_frame = current_frame

            if not detection_result_list[0].detections:
                position = "none"
                object_name = "none"
                HBridge.setMotorLeft(0.05)  
                HBridge.setMotorRight(-0.05)
            else:
                pid.update(center_x)  # Update the PID controller with the current position
                adjustment = pid.output / 1000  # Get the adjustment from the PID controller
                #print(adjustment)

                # If object detected
                if object_name == "obstacles":
                    # Adjust motor speeds
                    HBridge.setMotorLeft(SPEED_MEDIUM - adjustment)
                    HBridge.setMotorRight(SPEED_MEDIUM + adjustment)
                
                    # If obstacle is reached
                    if (object_width > 500):
                        print(f"Obstacle {count_obstacle} reached")

                        if count_obstacle == 1:
                            turnRightLeft()
                        elif count_obstacle == 2:
                            turnLeftRight()
                        elif count_obstacle == 3:
                            turnRightLeft()
                        elif count_obstacle == 4:
                            turnLeftRight()
                        count_obstacle += 1

                # If checkpoint detected
                if object_name == "checkpoint":
                    # Adjust motor speeds
                    HBridge.setMotorLeft(SPEED_MEDIUM - adjustment)
                    HBridge.setMotorRight(SPEED_MEDIUM + adjustment)

                    # If checkpoint is reached
                    if (object_width > 250):
                        print(f"Checkpoint {count_checkpoint} reached")
                        if count_checkpoint == 1:
                            turnLeft()
                        elif count_checkpoint == 2:
                            uturn()
                        elif count_checkpoint == 3:
                            turnRight()
                        elif count_checkpoint == 4:
                            print("Finish")
                            break
                        HBridge.setMotorLeft(0)
                        HBridge.setMotorRight(SPEED_SLOW)
                        time.sleep(2)
                        count_checkpoint += 1

            speedleft, speedright = HBridge.getMotorPowers()
            print("adjust: " + str(adjustment) + ", left: " + str(speedleft) + ", right: " + str(speedright) + ", pos: " + position + ", object: " + object_name + ", width: " + str(object_width) + ", height: " + str(object_height))

            detection_result_list.clear()

        if detection_frame is not None:
            cv2.imshow('object_detection', detection_frame)

        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
            break

    detector.close()
    cap.release()
    cv2.destroyAllWindows()


class PID:
    def __init__(self, P=0.25, I=0, D=0):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.sample_time = 0.00
        self.current_time = time.time()
        self.last_time = self.current_time
        self.clear()

    def clear(self):
        self.SetPoint = 0.0
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0

    def update(self, feedback_value):
        error = self.SetPoint - feedback_value
        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        if (delta_time >= self.sample_time):
            self.PTerm = self.Kp * error
            self.ITerm += error * delta_time

            if (delta_time > 0):
                self.DTerm = delta_error / delta_time

            self.last_time = self.current_time
            self.last_error = error

            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)

    def setKp(self, proportional_gain):
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        self.Kd = derivative_gain

    def setSetPoint(self, set_point):
        self.SetPoint = set_point

    def setSampleTime(self, sample_time):
        self.sample_time = sample_time


def turnRight():
    print("Turn right")
    HBridge.setMotorLeft(SPEED_SLOW)
    HBridge.setMotorRight(-SPEED_SLOW)
    time.sleep(2)


def turnLeft():
    print("Turn left")
    HBridge.setMotorLeft(-SPEED_SLOW)
    HBridge.setMotorRight(SPEED_SLOW)
    time.sleep(2)


def turnRightLeft():
    print("Turn right")
    HBridge.setMotorLeft(SPEED_MEDIUM)
    HBridge.setMotorRight(SPEED_SLOW)
    time.sleep(2)
    print("Turn left")
    HBridge.setMotorLeft(SPEED_SLOW)
    HBridge.setMotorRight(SPEED_MEDIUM)
    time.sleep(2)


def turnLeftRight():
    print("Turn left")
    HBridge.setMotorLeft(SPEED_SLOW)
    HBridge.setMotorRight(SPEED_MEDIUM)
    time.sleep(2)
    print("Turn right")
    HBridge.setMotorLeft(SPEED_MEDIUM)
    HBridge.setMotorRight(SPEED_SLOW)
    time.sleep(2)


def uturn():
    print("Turn 180 degree")
    HBridge.setMotorLeft(-SPEED_SLOW)
    HBridge.setMotorRight(SPEED_SLOW)
    time.sleep(5)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--model',
        help='Path of the object detection model.',
        required=False,
    #      default='efficientdet_lite0.tflite')
        default='best.tflite')
    parser.add_argument(
        '--maxResults',
        help='Max number of detection results.',
        required=False,
        default=1)
    parser.add_argument(
        '--scoreThreshold',
        help='The score threshold of detection results.',
        required=False,
        type=float,
        default=0.80)
    # Finding the camera ID can be very reliant on platform-dependent methods. 
    # One common approach is to use the fact that camera IDs are usually indexed sequentially by the OS, starting from 0. 
    # Here, we use OpenCV and create a VideoCapture object for each potential ID with 'cap = cv2.VideoCapture(i)'.
    # If 'cap' is None or not 'cap.isOpened()', it indicates the camera ID is not available.
    parser.add_argument(
        '--cameraId', help='Id of camera.', required=False, type=int, default=0)
    parser.add_argument(
        '--frameWidth',
        help='Width of frame to capture from camera.',
        required=False,
        type=int,
        default=640)
    parser.add_argument(
        '--frameHeight',
        help='Height of frame to capture from camera.',
        required=False,
        type=int,
        default=480)
    args = parser.parse_args()

    run(args.model, int(args.maxResults),
        args.scoreThreshold, int(args.cameraId), args.frameWidth, args.frameHeight)


if __name__ == '__main__':
    main()
