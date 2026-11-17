import math

INCLUDED_ENTRIES = {"tourist": 1, "business": 3, "student": 2}
VALID_SPEEDS = ("normal", "express")


# ---------- validation helpers ----------
# Every invalid input is reported with ValueError, so callers only ever
# have to handle one documented exception type.

def _check_int(value, name, minimum=0):
    # bool is a subclass of int, so it must be rejected explicitly
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return value


def _check_bool(value, name):
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean")
    return value


def _check_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if isinstance(value, float) and math.isnan(value):
        raise ValueError(f"{name} must not be NaN")
    return value


# ---------- public API ----------

def visa_fee(visa_type, entries, speed, nationality_group):
    # isinstance check first: an unhashable value (e.g. a list) would
    # otherwise raise TypeError in the dict lookup
    if not isinstance(visa_type, str) or visa_type not in INCLUDED_ENTRIES:
        raise ValueError("unknown visa type")
    _check_int(entries, "entries")
    if not isinstance(speed, str) or speed not in VALID_SPEEDS:
        raise ValueError("unknown processing speed")
    if not isinstance(nationality_group, str):
        raise ValueError("nationality group must be a string")
    included = INCLUDED_ENTRIES[visa_type]
    if nationality_group == "A" and visa_type != "student":
        included += 1
    extra = entries - included
    if extra <= 0:
        return 0
    if speed == "express":
        rate = 100
    else:
        rate = 40
    if extra > 5:
        rate = rate + 20
        if speed == "express":
            rate += 10
    return extra * rate


def documents_complete(forms_filed, photos, is_renewal):
    _check_int(forms_filed, "forms_filed")
    _check_int(photos, "photos")
    _check_bool(is_renewal, "is_renewal")
    if is_renewal:
        return forms_filed >= 1
    if photos < 2:
        return False
    return forms_filed >= 3


def application_status(days_left, is_express, is_peak_season):
    # negative days_left is allowed (deadline passed -> "closed")
    _check_number(days_left, "days_left")
    _check_bool(is_express, "is_express")
    _check_bool(is_peak_season, "is_peak_season")
    if is_express:
        cutoff = 10
    else:
        cutoff = 30
    if is_peak_season:
        cutoff += 15
    if days_left >= cutoff:
        return "open"
    elif days_left >= cutoff - 15:
        return "closing"
    return "closed"