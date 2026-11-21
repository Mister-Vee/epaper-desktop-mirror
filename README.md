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

**Set your own VCOM.** The script uses `vcom=-1.42`, which is right for my panel only. Use the value printed on your
display's ribbon cable or label (it is in `AutoEPDDisplay(vcom=..., spi_hz=...)`).

## Credits

Drives the display with GregDMeyer's [IT8951](https://github.com/GregDMeyer/IT8951) library (installed separately).

From [The Orange Garage](https://theorangegarage.com), Kent, Ohio.
