# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Config:
    def __init__(self, data: dict):
        self.data = data

    def get(self, key: str, default=None):
        if key in self.data:
            return self.data[key]
        else:
            return default

    def __getitem__(self, key: str):
        return self.data[key]

    def __str__(self):
        return f"[Config Wrapper: {str(self.data)}]"
