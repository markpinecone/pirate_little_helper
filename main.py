import pygetwindow as gw
import pyautogui
import numpy as np
import cv2
import winsound
import time
import keyboard


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
        self.last_alert_times = {color: 0 for color in colors_dict.keys()}
        self.last_blue_pixel_counts = []
        self.alerting = Alerting()
        self.last_alert_times['rg'] = 0

    def _get_window_screenshot(self):
        try:
            window = gw.getWindowsWithTitle(self.window_title)[0]
            left, top, width, height = window.left, window.top, window.width, window.height
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            return np.array(screenshot)
        except IndexError:
            # Handle the case when the window is not found
            print("Window not found. Skipping current iteration.")
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
            return False  # Return False if the list is empty
        mean_blue_count = np.mean(self.last_blue_pixel_counts)
        threshold_percentage = 0.02  # 1% threshold for change
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
        image = self._get_window_screenshot()
        pixel_counts = self._get_pixel_counts(image)

        # Store the current blue pixel count
        self.last_blue_pixel_counts.append(pixel_counts['blue'])
        if len(self.last_blue_pixel_counts) > 3:
            self.last_blue_pixel_counts.pop(0)  # Ensure only the last 3 counts are stored

        # Check for blue alert
        if self._check_blue_alert_condition(pixel_counts['blue']):
            self.alerting.play_blue_alert()
            self.last_alert_times['blue'] = time.time()

        # Check for red or green alert
        if self._check_rg_alert_condition(pixel_counts):
            self.alerting.play_rg_alert()
            self.last_alert_times['rg'] = time.time()

        del image
        return pixel_counts


class Application:
    def __init__(self, detector, delay_seconds=2):
        self.detector = detector
        self.delay_seconds = delay_seconds
        self.paused = False

    def toggle_pause(self):
        self.paused = not self.paused
        print("Paused" if self.paused else "Resumed")

    def run(self):
        keyboard.add_hotkey('win+shift+x', self.toggle_pause)
        while True:
            if not self.paused:
                image = self.detector._get_window_screenshot()
                if image is not None:
                    pixel_counts = self.detector._get_pixel_counts(image)
                    print("Pixel counts for each color:", pixel_counts)
                    del image
            time.sleep(self.delay_seconds)

window_title = 'Entropia Universe Client (64 bit) [Space]'
colors = {
    'blue': (1, 1, 192),
    'red': (175, 1, 1),
    'green': (0, 191, 1)
}
detector = ColorDetector(window_title, colors)
app = Application(detector)
app.run()
