#!/usr/bin/env python3

# a simple vec3 implementation helper class

from typing import Self, Tuple, Iterator
import math
import random

def random_unit() -> float:
    """ Returns a random number on the range of [-1,1]. """
    return random.random() * 2 - 1


class vec3:
    """
    A simple python 3-axis vector object. Can represent a point in space, a
    vector, a color, or some other 3-dimensional value.
    """
    def __init__(self, *args):
        # if three arguments given, extract to each part
        if (len(args) == 3):
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]
        # one argument was given
        elif (len(args) == 1):
            arg = args[0]
            # another vec3 was passed, copy it
            if isinstance(arg, self.__class__):
                self.x = arg.x
                self.y = arg.y
                self.z = arg.z
            # a list or tuple was passed, extract elements
            elif isinstance(arg, (list,tuple)):
                self.x = arg[0]
                self.y = arg[1]
                self.z = arg[2]
            # a single float or int was passed, swizzle it
            elif isinstance(arg, (int,float)):
                self.x = arg
                self.y = arg
                self.z = arg
            # some other value was passed (bad!)
            else:
                raise TypeError("invalid argument passed to vec3 constructor")
        # some other number of arguments was given (bad!)
        else:
            raise TypeError("invalid argument passed to vec3 constructor")

    # alias r, g, b to x, y, z so we can use this as a color as well

    @property
    def r(self): return self.x
    @r.setter
    def set_r(self, n): self.x = n

    @property
    def g(self): return self.x
    @g.setter
    def set_g(self, n): self.y = n

    @property
    def b(self): return self.x
    @b.setter
    def set_b(self, n): self.z = n

    # simple astuple() method and iterator access
    def astuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    def __iter__(self) -> Iterator:
        return iter(self.astuple())
    
    # simple string cast
    def __str__(self) -> str:
        return f"({self.x:+.3f}, {self.y:+.3f}, {self.z:+.3f})"

    # simple vector negation
    def __neg__(self) -> Self:
        return vec3(-self.x, -self.y, -self.z)

    # quick arithmetic operators -- e.g. self + rhs
    # note that the vec3 initializer has already done the hard work of
    # type-casting other types, let's just use that

    def __add__(self, rhs) -> Self:
        try:
            rhs = self.__class__(rhs)
            return vec3(self.x+rhs.x, self.y+rhs.y, self.z+rhs.z)
        except TypeError:
            return NotImplemented

    def __sub__(self, rhs) -> Self:
        try:
            rhs = self.__class__(rhs)
            return vec3(self.x-rhs.x, self.y-rhs.y, self.z-rhs.z)
        except TypeError:
            return NotImplemented

    def __mul__(self, rhs) -> Self:
        try:
            rhs = self.__class__(rhs)
            return vec3(self.x*rhs.x, self.y*rhs.y, self.z*rhs.z)
        except TypeError:
            return NotImplemented

    def __truediv__(self, rhs) -> Self:
        try:
            rhs = self.__class__(rhs)
            return vec3(self.x/rhs.x, self.y/rhs.y, self.z/rhs.z)
        except TypeError:
            return NotImplemented

    # right-side arithmetic operators -- e.g. lhs + self

    def __radd__(self, lhs) -> Self:
        try:
            lhs = self.__class__(lhs)
            return vec3(lhs.x+self.x, lhs.y+self.y, lhs.z+self.z)
        except TypeError:
            return NotImplemented

    def __rsub__(self, lhs) -> Self:
        try:
            lhs = self.__class__(lhs)
            return vec3(lhs.x-self.x, lhs.y-self.y, lhs.z-self.z)
        except TypeError:
            return NotImplemented

    def __rmul__(self, lhs) -> Self:
        try:
            lhs = self.__class__(lhs)
            return vec3(lhs.x*self.x, lhs.y*self.y, lhs.z*self.z)
        except TypeError:
            return NotImplemented

    def __rtruediv__(self, lhs) -> Self:
        try:
            lhs = self.__class__(lhs)
            return vec3(lhs.x/self.x, lhs.y/self.y, lhs.z/self.z)
        except TypeError:
            return NotImplemented

    # in-place arithmetic operators -- e.g. self += rhs

    def __iadd__(self, rhs) -> Self:
        try:
            rhs = self.__class__(rhs)
            self.x += rhs.x
            self.y += rhs.y
            self.z += rhs.z
            return self
        except TypeError:
            return NotImplemented

    def __isub__(self, rhs) -> Self:
        try:
            rhs = self.__class__(rhs)
            self.x -= rhs.x
            self.y -= rhs.y
            self.z -= rhs.z
            return self
        except TypeError:
            return NotImplemented

    def __imul__(self, rhs) -> Self:
        try:
            rhs = self.__class__(rhs)
            self.x *= rhs.x
            self.y *= rhs.y
            self.z *= rhs.z
            return self
        except TypeError:
            return NotImplemented

    def __itruediv__(self, rhs) -> Self:
        try:
            rhs = self.__class__(rhs)
            self.x /= rhs.x
            self.y /= rhs.y
            self.z /= rhs.z
            return self
        except TypeError:
            return NotImplemented

    # special vector operations -- we aren't gonna type-cast here as well like
    # above for sake of making the user be explicit with casting inputs

    @classmethod
    def squared_length(cls, v: Self) -> float:
        if not isinstance(v, cls):
            raise TypeError("cannot perform squared_length with non-vec3 type")
        return v.x**2 + v.y**2 + v.z**2

    @classmethod
    def length(cls, v: Self) -> float:
        if not isinstance(v, cls):
            raise TypeError("cannot perform length with non-vec3 type")
        ## manually inlining this results in about a 1.13x speedup
        ## (0.46s/1Mi vs 0.52 on test machine)
        # return math.sqrt(cls.squared_length(v))
        return math.sqrt(v.x**2 + v.y**2 + v.z**2)

    @classmethod
    def distance(cls, lhs: Self, rhs: Self) -> float:
        if not isinstance(lhs, cls) or not isinstance(rhs, cls):
            raise TypeError("cannot perform distance with non-vec3 type(s)")
        ## manually inlining this results in about a 2.27x speedup
        ## (1.25s/1Mi vs 0.55 on test machine)
        # return cls.length(lhs - rhs)
        return math.sqrt((lhs.x-rhs.x)**2 + (lhs.y-rhs.y)**2 + (lhs.z-rhs.z)**2)

    @classmethod
    def normalize(cls, v: Self) -> Self:
        if not isinstance(v, cls):
            raise TypeError("cannot perform normalize with non-vec3 type")
        ## manually inlining this results in about a 1.09x speedup
        ## (2.09s/1Mi vs 1.92 on test machine)
        # return v / cls.length(v)
        return v / math.sqrt(v.x**2 + v.y**2 + v.z**2)

    @classmethod
    def dot(cls, lhs: Self, rhs: Self) -> float:
        if not isinstance(lhs, cls) or not isinstance(rhs, cls):
            raise TypeError("cannot perform cross with non-vec3 type(s)")
        return lhs.x*rhs.x + lhs.y*rhs.y + lhs.z*rhs.z

    @classmethod
    def cross(cls, lhs: Self, rhs: Self) -> Self:
        if not isinstance(lhs, cls) or not isinstance(rhs, cls):
            raise TypeError("cannot perform cross with non-vec3 type(s)")
        return cls(
            lhs.y*rhs.z - lhs.z*rhs.y,
            lhs.z*rhs.x - lhs.x*rhs.z,
            lhs.x*rhs.y - lhs.y*rhs.x
        )
    
    @classmethod
    def reflect(cls, v: Self, n: Self) -> Self:
        """ Reflects vec3 v across vec3 n. """
        if not isinstance(v, cls) or not isinstance(n, cls):
            raise TypeError("cannot perform reflect with non-vec3 type(s)")
        n = cls.normalize(n)
        return v - 2 * cls.dot(v, n) * n

    @classmethod
    def random_on_unit_sphere(cls) -> Self:
        """ Returns a random vector on the unit sphere. """
        # generate a random vector, and return if it is within the unit sphere
        while True:
            v = cls(random_unit(), random_unit(), random_unit())
            length = cls.squared_length(v)  # >1 will stay >1 and <1 will stay <1
            if (length <= 1):
                # normalize and return
                return v / math.sqrt(length)

    @classmethod
    def random_on_hemisphere(cls, v: Self) -> Self:
        """ Returns a random vector on the hemisphere of v. """
        r = cls.random_on_unit_sphere()
        return r if (cls.dot(r, v) > 0) else -r


# =========================================================


def benchmark():

    import time

    def benchmark_single(title: str, args: list, f):
        print('='*10, title, '='*10)
        for niters in (10, 1_000, 1_000_000):
            # generate random data arrays
            data = [
                [ gen() for gen in args ]
                for _ in range(niters)
            ]
            out = [ None for _ in range(niters) ]
            # run benchmark
            start = time.perf_counter()
            for i in range(niters):
                out[i] = f(*data[i])
            elapsed = time.perf_counter() - start
            print(str(niters).rjust(7), f"iters took {elapsed:02.4f}s")
        print()

    N = 20

    benchmark_single(
        f"1/{N} vector-construct-single",
        [
            lambda: random_unit() * 10
        ],
        lambda r: vec3(r)
    )

    benchmark_single(
        f"2/{N} vector-construct-triple",
        [
            lambda: random_unit() * 10,
            lambda: random_unit() * 10,
            lambda: random_unit() * 10
        ],
        lambda x,y,z: vec3(x,y,z)
    )

    benchmark_single(
        f"3/{N} vector-add-vector",
        [
            lambda: vec3(random_unit() * 10),
            lambda: vec3(random_unit() * 10)
        ],
        lambda lhs,rhs: lhs+rhs
    )

    benchmark_single(
        f"4/{N} vector-multiply-vector",
        [
            lambda: vec3(random_unit() * 10),
            lambda: vec3(random_unit() * 10)
        ],
        lambda lhs,rhs: lhs*rhs
    )

    benchmark_single(
        f"5/{N} vector-add-float",
        [
            lambda: vec3(random_unit() * 10),
            lambda: random_unit() * 10
        ],
        lambda lhs,rhs: lhs+rhs
    )

    benchmark_single(
        f"6/{N} vector-multiply-float",
        [
            lambda: vec3(random_unit() * 10),
            lambda: random_unit() * 10
        ],
        lambda lhs,rhs: lhs*rhs
    )

    benchmark_single(
        f"7/{N} float-add-vector",
        [
            lambda: random_unit() * 10,
            lambda: vec3(random_unit() * 10)
        ],
        lambda lhs,rhs: lhs+rhs
    )

    benchmark_single(
        f"8/{N} float-multiply-vector",
        [
            lambda: random_unit() * 10,
            lambda: vec3(random_unit() * 10)
        ],
        lambda lhs,rhs: lhs*rhs
    )

    benchmark_single(
        f"9/{N} vector-squared-length",
        [
            lambda: vec3(random_unit() * 10)
        ],
        lambda v: vec3.squared_length(v)
    )

    def length_slow(cls, v):
        if not isinstance(v, cls):
            raise TypeError("cannot perform length_slow with non-vec3 type")
        return math.sqrt(cls.squared_length(v))

    def distance_slow(cls, lhs, rhs):
        if not isinstance(lhs, cls) or not isinstance(rhs, cls):
            raise TypeError("cannot perform distance_slow with non-vec3 type(s)")
        return length_slow(cls, lhs - rhs)

    def normalize_slow(cls, v):
        if not isinstance(v, cls):
            raise TypeError("cannot perform normalize_slow with non-vec3 type")
        return v / length_slow(cls, v)

    benchmark_single(
        f"10/{N} vector-length-builtin",
        [
            lambda: vec3(random_unit() * 10)
        ],
        lambda v: vec3.length(v)
    )

    benchmark_single(
        f"11/{N} vector-length-slow",
        [
            lambda: vec3(random_unit() * 10)
        ],
        lambda v: length_slow(vec3, v)
    )

    benchmark_single(
        f"12/{N} vector-distance-builtin",
        [
            lambda: vec3(random_unit() * 10),
            lambda: vec3(random_unit() * 10)
        ],
        lambda a,b: vec3.distance(a, b)
    )

    benchmark_single(
        f"13/{N} vector-distance-slow",
        [
            lambda: vec3(random_unit() * 10),
            lambda: vec3(random_unit() * 10)
        ],
        lambda a,b: distance_slow(vec3, a, b)
    )

    benchmark_single(
        f"14/{N} vector-normalize-builtin",
        [
            lambda: vec3(random_unit() * 10)
        ],
        lambda v: vec3.normalize(v)
    )

    benchmark_single(
        f"15/{N} vector-normalize-slow",
        [
            lambda: vec3(random_unit() * 10)
        ],
        lambda v: normalize_slow(vec3, v)
    )

    benchmark_single(
        f"16/{N} vector-dot",
        [
            lambda: vec3(random_unit() * 10),
            lambda: vec3(random_unit() * 10)
        ],
        lambda a,b: vec3.dot(a, b)
    )

    benchmark_single(
        f"17/{N} vector-cross",
        [
            lambda: vec3(random_unit() * 10),
            lambda: vec3(random_unit() * 10)
        ],
        lambda a,b: vec3.cross(a, b)
    )

    benchmark_single(
        f"18/{N} vector-refect",
        [
            lambda: vec3(random_unit() * 10),
            lambda: vec3(random_unit() * 10)
        ],
        lambda a,b: vec3.reflect(a, b)
    )

    benchmark_single(
        f"19/{N} vector-random-on-unit-sphere",
        [
        ],
        lambda: vec3.random_on_unit_sphere()
    )

    benchmark_single(
        f"20/{N} vector-random-on-hemisphere",
        [
            lambda: vec3(random_unit() * 10)
        ],
        lambda v: vec3.random_on_hemisphere(v)
    )


# run benchmark if we're running this file directly
if __name__ == '__main__':
    try:
        benchmark()
    except KeyboardInterrupt:
        print("quitting benchmark")
        exit(0)

