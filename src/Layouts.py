import cython
import PySimpleGUI as sg

from .utils.random_data import random_data


cdef class Layouts:
    def __init__(self, data: dict[str, dict[str, str]]) -> None:
        """Init shared settings for the layouts."""
        sg.theme("Dark Gray 2")
