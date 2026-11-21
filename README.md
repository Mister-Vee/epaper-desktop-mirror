# epaper-desktop-mirror

Mirror a Raspberry Pi's desktop onto an IT8951 e-paper display (Waveshare), fast: it compares each frame with the last
one and redraws only the rectangle that changed, in 16 shades of grey.

Written for a Raspberry Pi 4 (8 GB) field computer. It is quicker than the usual PaperTTY route and easier on the SD
card. It runs the display at its suggested voltage and raises the controller's SPI clock. When nothing on screen moves
it backs off and checks less often.

The bigger win is what the Pi doesn't do: apps draw into a buffer, light apps and VNC carry the picture, and the Pi
turns its own display hardware off. That saves a lot of memory and power.

## Set up

```sh
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv
python3 -m venv myenv
source myenv/bin/activate
pip install Pillow mss numpy
pip install git+https://github.com/GregDMeyer/IT8951.git
python3 mirror_desktop.py
```

**Set your own VCOM.** `VCOM = -1.42` at the top of `mirror_desktop.py` is right for my panel only. Use the value
printed on your display's ribbon cable or label. The other settings are next to it: the SPI speed (lower it if updates
look garbled), how big a change counts, how fast it checks, and how often it does a full ghost-clearing refresh.

## Checks

The image logic can be checked on any computer, without a Pi or a panel:

```sh
pip install Pillow numpy
python -m unittest test_logic
```

## The 2023 version

`mirror_desktop_2023.py` is the original, kept for the record. It crashes on its second frame (it sums a colour axis that
a grey image doesn't have), slows down when small things change, resizes after cutting to 16 greys, and misses the last
row and column of each change. `mirror_desktop.py` fixes those and adds a regular full refresh to clear ghosting.
The fixed version is checked on a PC; it hasn't been run on the panel yet.

## Credits

Drives the display with GregDMeyer's [IT8951](https://github.com/GregDMeyer/IT8951) library (installed separately).

From [The Orange Garage](https://theorangegarage.com), Kent, Ohio.

## Licence

MIT. See [LICENSE](LICENSE).
