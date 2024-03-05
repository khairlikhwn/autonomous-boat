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

import cv2
import numpy as np
import MDD10A as HBridge


MARGIN = 5  # pixels
ROW_SIZE = 30  # pixels
FONT_SIZE = 0.7
FONT_THICKNESS = 1
TEXT_COLOR = (0, 0, 0)  # black


def visualize(
    image,
    detection_result
) -> np.ndarray:
  """Draws bounding boxes on the input image and return it.
  Args:
    image: The input RGB image.
    detection_result: The list of all "Detection" entities to be visualized.
  Returns:
    Image with bounding boxes.
  """
  # Draw position boundary lines
  boundary_line1_start = (image.shape[1] // 3, 0)
  boundary_line1_end = (image.shape[1] // 3, image.shape[0])
  cv2.line(image, boundary_line1_start, boundary_line1_end, (255, 0, 0), 2)  

  boundary_line2_start = (2 * image.shape[1] // 3, 0)
  boundary_line2_end = (2 * image.shape[1] // 3, image.shape[0])
  cv2.line(image, boundary_line2_start, boundary_line2_end, (255, 0, 0), 2)  
  
  for detection in detection_result.detections:
    # Draw bounding_box
    bbox = detection.bounding_box
    start_point = bbox.origin_x, bbox.origin_y
    end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
    # Use the orange color for high visibility.
    cv2.rectangle(image, start_point, end_point, (10, 255, 0), 2)
    
    # Calculate center of bounding box
    center_x = (start_point[0] + end_point[0]) / 2
        
    # Draw center_x line
    center_line_start = (int(center_x), start_point[1])
    center_line_end = (int(center_x), end_point[1])
    cv2.line(image, center_line_start, center_line_end, (10, 255, 0), 2)  # red line
    
    # Determine position
    if center_x < image.shape[1] / 3:
        position = "left"
    elif center_x < 2 * image.shape[1] / 3:
        position = "middle"
    else:
        position = "right"
    
    # Draw label and score
    category = detection.categories[0]
    category_name = category.category_name
    probability = round(category.score, 2)
    result_text = category_name + ': ' + str(probability) + '% ' + '(' + position + ')'

    # Calculate text size
    (text_width, text_height), _ = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, FONT_THICKNESS)

    # Calculate text location (above the bounding box)
    text_location = (bbox.origin_x, bbox.origin_y - MARGIN)

    # Draw a white rectangle behind the text
    rectangle_bgr = (255, 255, 255)  # white
    rectangle_start_point = (bbox.origin_x - 0, bbox.origin_y - text_height - 2 * MARGIN)
    rectangle_end_point = (bbox.origin_x + text_width + 0, bbox.origin_y)
    cv2.rectangle(image, rectangle_start_point, rectangle_end_point, rectangle_bgr, -1)

    # Draw the text
    cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_DUPLEX,
                FONT_SIZE, TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)
    
    # Determine position and adjust motor speed
    if position == "left":
        HBridge.setMotorLeft(0.1)  # slow down left motor, full speed right motor
        HBridge.setMotorRight(0.3)
    elif position == "middle":
        HBridge.setMotorLeft(0.3)  # full speed both motors
        HBridge.setMotorRight(0.3)
    else:  # position == "
        HBridge.setMotorLeft(0.3)  # full speed left motor, slow down right motor
        HBridge.setMotorRight(0.1)
        
    speedleft, speedright = HBridge.getMotorPowers()
    print("left motor: " + str(speedleft) + ", right motor: " + str(speedright) + ", pos: " + position)

  return image

