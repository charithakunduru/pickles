import enum

class PickleCategory(str, enum.Enum):
    VEG = "VEG"
    NON_VEG = "NON_VEG"
    SWEET = "SWEET"

class SpiceLevel(str, enum.Enum):
    MILD = "MILD"
    MEDIUM = "MEDIUM"
    SPICY = "SPICY"
    EXTRA_SPICY = "EXTRA_SPICY"
