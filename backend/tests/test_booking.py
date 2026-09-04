from app.booking import book_site_visit

def test_booking_success():
    result = book_site_visit("Saturday", "11:00 AM")
    assert result["success"] is True
    assert result["date"] == "Saturday"
    assert result["time"] == "11:00 AM"
    assert "booking_id" in result
    assert result["booking_id"].startswith("NS-")

def test_booking_failure():
    result = book_site_visit("Monday", "11:00 AM")
    assert result["success"] is False
    assert result["error"] == "slot_unavailable"
    assert "alternatives" in result
    assert "Saturday 11:00 AM" in result["alternatives"]
