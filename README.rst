=========
rr.approx
=========

Approximate floating point arithmetic library. This simple module can be used to compare numbers using a relative and absolute tolerance, to mitigate floating point rounding errors.

.. code-block::

    from rr.approx import Approx

    x = Approx(0.1) * 3
    print x == 0.3  # True

The ``Approx`` class is very simple to use as a replacement for "regular" floats.
