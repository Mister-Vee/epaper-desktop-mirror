from PIL import Image, ImageChops, ImageOps
from mss import mss
from IT8951 import constants
from IT8951.display import AutoEPDDisplay
import time
import numpy as np
import os
import sys

os.nice(10)

def get_difference_bbox(img1, img2, threshold=5):
    """Get the bounding box of the difference between two images using numpy."""
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    diff = np.abs(arr1 - arr2)
    diff_sum = np.sum(diff, axis=2)
    changed = diff_sum > threshold
    rows, cols = np.where(changed)
    if len(rows) == 0:
        return None
    top, left, bottom, right = min(rows), min(cols), max(rows), max(cols)
    return (left, top, right, bottom)

def convert_to_4bit_grayscale(image):
    """Convert an image to 4-bit grayscale."""
    return ImageOps.grayscale(image).point(lambda x: x * 16 // 256 * 16)

def main():
    # Initialize the EPD display
    display = AutoEPDDisplay(vcom=-1.42, spi_hz=80000000)
    epd_width, epd_height = display.width, display.height

    prev_image = None
    sleep_duration = 0.1  # Initial sleep duration

    while True:
        # Capture the screen
        with mss() as sct:
            monitor = sct.monitors[0]
            screenshot = sct.grab(monitor)
            image = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
            image_4bit = convert_to_4bit_grayscale(image)
            image_resized = image_4bit.resize((epd_width, epd_height))

        if prev_image:
            bbox = get_difference_bbox(image_resized, prev_image)

            if bbox:
                display.frame_buf.paste(image_resized.crop(bbox), bbox[:2])
                display.draw_partial(constants.DisplayModes.GC16)

                # Adjust sleep duration based on activity
                bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                if bbox_area > (epd_width * epd_height * 0.1):  # 10% of screen area changed
                    sleep_duration = 0.01  # High activity
                else:
                    sleep_duration = min(sleep_duration + 0.1, 10.0)  # Gradually increase sleep duration up to 1.0s
            else:
                sleep_duration = min(sleep_duration + 0.1, 10.0)  # No activity, increase sleep duration
        else:
            display.frame_buf.paste(image_resized, (0, 0))
            display.draw_full(constants.DisplayModes.GC16)

        prev_image = image_resized
        time.sleep(sleep_duration)

if __name__ == "__main__":
    main()
