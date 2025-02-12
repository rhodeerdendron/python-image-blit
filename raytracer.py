#!/usr/bin/env python3

# basic triangle drawing demo

from screen import *


# =========================================================

from typing import Optional, List, Tuple
import math
import time
import random

from vec3 import vec3


# first, some simple helper functions

def lerp(a, b, t: float):
    """ Returns a when t=0, b when t=1, and lerps between a and b between. """
    return (1-t)*a + t*b

def smoothstep(a, b, t: float):
    """ Smoothly transitions between a and b based on t. """
    if   t <= 0: return a
    elif t >= 1: return b
    return lerp(a, b, 3*t**2 - 2*t**3)

def clamp(a: float, b: float, f: float) -> float:
    """ Clamps float f to the range of [a,b]. """
    return max(a, min(b, f))

def clamp01_vec(v: vec3) -> vec3:
    """ Clamps vec3 v to the range of [0,1] on all axes. """
    return vec3(clamp(0,1,v.x), clamp(0,1,v.y), clamp(0,1,v.z))

def color_to_ints(color: vec3) -> Tuple[int, int, int]:
    """ Converts the given vec3 color to a tuple of RGB values. """
    color = color.astuple()
    color = map(lambda c: clamp(0,1,c), color)  # clamp to [0,1]
    color = map(lambda c: int(c*255.99), color) # map to [0,255]
    return tuple(color)

def format_time(seconds: float) -> str:
    """ Formats the given number of seconds into an H:M:S string. """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    hours, minutes, seconds = map(int, (hours, minutes, seconds))
    return f"{hours}h{minutes:02}m{seconds:02}"


# and now, the good stuff.

class Ray:
    """ Represents a ray in a given direction from a given point. """
    def __init__(self, pos: vec3, dir: vec3):
        self.pos = pos
        self.dir = dir
    
    def cast_by(self, t: float) -> vec3:
        """ Returns 't' units "stepped into" this ray. """
        return self.pos + t*self.dir


class Camera:
    """ Generates rays per pixel from the origin. """
    def __init__(self,
        look_from: vec3, look_at: vec3, world_up: vec3,
        aspect: float, vfov: float
    ):
        self.origin = look_from  # where is the camera
        self.world_up = world_up  # which way is "up"
        self.aspect = aspect  # camera's aspect ratio
        self.vfov = vfov  # camera's vertical field-of-view

        # we'll need a few more things for a proper camera; u, v, and w are
        # called the camera's "basis vectors." we're not doing any fancy
        # camera movement or rotation, so we don't need to save them

        w = vec3.normalize(look_at - look_from)      # direction cam is facing
        u = vec3.normalize(vec3.cross(w, world_up))  # cam's "right"
        v = vec3.cross(u, w)                         # cam's "up"

        # instead, we'll save a vec3 that represents the point in space that
        # the top-left of the screen occupies, a vector that represents the
        # ray from the top-left corner of the screen to the top-right, and one
        # that represents the ray from the top-left to the bottom-left

        half_height = math.tan(math.radians(vfov)/2)
        half_width = aspect * half_height

        # this is the vector that represents the transformation from the camera
        # origin to the top-left corner of the screen in world-space
        # that is, half the screen's width left (-u), half the screen's height
        # up (v), and 1 unit forward (w)
        self.topleft = half_width*-u + half_height*v + w
        
        # represents top edge, top-left to top-right
        self.horizontal = 2 * half_width * u
        # represents left edge, top-left to bottom-left
        self.vertical = 2 * half_height * -v

        print("camera origin is", self.origin)
        print("half_width", f"{half_width:.3f}")
        print("half_height", f"{half_height:.3f}")
        print("w", w)
        print("u", u)
        print("v", v)
        print("camera top-left is", self.topleft)
    
    def cast_ray(self, u: float, v: float) -> Ray:
        """ Casts a ray from the camera origin through the screen position u,v. """
        # generate a ray from the camera origin to the screen position u,v
        # because of how we decided to save topleft, horizontal, and vertical,
        # this is as simple as multiplying those vectors by the screen u and v
        direction = self.topleft + u*self.horizontal + v*self.vertical
        return Ray(self.origin, direction)


class HitRecord:
    """ Stores information about where and how a ray collided with a sphere. """
    def __init__(self,
        sphere,
        ray_in: Ray,
        normal: vec3,
        collision_point: vec3
    ):
        self.sphere = sphere
        self.ray_in = ray_in
        self.normal = normal
        self.collision_point = collision_point


class Material:
    """ Stores information about how the light should bounce off a sphere. """
    def __init__(self):
        pass

    def scatter(self, hit: HitRecord) -> Tuple[Ray, vec3]:
        raise NotImplementedError("cannot instance Material base class")

class Normals(Material):
    """ Simple texture that visualizes normals. """
    def __init__(self):
        super().__init__()

    def scatter(self, hit: HitRecord) -> Tuple[Ray, vec3]:
        return (None, hit.normal)

class Diffuse(Material):
    """ Diffuse, matte texture. """
    def __init__(self, color: vec3):
        super().__init__()
        self.color = color
    
    def scatter(self, hit: HitRecord) -> Tuple[Ray, vec3]:
        # pick a random direction to bounce
        direction = vec3.random_on_hemisphere(hit.normal)
        # return ray and color information
        ray = Ray(hit.collision_point, direction)
        return (ray, self.color)

class Light(Material):
    """ A glowing material that outputs more light than it receives. """
    def __init__(self, color: vec3, strength: float):
        super().__init__()
        self.color = color
        self.strength = strength
    
    def scatter(self, hit: HitRecord) -> Tuple[Ray, vec3]:
        # no reflections here! just add a super-strong color
        return (None, self.color * self.strength)


class Sphere:
    """ Represents a sphere with a given radius, position, and material. """
    def __init__(self, r: float, pos: vec3, material: Material):
        self.r = r
        self.pos = pos
        self.material = material
    
    def collide(self, ray: Ray) -> Optional[HitRecord]:
        """
        Returns a HitRecord object if the given ray collides with this sphere,
        or None if it doesn't.
        ---
        To solve for this, first, three things must be established:
        1.  The ray can be thought of as a point in space `p` and a direction
            vector `d`, such that any point along the ray can be thought of as
            some scalar `t` along `p + t*d`.
        2.  The sphere can be thought of as a point in space `c` and a scalar
            radius `r`, such that the surface of the sphere is described by
            all points `s` such that `|c - s| = r**2`.
        3.  The intersection of the ray and the sphere is some point that
            satisfies both conditions.
        ---
        I am not explaining this algorithm here, wikipedia does a better job
        and has LaTeX support.
        https://en.wikipedia.org/wiki/Line%E2%80%93sphere_intersection
        """
        u = vec3.normalize(ray.dir)
        oc = ray.pos - self.pos
        # find quadratic roots
        u_oc = vec3.dot(u, oc)
        oc_rsq = vec3.squared_length(oc) - self.r**2
        discrim = u_oc**2 - oc_rsq
        if discrim > 0:  # hit!
            sqrt_discrim = math.sqrt(discrim)
            for d in ( -u_oc-sqrt_discrim, -u_oc+sqrt_discrim ):
                # only keep if the intersection is "ahead" of the ray
                if (d > 0):
                    collision_point = ray.cast_by(d)
                    normal = (collision_point - self.pos) / self.r  # normalized
                    return HitRecord(
                        sphere = self,
                        ray_in = ray,
                        normal = normal,
                        collision_point = collision_point)
        return None


def closest_collision(ray: Ray, spheres: List[Sphere]) -> Optional[HitRecord]:
    """ Find the closest collision point given a ray and a list of spheres. """
    closest_collision = None
    closest_dist = math.inf
    for sphere in spheres:
        collision = sphere.collide(ray)
        if collision is not None:  # did we hit this sphere?
            dist = vec3.squared_length(  # squared_length to save compute time
                collision.collision_point - ray.pos)
            if dist < closest_dist:
                closest_dist = dist
                closest_collision = collision
    return closest_collision


MAX_BOUNCES = 12
SAMPLES_PER_PIXEL = 4
SKY_COLOR_DOWN = vec3(0.4, 0.5, 0.7)
SKY_COLOR_UP   = vec3(0.6, 0.8, 1.0)

def raytrace(image: Image, camera: Camera, spheres: List[Sphere]):
    print()  # allocate newline for \r
    last_progress = -1  # -1 instead of 0 to trigger first print
    last_length = 0
    start = time.time()

    # 1. for each pixel in the image...
    for y in range(image.height):
        for x in range(image.width):

            final_color = vec3(0.0)
            for sample in range(SAMPLES_PER_PIXEL):
                # 2. generate a ray from the camera origin to this pixel...
                u, v = x/image.width, y/image.height
                ray = camera.cast_ray(u, v)

                # 3. bounce it around a bunch!
                running_color = vec3(1.0)
                for bounce in range(MAX_BOUNCES):
                    closest = closest_collision(ray, spheres)
                    if closest is None:  # ray shot off into space
                        break

                    # 4. calculate the color and reflection of this sphere
                    ray, color = closest.sphere.material.scatter(closest)
                    running_color *= color
                    if ray is None:  # material fully absorbed ray
                        break

                # 5. all done bouncing! attenuate sky color: lerp grey->blue
                # based on final ray direction
                if ray is not None:
                    unit_dir = vec3.normalize(ray.dir)
                    t = 0.5 * (unit_dir.z+1)  # scale y [-1,1] to [0,1]
                    running_color *= smoothstep(SKY_COLOR_DOWN, SKY_COLOR_UP, t)
                final_color += clamp01_vec(running_color)

            # 6. once all our samples have been collected, average them out,
            # and blit the final color to the image
            final_color /= SAMPLES_PER_PIXEL
            image.pixel(x, y, color_to_ints(final_color))

            # 7. output progress
            percent = (y*image.width + x + 1) / (image.width*image.height)
            progress = int(100 * percent)
            if (progress != last_progress):
                last_progress = progress
                # progress bar and percent completed
                width = 40
                n_high = int(width*percent)
                progress_bar = '#'*n_high + '.'*(width-n_high)
                progress_pct = f'{progress}%'.rjust(4)
                # time so far and est. remaining
                taken = time.time() - start
                est = (taken / percent) - taken
                # put it all together
                out = '\r'
                out += f"progress: {progress_pct} [{progress_bar}] "
                out += f"{format_time(taken)} / est: {format_time(est)}"
                # pad with spaces to last length (to prevent \r artifacts)
                this_length = len(out)
                out.ljust(last_length)
                last_length = this_length
                print(out, end='', flush=True)
    
    # final print to commit last progress bar line
    print()



# =========================================================

zoom = 1.0 / 3
image = Image(1280*zoom,1080*zoom)

spheres = [
    Sphere(  1.0, vec3(2.0, 0.0,    0.0), Diffuse(vec3(0.9, 0.4, 0.3))),
    Sphere(  0.6, vec3(1.0, 2.0,    3.0), Light(  vec3(1.0, 0.8, 0.1), 8)),
    Sphere(250.0, vec3(0.0, 0.0, -251.0), Diffuse(vec3(0.8, 0.8, 0.8)))
]
camera = Camera(
    look_from = vec3(-3.0,  0.0,  0.0),
    look_at   = vec3( 0.0,  0.0,  0.0),
    world_up  = vec3( 0.0,  0.0,  1.0),
    aspect = image.width / image.height,
    vfov = 90.0
)

# catch ctrl+c for early exit
try:
    raytrace(image, camera, spheres)
except KeyboardInterrupt:
    print("\nstopping raytrace early")

image.show()
image.save("out.png")
