# Webcam ASCII art in the terminal

`ascii_webcam.py` reads a webcam with OpenCV and prints each frame as ASCII that follows the terminal width. Press `s` to save the current frame, `t` for a 3-second countdown and then a save, or `q` to quit.

It imports `termios` and `tty`, so it runs in a Unix terminal. It does not run on Windows.

## Run it

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ascii_webcam.py
```

`requirements.txt` is `opencv-python`, `numpy`, and `Pillow`.

## License

[MIT](LICENSE)
