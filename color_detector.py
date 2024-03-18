from PIL import ImageGrab
import numpy as np
import cv2
import time
import winsound
from win32 import win32gui

class Alerting:
    def __init__(self):
        pass

    def play_blue_alert(self):
        winsound.PlaySound("C:\\Windows\\Media\\Windows Message Nudge.wav", winsound.SND_FILENAME)

    def play_rg_alert(self):
        winsound.PlaySound("C:\\Windows\\Media\\tada.wav", winsound.SND_FILENAME)

class ColorDetector:
    def __init__(self, window_title, colors_dict, tolerance=0.02, avg_window=5):
        self.window_title = window_title
        self.colors_dict = colors_dict
        self.tolerance = tolerance
        self.avg_window = avg_window
        self.alerting = Alerting()
        self.last_alert_times = {color: 0 for color in colors_dict.keys()}
        self.last_alert_times['rg'] = 0
        self.last_blue_pixel_counts = []
        self.started = False

    def _get_window_screenshot(self):
        try:
            hwnd = win32gui.FindWindow(None, self.window_title)
            if hwnd == 0:
                print("Window with title '{}' not found.".format(self.window_title))
                return None
            dimensions = win32gui.GetWindowRect(hwnd)
            screenshot = ImageGrab.grab(dimensions)
            return np.array(screenshot)
        except Exception as e:
            print("Error occurred while retrieving window screenshot:", e)
            return None

    def _get_pixel_counts(self, image):
        pixel_counts = {}
        for color_name, color_rgb in self.colors_dict.items():
            tolerance_rgb = tuple(int(255 * self.tolerance) for _ in range(3))
            lower_bound = np.subtract(color_rgb, tolerance_rgb)
            upper_bound = np.add(color_rgb, tolerance_rgb)
            mask = cv2.inRange(image, lower_bound, upper_bound)
            pixel_counts[color_name] = np.count_nonzero(mask)
        return pixel_counts

    def _check_blue_alert_condition(self, pixel_count_threshold):
        current_time = time.time()
        if not self.last_blue_pixel_counts:
            return False
        mean_blue_count = np.mean(self.last_blue_pixel_counts)
        threshold_percentage = 0.02
        change_threshold = mean_blue_count * threshold_percentage
        return (current_time - self.last_alert_times['blue'] >= 30 and 
                pixel_count_threshold > 2 and 
                abs(pixel_count_threshold - mean_blue_count) > change_threshold)

    def _check_rg_alert_condition(self, pixel_counts):
        current_time = time.time()
        rg_pixel_count = sum(pixel_counts[color] for color in ['red', 'green'])
        return (current_time - self.last_alert_times['rg'] >= 30 and 
                rg_pixel_count > 2)

    def detect_and_alert(self):
        if not self.started:
            self.started = True
            print("Detection started")
            return None
        else:
            image = self._get_window_screenshot()
            if image is None:
                return None
            pixel_counts = self._get_pixel_counts(image)
            self.last_blue_pixel_counts.append(pixel_counts.get('blue', 0))
            if len(self.last_blue_pixel_counts) > 3:
                self.last_blue_pixel_counts.pop(0)
            if self._check_blue_alert_condition(pixel_counts.get('blue', 0)):
                self.alerting.play_blue_alert()
                self.last_alert_times['blue'] = time.time()
            if self._check_rg_alert_condition(pixel_counts):
                self.alerting.play_rg_alert()
                self.last_alert_times['rg'] = time.time()
            return pixel_counts