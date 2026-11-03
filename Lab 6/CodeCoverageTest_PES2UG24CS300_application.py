
import pytest
from visa_application import visa_fee, documents_complete, application_status


# Visa fee tests

def test_unknown_visa():
    with pytest.raises(ValueError):
        visa_fee("work", 2, "normal", "B")


def test_negative_entries():
    with pytest.raises(ValueError):
        visa_fee("tourist", -1, "normal", "B")


def test_included_entries():
    assert visa_fee("tourist", 1, "normal", "B") == 0


def test_nationality_group_a():
    assert visa_fee("tourist", 3, "normal", "A") == 40


def test_student_group_a():
    assert visa_fee("student", 3, "normal", "A") == 40


def test_express_fee():
    assert visa_fee("tourist", 3, "express", "B") == 200


def test_normal_fee():
    assert visa_fee("tourist", 3, "normal", "B") == 80


def test_extra_entries_normal():
    assert visa_fee("tourist", 7, "normal", "B") == 360


def test_extra_entries_express():
    assert visa_fee("tourist", 7, "express", "B") == 780


# Document completion tests

def test_renewal_complete():
    assert documents_complete(1, 0, True) is True


def test_renewal_incomplete():
    assert documents_complete(0, 0, True) is False


def test_insufficient_photos():
    assert documents_complete(3, 1, False) is False


def test_complete_documents():
    assert documents_complete(3, 2, False) is True


def test_insufficient_forms():
    assert documents_complete(2, 2, False) is False


# Application status tests

def test_application_open():
    assert application_status(30, False, False) == "open"


def test_application_closing():
    assert application_status(20, False, False) == "closing"


def test_application_closed():
    assert application_status(10, False, False) == "closed"


def test_express_peak_season():
    assert application_status(20, True, True) == "closing"
