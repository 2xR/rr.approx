=========
rr.approx
=========

Approximate floating point arithmetic library. This simple module can be used to compare numbers using a relative and absolute tolerance, to mitigate floating point rounding errors.

.. code-block:: python

    from rr.approx import Approx

    x = Approx(0.1) * 3
    print x == 0.3  # True

The ``Approx`` class is very simple to use as a replacement for "regular" floats -- you can use ``Approx`` objects instead of floats in most (if not all) contexts: arithmetic and comparisons.

The ``ApproxContext`` class, also accessible as ``Approx.Context``, provides a context manager to temporarily modify the module's tolerance parameters.

.. code-block:: python

    from rr.approx import Approx

    print Approx.Context()  # display current context
    Approx.Context(1e-4, 1e-2).apply()  # permanently modify tolerances
    print Approx.Context()
    with Approx.Context(rtol=1e-5, atol=1e-3):  # temporary modification
        print Approx.Context()
    print Approx.Context()


Installation
------------

From PyPI ("stable" release):

.. code-block:: bash

    pip install rr.approx

Or from the Git repo:

.. code-block:: bash

    git clone https://github.com/2xR/rr.approx.git
    pip install ./rr.approx


Contributing
------------

Improvements are welcome through github pull requests (tests would be nice to have... :P)

And if you're using the library and would like to say *"thanks!"* and/or keep me working on it, why not `buy me a beer <https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=2UMJC8HSU8RFJ&lc=PT&item_name=DoubleR&item_number=github%2f2xR%2fpaypal&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donate_LG%2egif%3aNonHosted>`_ ?
