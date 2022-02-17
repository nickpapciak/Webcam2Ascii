import math, os, sys, termios, threading, time, tty
import cv2, yaml
from PIL import Image

with open('./config.yml', 'r') as f: 
    config = yaml.safe_load(f)

WIDTH, HEIGHT = config['width'], config['height']
if config['extreme resolution']: 
    # doubles the resolution
    HEIGHT*=2
    WIDTH*=2

DENSITY_LIST = config['density'] + ' ' * config['padding']
if config['background']['dark']: 
    DENSITY_LIST = DENSITY_LIST[::-1]  # reverses the string



def rgb_to_ascii(r: int, g: int, b: int) -> str: 
    """Maps a series of three rgb values [0, 255] to a character from the density list"""
    if config['grayscale method']['average']:
        # Simple average
        grayscale = round((r + g + b)/3)

    elif config['grayscale method']['luma']:
        # Luma method. Uses BT.709 coefficients
        grayscale = round((r*0.2126 + g*0.7152 + b*0.0722))

    else:
        # Desaturation method. Midpoint of max and min of RGB
        grayscale = round((max(r, g, b) + min(r, g, b)) / 2)

    return DENSITY_LIST[math.floor(grayscale * (len(DENSITY_LIST)-1)/255)]



def exit_handler():
    """Thread to capture input and see if user is querying a close"""
    os.system('')
    filedescriptors = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    while True:
        if sys.stdin.read(1)[0].lower() == 'q': break
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN,filedescriptors)

def ascii_output(frame) -> str: 
    """Retrieves webcam input each frame and returns an ascii representation of that frame"""
    img = Image.fromarray(frame).resize((WIDTH, HEIGHT))

    output = ''
    for i, rgb in enumerate(img.getdata()): 
        if i%WIDTH == 0: 
            output+='\n\t'
        output += rgb_to_ascii(*rgb)

    # clears screen, moves cursor to home, prints output
    return f'\033[2J\033[H\n\n{output}'



if __name__ == '__main__':
    t = threading.Thread(target=exit_handler)
    t.start()

    # w: 1280, h: 720 (16:9) on Mac
    vc = cv2.VideoCapture(0)
    print('\033[?25l') # hides cursor

    while True: 
        if not t.is_alive(): break
        frame = vc.read()[1]
        print(ascii_output(frame))
        time.sleep(0.015)

    print('\033[?25h') # shows cursor
    vc.release()
