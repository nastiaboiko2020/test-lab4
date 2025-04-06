import pytest
from services.service import ShippingService
def test_create_shipping():
    service = ShippingService()
    shipping = service.create_shipping("order123", "user123", "address123")
    assert shipping["order_id"] == "order123"
    assert shipping["user_id"] == "user123"
    assert shipping["address"] == "address123"
