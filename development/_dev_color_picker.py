from PIL import ImageGrab
import mouse
import pyautogui
import time

def pick_color():
    # Capture the screenshot of the entire screen
    screenshot = ImageGrab.grab()

    # Get the pixel color at the mouse position
    x, y = pyautogui.position()
    pixel_color = screenshot.getpixel((x, y))

    # Print the RGB color to the console
    print(f"RGB Color: {pixel_color}")

if __name__ == '__main__':
    while True:
        if mouse.is_pressed('right'):
            pick_color()
        else:
            time.sleep(0.025)
