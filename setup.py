from setuptools import setup, find_packages
import pkgutil


setup(
    name="rr.approx",
    version=pkgutil.get_data("rr.approx", "VERSION").strip(),
    packages=find_packages(),
    package_data={
        "rr.approx": ["VERSION"],
    },
    author="Rui Jorge Rei",
    author_email="rui.jorge.rei@googlemail.com",
    url="https://github.com/2xR/rr.approx",
    license="MIT",
    description="A module for approximate floating point arithmetic",
)
