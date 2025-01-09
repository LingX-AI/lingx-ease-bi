from enum import Enum


class ModelFieldEnum(Enum):
    """
    Enum for Django model field choices
    """

    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj

    @classmethod
    def choices(cls):
        return [(key.value, key.label) for key in cls]
