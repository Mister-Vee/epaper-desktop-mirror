"""Checks the image logic without a Pi or a panel: python -m unittest test_logic"""
import unittest

from PIL import Image

import mirror_desktop as m


class Logic(unittest.TestCase):
    def test_grey_frames_compare_without_crashing(self):
        a = Image.new("L", (40, 30), 255)
        self.assertIsNone(m.changed_box(a, a.copy()))

    def test_box_includes_last_row_and_column(self):
        a = Image.new("L", (40, 30), 255)
        b = a.copy()
        b.putpixel((39, 29), 0)
        box = m.changed_box(b, a)
        self.assertEqual(box, (39, 29, 40, 30))
        self.assertEqual(b.crop(box).size, (1, 1))

    def test_darker_and_lighter_changes_both_count(self):
        a = Image.new("L", (10, 10), 128)
        b = a.copy(); b.putpixel((2, 3), 0)
        c = a.copy(); c.putpixel((2, 3), 255)
        self.assertEqual(m.changed_box(b, a), (2, 3, 3, 4))
        self.assertEqual(m.changed_box(c, a), (2, 3, 3, 4))

    def test_panel_frame_has_only_16_greys_and_panel_size(self):
        shot = Image.linear_gradient("L").convert("RGB").resize((1920, 1080))
        frame = m.to_panel(shot, 1200, 825)
        self.assertEqual(frame.size, (1200, 825))
        self.assertLessEqual(len(frame.getcolors(256)), 16)

    def test_any_change_wakes_it_up_and_idle_backs_off_to_the_cap(self):
        s = m.next_sleep(m.MAX_SLEEP, True)
        self.assertEqual(s, m.FAST_SLEEP)
        for _ in range(100):
            s = m.next_sleep(s, False)
        self.assertEqual(s, m.MAX_SLEEP)


if __name__ == "__main__":
    unittest.main()
