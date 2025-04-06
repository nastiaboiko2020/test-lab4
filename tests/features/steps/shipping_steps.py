from behave import given, when, then
from services.service import ShippingService
@given('a shipping service')
def step_given_shipping_service(context):
    context.service = ShippingService()
@when('I create a shipping order with order_id "{order_id}", user_id "{user_id}", and address "{address}"')
def step_when_create_shipping(context, order_id, user_id, address):
    context.shipping = context.service.create_shipping(order_id, user_id, address)
@then('the shipping order should have order_id "{order_id}", user_id "{user_id}", and address "{address}"')
def step_then_check_shipping(context, order_id, user_id, address):
    assert context.shipping["order_id"] == order_id
    assert context.shipping["user_id"] == user_id
    assert context.shipping["address"] == address
