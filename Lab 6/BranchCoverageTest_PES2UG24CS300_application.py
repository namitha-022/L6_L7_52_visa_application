
import pytest
from visa_application import visa_fee, documents_complete, application_status


# VISA FEE BRANCH TESTS

def test_invalid_visa():
    with pytest.raises(ValueError):
        visa_fee("work", 2, "normal", "B")


def test_valid_visa():
    assert visa_fee("tourist", 1, "normal", "B") == 0


def test_negative_entries():
    with pytest.raises(ValueError):
        visa_fee("tourist", -1, "normal", "B")


def test_valid_entries():
    assert visa_fee("tourist", 2, "normal", "B") == 40


def test_nationality_a_non_student():
    assert visa_fee("tourist", 3, "normal", "A") == 40


def test_nationality_a_student():
    assert visa_fee("student", 3, "normal", "A") == 40


def test_nationality_b():
    assert visa_fee("tourist", 3, "normal", "B") == 80


def test_normal_speed():
    assert visa_fee("tourist", 3, "normal", "B") == 80


def test_express_speed():
    assert visa_fee("tourist", 3, "express", "B") == 200


def test_extra_entries_exactly_five():
    assert visa_fee("tourist", 6, "normal", "B") == 200


def test_extra_entries_above_five_normal():
    assert visa_fee("tourist", 7, "normal", "B") == 360


def test_extra_entries_above_five_express():
    assert visa_fee("tourist", 7, "express", "B") == 780


# DOCUMENT COMPLETION BRANCH TESTS

def test_renewal_with_forms():
    assert documents_complete(1, 0, True) is True


def test_renewal_without_forms():
    assert documents_complete(0, 0, True) is False


def test_new_application_insufficient_photos():
    assert documents_complete(3, 1, False) is False


def test_new_application_sufficient_photos():
    assert documents_complete(3, 2, False) is True


def test_new_application_insufficient_forms():
    assert documents_complete(2, 2, False) is False


# APPLICATION STATUS BRANCH TESTS

def test_normal_non_peak_open():
    assert application_status(30, False, False) == "open"


def test_normal_non_peak_closing():
    assert application_status(20, False, False) == "closing"


def test_normal_non_peak_closed():
    assert application_status(14, False, False) == "closed"


def test_express_non_peak():
    assert application_status(10, True, False) == "open"


def test_peak_season_open():
    assert application_status(45, False, True) == "open"


def test_peak_season_closing():
    assert application_status(35, False, True) == "closing"


def test_express_peak_season_closed():
    assert application_status(9, True, True) == "closed"
