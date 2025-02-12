"""
# =========================================================

# main.py starter code

from screen import *

image = Image(400,300)

# modify pixels here!
image.pixel(100, 100, (255,0,0))
# TODO...

image.show()
image.save("out.png")

# =========================================================
"""

from PIL import Image as _PIL_Image
from typing import NoReturn

class Image:
    def __init__(self, width, height):
        self.size = (width,height)
        self.__canvas = _PIL_Image.new("RGB", self.size)
        self.__pixels = list(self.__canvas.getdata())
    
    @property
    def width(self) -> int: return self.size[0]
    @property
    def height(self) -> int: return self.size[1]

    def pixel(self, x: int, y: int, color: tuple) -> None:
        # coords too high?
        if x > self.width:  raise IndexError(f"x {x} too high ({self.width=})")
        if y > self.height: raise IndexError(f"y {y} too high ({self.height=})")
        # coords too low?
        if x < 0: raise IndexError(f"x {x} cannot be negative")
        if y < 0: raise IndexError(f"y {y} cannot be negative")
        # color invalid?
        all_ints = all(map(lambda c: isinstance(c, int), color))
        all_bounded = all(map(lambda c: 0 <= c <= 255, color))
        if len(color) != 3 or not all_ints or not all_bounded:
            raise ValueError(f"invalid color {color}")
        # all good :3
        self.__pixels[y * self.width + x] = color

    
    def __flush(self) -> None:
        self.__canvas.putdata(self.__pixels)

    def show(self, title:str="Output") -> NoReturn:
        # prepare tk
        #     note: these imports are done here, instead of global, so that
        #     this class can be used without installing tkinter (just don't
        #     call this function!)
        import tkinter as tk
        from PIL import ImageTk

        self.__flush()

        # create a tk window
        root = tk.Tk()
        root.title(title)
        root.geometry(f"{self.width}x{self.height}")
        root.resizable(width=False, height=False)

        # blit the image
        imagetk = ImageTk.PhotoImage(self.__canvas)
        panel = tk.Label(root, image=imagetk)
        panel.image = imagetk
        panel.pack()

        # display
        root.mainloop()
    
    def save(self, path: str) -> None:
        self.__flush()
        self.__canvas.save(path)
        print(f"Image saved to {path}")
