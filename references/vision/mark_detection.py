import cv2
import numpy as np

class MarkDetector:
    def __init__(self, template_path):
        self.template = cv2.imread(template_path, 0)
        
    def find_mark(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        res = cv2.matchTemplate(gray_frame, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        mark_w, mark_h = self.template.shape[::-1]
        center_x = max_loc[0] + mark_w // 2
        center_y = max_loc[1] + mark_h // 2
        return (center_x, center_y), max_val

    def draw_debug(self, frame, location):
        cv2.circle(frame, location, 10, (0, 255, 0), 2)
        return frame