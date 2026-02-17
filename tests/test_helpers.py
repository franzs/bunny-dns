"""Tests for internal helper functions."""

from datetime import datetime, timezone

from bunnydns._helpers import _parse_dt


class TestParseDt:
    def test_none(self):
        assert _parse_dt(None) is None

    def test_already_datetime(self):
        dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert _parse_dt(dt) is dt

    def test_iso_format_with_z(self):
        result = _parse_dt("2024-01-15T10:30:00Z")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30

    def test_iso_format_with_offset(self):
        result = _parse_dt("2024-01-15T10:30:00+00:00")
        assert result is not None
        assert result.year == 2024

    def test_iso_format_with_milliseconds(self):
        result = _parse_dt("2024-01-15T10:30:00.123Z")
        assert result is not None
        assert result.year == 2024
