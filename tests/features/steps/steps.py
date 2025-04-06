from behave import given, when, then
from eshop import Product, ShoppingCart, Order

@given("The product has availability of {availability}")
def create_product(context, availability):
    context.product = Product(name="Test Product", price=100, available_amount=int(availability))

@given('An empty shopping cart')
def empty_cart(context):
    context.cart = ShoppingCart()

@then("Product is added to the cart successfully")
def add_successful(context):
    assert context.add_successfully == True

@then("Product is not added to cart successfully")
def add_failed(context):
    assert context.add_successfully == False

@given("A product with name {name}")
def create_named_product(context, name):
    context.product = Product(name=name, price=100, available_amount=10)

@given("An order with the cart")
def create_order(context):
    context.order = Order(context.cart)

@given("I create a product with price {price} and availability {availability}")
def create_product_with_price(context, price, availability):
    context.product = Product(name="Test Product", price=float(price), available_amount=int(availability))

@when("I check if {amount} items are available")
def check_availability(context, amount):
    context.result = context.product.is_available(int(amount))

@when("I add product to the cart in amount {amount}")
def add_product(context, amount):
    try:
        context.cart.add_product(context.product, int(amount))
        context.add_successfully = True
    except ValueError:
        context.add_successfully = False

@when("I add product to the cart with None amount")
def add_product_none(context):
    try:
        context.cart.add_product(context.product, None)
        context.add_successfully = True
    except (ValueError, TypeError):
        context.add_successfully = False

@when("I remove the product from the cart")
def remove_product(context):
    context.cart.remove_product(context.product)

@when("I calculate the total price")
def calculate_total(context):
    context.total = context.cart.calculate_total()

@when("I place the order")
def place_order(context):
    try:
        context.order.place_order()
        context.order_success = True
    except Exception:
        context.order_success = False

@when("I buy {amount} items of the product")
def buy_product(context, amount):
    context.product.buy(int(amount))

@when("I check the product price")
def check_price(context):
    context.price = context.product.price

@then("The product should not be available")
def check_not_available(context):
    assert context.result == False

@then("The product should be available")
def check_available(context):
    assert context.result == True

@then("The cart should be empty")
def check_cart_empty(context):
    assert len(context.cart.products) == 0

@then("The total price should be {total}")
def check_total(context, total):
    assert context.total == float(total)

@then("The order should be placed successfully")
def check_order_success(context):
    assert context.order_success == True

@then("The product should have {amount} items available")
def check_remaining_amount(context, amount):
    assert context.product.available_amount == int(amount)

@then("The product price should be {price}")
def check_product_price(context, price):
    assert context.price == float(price)