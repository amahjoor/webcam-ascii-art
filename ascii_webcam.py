import cv2
import numpy as np
from PIL import Image
import os
import shutil
import sys
import select
import termios
import tty
import time
from datetime import datetime

class ASCIIConverter:
    def __init__(self):
        # ASCII characters from darkest to lightest
        self.ASCII_CHARS = "@%#*+=-:. "
        # Get initial terminal size
        self.update_dimensions()
        # ANSI escape codes for cursor movement and screen control
        self.HIDE_CURSOR = '\033[?25l'
        self.SHOW_CURSOR = '\033[?25h'
        self.CLEAR_SCREEN = '\033[2J'
        self.CURSOR_HOME = '\033[H'
        self.CLEAR_TO_END = '\033[0J'
        
    def update_dimensions(self):
        """Update dimensions based on terminal size"""
        # Get terminal size
        terminal = shutil.get_terminal_size()
        # Always use full width, height will be calculated based on aspect ratio
        self.width = terminal.columns
        self.term_height = terminal.lines
        
    def resize_image(self, image):
        """Resize image to fit terminal width while maintaining aspect ratio"""
        # Get current terminal width
        self.update_dimensions()
        
        # Always use full width and calculate height based on aspect ratio
        new_width = self.width
        image_ratio = image.shape[0] / image.shape[1]
        # Calculate height based on width and image ratio
        # Multiply by 0.5 because terminal characters are roughly twice as tall as wide
        new_height = int(new_width * image_ratio * 0.5)
        
        # Ensure height doesn't exceed terminal height
        new_height = min(new_height, self.term_height)
        
        return cv2.resize(image, (new_width, new_height))

    def to_grayscale(self, image):
        """Convert image to grayscale"""
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def pixels_to_ascii(self, image):
        """Convert pixels to ASCII characters"""
        pixels = image.astype(np.float32) / 255.0
        indices = (pixels * (len(self.ASCII_CHARS) - 1)).astype(np.int32)
        ascii_image = np.array(list(self.ASCII_CHARS))[indices]
        return ascii_image

    def frame_to_ascii(self, frame):
        """Convert a frame to ASCII art"""
        resized = self.resize_image(frame)
        grayscale = self.to_grayscale(resized)
        ascii_image = self.pixels_to_ascii(grayscale)
        return ascii_image

    def display_frame(self, ascii_frame, countdown=None):
        """Display the ASCII frame with proper terminal control"""
        # Move to home position
        sys.stdout.write(self.CURSOR_HOME)
        
        # Join all lines with exact terminal width
        frame_text = []
        for row in ascii_frame:
            # Ensure each line is exactly terminal width
            line = ''.join(row)
            line = line.ljust(self.width)  # Pad with spaces to full width
            frame_text.append(line)
        
        # If there's a countdown, add it to the center of the first line
        if countdown is not None:
            center_pos = self.width // 2
            countdown_text = str(countdown)
            start_pos = center_pos - len(countdown_text) // 2
            frame_text[0] = (
                frame_text[0][:start_pos] +
                countdown_text +
                frame_text[0][start_pos + len(countdown_text):]
            )
            
        # Join all lines and clear remaining screen
        sys.stdout.write('\n'.join(frame_text))
        sys.stdout.write(self.CLEAR_TO_END)
        sys.stdout.flush()

    def save_frame(self, ascii_frame):
        """Save ASCII frame to a text file in the frames directory"""
        # Create frames directory if it doesn't exist
        frames_dir = "frames"
        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(frames_dir, f"ascii_frame_{timestamp}.txt")
        
        # Save the frame with exact width
        with open(filename, 'w') as f:
            for row in ascii_frame:
                # Join the row and ensure it's exactly the terminal width
                line = ''.join(row)[:self.width].ljust(self.width)
                f.write(line + '\n')

def get_key_press():
    """Check if a key has been pressed"""
    if select.select([sys.stdin], [], [], 0.0)[0]:
        return sys.stdin.read(1)
    return None

def main():
    # Set up terminal for non-blocking input
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        
        converter = ASCIIConverter()
        # NOTE: 1 is the default webcam, however 0 is the first external webcam. Change this to 0 or 2, etc. to use a different webcam.
        cap = cv2.VideoCapture(1)  # Open webcam

        if not cap.isOpened():
            print("Error: Could not open webcam")
            return

        # Create frames directory if it doesn't exist
        if not os.path.exists("frames"):
            os.makedirs("frames")

        # Initial terminal setup
        sys.stdout.write(converter.HIDE_CURSOR)
        sys.stdout.write(converter.CLEAR_SCREEN)
        sys.stdout.write(converter.CURSOR_HOME)
        sys.stdout.flush()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to ASCII
            ascii_frame = converter.frame_to_ascii(frame)

            # Check for key press
            key = get_key_press()
            if key == 'q':
                break
            elif key == 's':
                converter.save_frame(ascii_frame)
            elif key == 't':
                # Timer mode - countdown from 3
                for i in range(3, 0, -1):
                    start_time = time.time()
                    while time.time() - start_time < 1.0:
                        # Update frame during countdown
                        ret, frame = cap.read()
                        if ret:
                            ascii_frame = converter.frame_to_ascii(frame)
                            converter.display_frame(ascii_frame, countdown=i)
                        if get_key_press() == 'q':  # Allow quitting during countdown
                            return
                # Take the picture after countdown
                ret, frame = cap.read()
                if ret:
                    ascii_frame = converter.frame_to_ascii(frame)
                    converter.save_frame(ascii_frame)

            # Display the current frame
            converter.display_frame(ascii_frame)

    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        # Show cursor again and clear screen before exiting
        sys.stdout.write(converter.SHOW_CURSOR)
        sys.stdout.write(converter.CLEAR_SCREEN)
        sys.stdout.write(converter.CURSOR_HOME)
        sys.stdout.flush()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 