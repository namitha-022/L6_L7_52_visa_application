import pytest
from hypothesis import given, settings, strategies as st
from visa_application import (
    visa_fee, documents_complete, application_status, INCLUDED_ENTRIES,
)

# Example test cases (from the starter file):
def test_within_included_entries():
    assert visa_fee("tourist", 1, "normal", "B") == 0

def test_documents_complete():
    assert documents_complete(3, 2, False) is True


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------
# "Anything": junk of many types, to hit type-validation bugs.
anything = st.one_of(
    st.none(), st.booleans(), st.integers(), st.floats(allow_nan=True, allow_infinity=True),
    st.text(), st.binary(), st.lists(st.integers(), max_size=3),
    st.dictionaries(st.text(max_size=3), st.integers(), max_size=2),
)
visa_types = st.sampled_from(sorted(INCLUDED_ENTRIES))
speeds = st.sampled_from(["normal", "express"])
groups = st.sampled_from(["A", "B"]) | st.text(max_size=3)
entries_st = st.integers(min_value=0, max_value=10_000)
small_ints = st.integers(min_value=0, max_value=1_000)


def only_value_error(func, *args):
    """Property: a function either returns normally or raises ValueError.
    Any other exception (TypeError, AttributeError, ...) is a bug."""
    try:
        return func(*args)
    except ValueError:
        return None
    except Exception as e:  # noqa
        pytest.fail(f"{func.__name__}{args!r} crashed with {type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# 1. Crash / robustness fuzzing: arbitrary input, only ValueError allowed
# ---------------------------------------------------------------------------
@given(anything, anything, anything, anything)
def test_visa_fee_never_crashes(a, b, c, d):
    only_value_error(visa_fee, a, b, c, d)

@given(anything, anything, anything)
def test_documents_complete_never_crashes(a, b, c):
    only_value_error(documents_complete, a, b, c)

@given(anything, anything, anything)
def test_application_status_never_crashes(a, b, c):
    only_value_error(application_status, a, b, c)


# ---------------------------------------------------------------------------
# 2. Invalid input must be rejected (not silently accepted)
# ---------------------------------------------------------------------------
@given(st.text().filter(lambda s: s not in INCLUDED_ENTRIES), entries_st, speeds, groups)
def test_unknown_visa_type_rejected(v, e, s, g):
    with pytest.raises(ValueError):
        visa_fee(v, e, s, g)

@given(visa_types, st.integers(max_value=-1), speeds, groups)
def test_negative_entries_rejected(v, e, s, g):
    with pytest.raises(ValueError):
        visa_fee(v, e, s, g)

@given(visa_types, entries_st, st.text().filter(lambda s: s not in ("normal", "express")), groups)
def test_unknown_speed_rejected(v, e, s, g):
    with pytest.raises(ValueError):
        visa_fee(v, e, s, g)

@given(visa_types, st.floats() | st.booleans() | st.none() | st.text(), speeds, groups)
def test_non_integer_entries_rejected(v, e, s, g):
    with pytest.raises(ValueError):
        visa_fee(v, e, s, g)

@given(st.none() | st.floats() | st.booleans() | st.text(), small_ints, st.booleans())
def test_documents_non_integer_forms_rejected(f, p, r):
    with pytest.raises(ValueError):
        documents_complete(f, p, r)

@given(small_ints, small_ints, st.none() | st.integers() | st.text())
def test_documents_non_bool_renewal_rejected(f, p, r):
    with pytest.raises(ValueError):
        documents_complete(f, p, r)

@given(st.integers(max_value=-1), small_ints, st.booleans())
def test_documents_negative_forms_rejected(f, p, r):
    with pytest.raises(ValueError):
        documents_complete(f, p, r)

def test_status_nan_rejected():
    with pytest.raises(ValueError):
        application_status(float("nan"), False, False)

@given(st.none() | st.text() | st.booleans(), st.booleans(), st.booleans())
def test_status_non_numeric_days_rejected(d, e, p):
    with pytest.raises(ValueError):
        application_status(d, e, p)

@given(st.integers(), st.none() | st.integers() | st.text(), st.booleans())
def test_status_non_bool_express_rejected(d, e, p):
    with pytest.raises(ValueError):
        application_status(d, e, p)


# ---------------------------------------------------------------------------
# 3. Properties of valid input
# ---------------------------------------------------------------------------
@given(visa_types, entries_st, speeds, groups)
def test_fee_is_non_negative_int(v, e, s, g):
    fee = visa_fee(v, e, s, g)
    assert type(fee) is int and fee >= 0

@given(visa_types, st.integers(min_value=0, max_value=1), speeds, groups)
def test_fee_zero_within_included_entries(v, e, s, g):
    # every visa type includes at least 1 entry
    assert visa_fee(v, e, s, g) == 0

@given(visa_types, entries_st, groups)
def test_express_never_cheaper_than_normal(v, e, g):
    assert visa_fee(v, e, "express", g) >= visa_fee(v, e, "normal", g)

@given(visa_types, entries_st, speeds, groups)
def test_fee_monotonic_in_entries(v, e, s, g):
    assert visa_fee(v, e + 1, s, g) >= visa_fee(v, e, s, g)

@given(entries_st, speeds)
def test_group_a_never_pays_more_than_b(e, s):
    for v in INCLUDED_ENTRIES:
        assert visa_fee(v, e, s, "A") <= visa_fee(v, e, s, "B")

@given(small_ints, small_ints)
def test_renewal_only_needs_one_form(f, p):
    assert documents_complete(f, p, True) is (f >= 1)

@given(small_ints, small_ints)
def test_new_application_rule(f, p):
    assert documents_complete(f, p, False) is (p >= 2 and f >= 3)

@given(st.integers() | st.floats(allow_nan=False), st.booleans(), st.booleans())
def test_status_returns_known_value(d, e, p):
    assert application_status(d, e, p) in {"open", "closing", "closed"}

@given(st.integers(-1000, 1000), st.integers(0, 1000), st.booleans(), st.booleans())
def test_status_monotonic_in_days(d, extra, e, p):
    order = {"closed": 0, "closing": 1, "open": 2}
    assert order[application_status(d + extra, e, p)] >= order[application_status(d, e, p)]

@given(st.integers(-1000, 1000), st.booleans())
def test_peak_season_never_more_open(d, e):
    order = {"closed": 0, "closing": 1, "open": 2}
    assert order[application_status(d, e, True)] <= order[application_status(d, e, False)]