#!/usr/bin/python
"""
Base class format for all importable transactions to standardize processing between different
importable files
"""


class ImportRecord:
    """my doc is my string, verify me"""

    # This isnt currently used. given the native support for pandas in PyQt6 this may not be needed
    #  but I will need to test further
    account = ""
    charge_name = ""
    transaction_date = ""
    post_date = ""
    amount = 0
    category_tag = ""
    notes = ""

    def __init__(self, *args, **kwargs):
        self.name = __name__
        for name, value in kwargs.items():
            setattr(self, name, value)
        self.transaction_date = self.transaction_date or self.post_date

    def __str__(self):
        return self.name
