"""This module exposes the Approx class which allows approximate comparison of floating point
values. Two values are considered equal if their relative difference is smaller than a given
relative tolerance (http://en.wikipedia.org/wiki/Relative_difference). The base comparison is:

    |x-y| / max(|x|,|y|) < rtol

This formula breaks down when one of the numbers is 0, since no number other than 0 itself is
considered approximately == 0 unless rtol > 1. Replacing x by 0 in the formula and assuming
y != 0, yields

    |y| / |y| < rtol

So rtol would effectively have to be > 1 for the formula to accept any non-zero number as "close
enough" to 0. Note however that rtol should normally be a small positive number (e.g. 1e-6), so
this is not satisfactory.

To fix this, we introduce a second tolerance parameter: absolute tolerance. First, we transform the
previous inequality by multiplying both sides by max(|x|,|y|). Since this is > 0 (because at least
one of the numbers is != 0), the direction of the inequality is maintained, leading to

    |x-y| < rtol * max(|x|,|y|)

Now, we simply add the absolute tolerance to the right-hand side of the inequality

    |x-y| < atol + rtol * max(|x|,|y|)

This keeps at least the absolute tolerance for when one of the numbers is 0. Additionally, the
influence of absolute tolerance should fade when comparing large numbers, since the other term
should be much larger.
"""
import collections
import contextlib
import itertools
import math

__version__ = "0.3.0"
__author__ = "Rui Rei"
__copyright__ = "Copyright 2017 {author}".format(author=__author__)
__license__ = "MIT"


class Approx(float):
    """A float subclass to alleviate (but does not eliminate!) floating point rounding errors by
    comparing approximately. Comparison operators are redefined to use the absolute and relative
    tolerances defined at the class level.
    """

    # Default tolerance parameters. Can be customized directly, but Approx.context() is the
    # recommended way to change them.
    rtol = 1e-9  # default relative tolerance
    atol = 1e-12  # default absolute tolerance

    @classmethod
    @contextlib.contextmanager
    def context(cls, rtol=None, atol=None):
        """Temporarily change the tolerances for comparisons involving instances of `cls`."""
        # Record original state of the tolerance parameters. We do not obtain the values from
        # `cls` using attribute access as that could give us inherited values. Instead,
        # we look up the tolerances directly in the class dict to be able to tell if it was
        # originally missing or not. This is useful below when restoring the original state.
        missing = object()
        orig_tols = {
            "rtol": cls.__dict__.get("rtol", missing),
            "atol": cls.__dict__.get("atol", missing),
        }
        # Change tolerance parameters.
        if rtol is not None:
            cls.rtol = rtol
        if atol is not None:
            cls.atol = atol
        try:
            yield  # run with statement block
        finally:
            # Restore the class' original state.
            for attr, orig_val in orig_tols.items():
                if orig_val is not missing:
                    setattr(cls, attr, orig_val)
                elif attr in cls.__dict__:
                    delattr(cls, attr)

    def tolerance(self, other):
        """Compute the actual tolerance for approximate comparison between `self` and `other`."""
        x = float(self)
        y = float(other)
        return self.atol + self.rtol * max(abs(x), abs(y))

    # --------------------------------------------------------------------------
    # Customize instance creation and represention
    __slots__ = ()  # prevent creation of a dictionary per Approx instance

    def __repr__(self):
        return float.__repr__(self) + "~"

    def __str__(self):
        return float.__str__(self) + "~"

    # --------------------------------------------------------------------------
    # Rich comparison operators
    def __eq__(self, other):
        """Approximate comparison of floating point values using absolute and relative tolerances.

        This function is equivalent to

            |x - y| <= atol + rtol * max(|x|, |y|)

        This is very similar to what is done in numpy, but this function is symmetric, that is,
        the order of the two numbers is irrelevant to the result. In numpy.isclose(),
        the relative tolerance is multiplied by the absolute value of the second number,
        so calling the function with reversed arguments can give different results; these cases
        should be very rare but can lead to extremely hard to find bugs. I suppose this decision
        was made for performance reasons, but I prefer to keep the results intuitive.
        """
        x = float(self)
        y = float(other)
        if x == y:
            return True
        z = abs(x - y) - self.atol
        return z <= 0.0 or z <= self.rtol * max(abs(x), abs(y))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return float.__le__(self, other) or self.__eq__(other)

    def __lt__(self, other):
        return float.__lt__(self, other) and not self.__eq__(other)

    def __ge__(self, other):
        return float.__ge__(self, other) or self.__eq__(other)

    def __gt__(self, other):
        return float.__gt__(self, other) and not self.__eq__(other)

    # --------------------------------------------------------------------------
    # Rich comparison operators for iterables
    @classmethod
    def _deep_apply(cls, op, x, y):
        """This internal function allows the application of rich comparison operators between two
        numbers, a number and a (possibly nested) sequence of numbers, or two (flat/nested)
        sequences of numbers. When comparing two sequences, missing values are filled with NaN.
        Returns a generator expression in case sequences are involved, or a plain old boolean if
        two numbers are being compared.
        """
        x_is_iterable = isinstance(x, collections.Iterable)
        y_is_iterable = isinstance(y, collections.Iterable)
        if x_is_iterable and y_is_iterable:
            return (
                cls._deep_apply(op, u, v)
                for u, v in itertools.zip_longest(x, y, fillvalue=math.nan)
            )
        elif x_is_iterable:
            return (cls._deep_apply(op, u, y) for u in x)
        elif y_is_iterable:
            return (cls._deep_apply(op, x, v) for v in y)
        else:
            return op(cls(x), y)

    @classmethod
    def deep_eq(cls, x, y):
        return cls._deep_apply(cls.__eq__, x, y)

    @classmethod
    def deep_ne(cls, x, y):
        return cls._deep_apply(cls.__ne__, x, y)

    @classmethod
    def deep_le(cls, x, y):
        return cls._deep_apply(cls.__le__, x, y)

    @classmethod
    def deep_lt(cls, x, y):
        return cls._deep_apply(cls.__lt__, x, y)

    @classmethod
    def deep_ge(cls, x, y):
        return cls._deep_apply(cls.__ge__, x, y)

    @classmethod
    def deep_gt(cls, x, y):
        return cls._deep_apply(cls.__gt__, x, y)

    # --------------------------------------------------------------------------
    # Other numeric operators
    def __add__(self, other): return type(self)(float.__add__(self, other))
    def __sub__(self, other): return type(self)(float.__sub__(self, other))
    def __mul__(self, other): return type(self)(float.__mul__(self, other))
    def __truediv__(self, other): return type(self)(float.__truediv__(self, other))
    def __floordiv__(self, other): return type(self)(float.__floordiv__(self, other))
    def __mod__(self, other): return type(self)(float.__mod__(self, other))
    def __divmod__(self, other): return type(self)(float.__divmod__(self, other))
    def __pow__(self, other): return type(self)(float.__pow__(self, other))

    def __radd__(self, other): return type(self)(float.__radd__(self, other))
    def __rsub__(self, other): return type(self)(float.__rsub__(self, other))
    def __rmul__(self, other): return type(self)(float.__rmul__(self, other))
    def __rtruediv__(self, other): return type(self)(float.__rtruediv__(self, other))
    def __rfloordiv__(self, other): return type(self)(float.__rfloordiv__(self, other))
    def __rmod__(self, other): return type(self)(float.__rmod__(self, other))
    def __rdivmod__(self, other): return type(self)(float.__rdivmod__(self, other))
    def __rpow__(self, other): return type(self)(float.__rpow__(self, other))

    def __neg__(self): return type(self)(float.__neg__(self))
    def __pos__(self): return type(self)(float.__pos__(self))
    def __abs__(self): return type(self)(float.__abs__(self))


# Provide module-level functions for approximate comparison operators.
def tolerance(x, y):
    return Approx(x).tolerance(y)


def eq(x, y):
    return Approx(x) == y


def ne(x, y):
    return Approx(x) != y


def le(x, y):
    return Approx(x) <= y


def lt(x, y):
    return Approx(x) < y


def ge(x, y):
    return Approx(x) >= y


def gt(x, y):
    return Approx(x) > y


# Set up some convenient aliases for Approx class methods.
context = Approx.context
deep_eq = Approx.deep_eq
deep_ne = Approx.deep_ne
deep_le = Approx.deep_le
deep_lt = Approx.deep_lt
deep_ge = Approx.deep_ge
deep_gt = Approx.deep_gt
