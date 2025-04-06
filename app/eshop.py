import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta


@dataclass
class Product:
    name: str
    price: float
    available_amount: int
    product_id: str = None  # Додаємо унікальний ідентифікатор

    def __post_init__(self):
        # Генеруємо product_id, якщо він не вказаний
        if self.product_id is None:
            self.product_id = str(uuid.uuid4())

    def buy(self, amount: int):
        if amount > self.available_amount:
            raise ValueError(f"Not enough {self.name} in stock")
        self.available_amount -= amount

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.product_id)

    def __eq__(self, other):
        if not isinstance(other, Product):
            return False
        return self.product_id == other.product_id


class ShoppingCart:
    def __init__(self):
        self.products = {}

    def add_product(self, product: Product, amount: int):
        if product.available_amount < amount:
            raise ValueError(f"Not enough {product.name} in stock")
        self.products[product] = amount

    def submit_cart_order(self):
        product_ids = []
        for product, count in self.products.items():
            product.buy(count)
            product_ids.append(str(product))
        self.products.clear()
        return product_ids


class Order:
    def __init__(self, cart: ShoppingCart, shipping_service, order_id: str = None):
        self.cart = cart
        self.order_id = order_id if order_id else str(uuid.uuid4())
        self.shipping_service = shipping_service

    def place_order(self, shipping_type: str, due_date: datetime = None):
        if due_date is None:
            due_date = datetime.now(timezone.utc) + timedelta(seconds=3)

        if shipping_type not in self.shipping_service.list_available_shipping_type():
            raise ValueError("Shipping type is not available")

        product_ids = self.cart.submit_cart_order()
        shipping_id = self.shipping_service.create_shipping(
            shipping_type=shipping_type,
            product_ids=product_ids,
            order_id=self.order_id,
            due_date=due_date
        )
        return shipping_id