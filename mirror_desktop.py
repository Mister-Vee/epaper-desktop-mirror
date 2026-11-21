"""Mirror the Raspberry Pi desktop onto an IT8951 e-paper display, redrawing only what changed.

2026 fixes over mirror_desktop_2023.py (kept for the record):
- no crash on the second frame (the grey image has no colour axis to sum over)
- resize first, then cut to 16 greys, so resizing can't bring back in-between greys
- the changed box includes its last row and column
- any change wakes it up; it only slows down while nothing changes (up to MAX_SLEEP)
- a full refresh every FULL_REFRESH_EVERY partial redraws clears ghosting
- signed maths for the difference, one screen grabber, aspect ratio kept
"""
import os
import time

import numpy as np
from PIL import Image, ImageOps

VCOM = -1.42                # set this to the value on YOUR panel's label or ribbon cable
SPI_HZ = 80_000_000         # lower it (e.g. 24_000_000) if you see garbled updates
THRESHOLD = 8               # grey difference (0-255) that counts as a change
FAST_SLEEP = 0.05           # seconds between checks while things are changing
MAX_SLEEP = 1.0             # longest wait while nothing changes
SLEEP_STEP = 0.1            # how quickly it backs off when idle
FULL_REFRESH_EVERY = 50     # partial redraws between full (ghost-clearing) refreshes


def to_panel(image, width, height):
    """Fit the screenshot to the panel (keeping its shape), then cut it to 16 greys."""
    grey = ImageOps.grayscale(image)
    fitted = ImageOps.pad(grey, (width, height), color=255)
    return fitted.point(lambda x: (x >> 4) * 17)  # 16 evenly spaced greys, 0..255


def changed_box(new, old, threshold=THRESHOLD):
    """(left, top, right, bottom) of the area that changed, right/bottom exclusive like PIL; None if nothing did."""
    diff = np.abs(np.asarray(new, dtype=np.int16) - np.asarray(old, dtype=np.int16))
    rows, cols = np.nonzero(diff > threshold)
    if rows.size == 0:
        return None
    return (int(cols.min()), int(rows.min()), int(cols.max()) + 1, int(rows.max()) + 1)


def next_sleep(current, changed):
    """Any change: check again soon. No change: back off a little, up to MAX_SLEEP."""
    return FAST_SLEEP if changed else min(current + SLEEP_STEP, MAX_SLEEP)


def main():
    from mss import mss
    from IT8951 import constants
    from IT8951.display import AutoEPDDisplay

    os.nice(10)
    display = AutoEPDDisplay(vcom=VCOM, spi_hz=SPI_HZ)
    width, height = display.width, display.height

    prev = None
    sleep = FAST_SLEEP
    partials = 0
    with mss() as grabber:
        monitor = grabber.monitors[1] if len(grabber.monitors) > 1 else grabber.monitors[0]
        while True:
            shot = grabber.grab(monitor)
            frame = to_panel(Image.frombytes("RGB", shot.size, shot.rgb), width, height)

            if prev is None or partials >= FULL_REFRESH_EVERY:
                display.frame_buf.paste(frame, (0, 0))
                display.draw_full(constants.DisplayModes.GC16)
                partials = 0
                box = True
            else:
                box = changed_box(frame, prev)
                if box:
                    display.frame_buf.paste(frame.crop(box), box[:2])
                    display.draw_partial(constants.DisplayModes.GC16)
                    partials += 1

            prev = frame
            sleep = next_sleep(sleep, bool(box))
            time.sleep(sleep)


if __name__ == "__main__":
    main()
