# python-screen

A simple class for blitting pixels to a canvas, and either displaying that canvas on-screen or writing to a file.

### `Image` usage

```py
from screen import *

image = Image(640,480)

image.pixel(100, 150, (255,0,0))
image.pixel(200, 250, (0,255,0))
image.pixel(250, 100, (0,0,255))

image.show()
```

---

### Graphics demo programs

Also included is a few samples of very primitive graphics code, to demonstrate how such things function under-the-hood. **Do note that these are all written for teaching purposes, and only "trivial" optimizations are taken where they do not sully the learning experience.**

`triangle.py` - demos how triangles are rasterized to the screen.
`raytracer.py` - a very simple raytracer, complete with camera and materials and all.
