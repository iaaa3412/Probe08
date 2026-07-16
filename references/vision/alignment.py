import numpy as np

class AlignmentManager:
    def __init__(self):
        self.pixel_to_micron_ratio = 0.5 
        
    def calculate_stage_correction(self, mark_pixel_x, mark_pixel_y, target_center_x, target_center_y):
        diff_x = mark_pixel_x - target_center_x
        diff_y = mark_pixel_y - target_center_y
        micron_x = diff_x * self.pixel_to_micron_ratio
        micron_y = diff_y * self.pixel_to_micron_ratio
        return micron_x, micron_y