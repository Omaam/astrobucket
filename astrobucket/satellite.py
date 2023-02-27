"""Stellite module.

Note:
    First letter and following letters of satelite class must be
    uppercase and lowercase letter.
"""
import sys

__all__ = ['get_satellite']


class Satellite:
    @property
    def piperkev(self):
        raise NotImplementedError()


class Newton(Satellite):
    @property
    def piperkev(self):
        return None


class Nicer(Satellite):
    @property
    def piperkev(self):
        return 100


def get_satellite(name: str):
    sat_name = str(name).lower().capitalize()
    try:
        satellite_class = getattr(sys.modules[__name__], sat_name)
        return satellite_class()
    except AttributeError:
        raise ValueError("Invalid satellite name")
