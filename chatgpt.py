import cv2 as cv
import numpy as np
from cvDraw import *

def draw(x):
    global p0, p1
    d = 1#cv.getTrackbarPos('thickness', 'window')
    d = 1 if d==0 else d
    i = 0#cv.getTrackbarPos('color', 'window')
    color = colors[i]
    img[:] = img0
    cv.rectangle(img, p0, p1, color, d)
    cv.imshow('window', img)
    text = f'color={color}, thickness={d}'
    cv.displayOverlay('window', text)

def mouse(event, x, y, flags, param):
    global p0, p1
    if event == cv.EVENT_LBUTTONDOWN:
        img0[:] = img
        p0 = x, y
    elif event == cv.EVENT_MOUSEMOVE and flags == 1:
        p1 = x, y
    elif event == cv.EVENT_LBUTTONUP:
        p1 = x, y
    draw(0)

cv.setMouseCallback('window', mouse)
#cv.createTrackbar('color', 'window', 0, 6, None)
#cv.createTrackbar('thickness', 'window', 0, 10, None)

cv.waitKey(0)
cv.destroyAllWindows()

######################################

import numpy as np
import cv2 as cv

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)

CYAN = (255, 255, 0)
MAGENTA = (255, 0, 255)
YELLOW = (0, 255, 255)

colors = (RED, GREEN, BLUE, MAGENTA, CYAN, YELLOW, WHITE)
p0 = p1 = 0, 0

img0 = cv.imread('datasets\Image__2022-09-23__19-59-27.jpg') #np.zeros((200, 500, 3), np.uint8)
img = img0.copy()
cv.imshow('window', img)