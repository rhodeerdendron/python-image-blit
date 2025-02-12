#!/usr/bin/env python3

# basic triangle drawing demo

from screen import *


# =========================================================

def lerp(start, end, t):
    """ Linear interpolation between two values """
    return start*(1-t) + end*t

def delerp(start, end, value):
    """ How far through [start,end] is the given value? """
    return (value-start) / (end-start)

def horizontal_line(image, y, xstart, xend, color):
    """ Blit a horizontal line to the given image """
    xlow, xhigh = sorted([xstart,xend])
    # blit row
    for x in range(int(xlow), int(xhigh)+1):
        image.pixel(x, y, color)

def triangle(image: Image, x0,y0, x1,y1, x2,y2, color):
    image.pixel(x0, y0, (255,0,0))
    image.pixel(x1, y1, (0,255,0))
    image.pixel(x2, y2, (0,0,255))

    # vertically sort our points 
    points = (x0,y0), (x1,y1), (x2,y2)                    # pack
    y_sorted_points = sorted(points, key=lambda p: p[1])  # sort by y
    (xh,yh), (xm,ym), (xl,yl) = y_sorted_points           # unpack

    # note: "high" means -y, since 0,0 is top-left
    print(f"highest {xh},{yh}")
    print(f"middle  {xm},{ym}")
    print(f"lowest  {xl},{yl}")

    # top triangle -- hi to mid
    for y in range(yh, ym):
        percent = delerp(yh, ym, y)         # how far along is the y?
        x = lerp(xh, xm, percent)           # how far along does that put x?
        percent_long = delerp(yh, yl, y)    # what about the long edge (hi to lo) y?
        x_long = lerp(xh, xl, percent_long) # how far along does that put the long edge x?

        horizontal_line(image, y, x, x_long, color)

    # bottom triangle -- mid to lo (including bottom)
    for y in range(ym, yl+1):
        percent = delerp(ym, yl, y)         # how far along is the y?
        x = lerp(xm, xl, percent)           # how far along does that put x?
        percent_long = delerp(yh, yl, y)    # what about the long edge (hi to lo) y?
        x_long = lerp(xh, xl, percent_long) # how far along does that put the long edge x?

        horizontal_line(image, y, x, x_long, color)


# =========================================================

image = Image(400,300)

WHITE = (255,255,255)
triangle(image, 100,150, 200,250, 250,100, WHITE)

image.show()
#image.save("out.png")
