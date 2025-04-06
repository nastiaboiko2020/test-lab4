import uuid
import boto3
from app.eshop import Product, ShoppingCart, Order
import random
from services import ShippingService
from services.repository import ShippingRepository
from services.publisher import ShippingPublisher
from datetime import datetime, timedelta, timezone
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE
import pytest

# Початкові тести
@pytest.mark.parametrize("order_id, shipping_id", [
    ("order_1", "shipping_1"),
    ("order_i2hur2937r9", "shipping_1!!!!"),
    (8662354, 123456),
    (str(uuid.uuid4()), str(uuid.uuid4()))
])
def test_place_order_with_mocked_repo(mocker, order_id, shipping_id):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    # Мокуємо сам метод create_shipping у shipping_service
    mocker.patch.object(shipping_service, "create_shipping", return_value=shipping_id)

    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )

    order = Order(cart, shipping_service, order_id)
    due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
    actual_shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=due_date
    )

    assert actual_shipping_id == shipping_id, "Actual shipping id must be equal to mock return value"

    shipping_service.create_shipping.assert_called_with(
        shipping_type=ShippingService.list_available_shipping_type()[0],
        product_ids=["Product"],
        order_id=order_id,
        due_date=due_date
    )

def test_place_order_with_unavailable_shipping_type_fails(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service)
    shipping_id = None

    with pytest.raises(ValueError) as excinfo:
        shipping_id = order.place_order(
            "Новий тип доставки",
            due_date=datetime.now(timezone.utc) + timedelta(seconds=3)
        )
    assert shipping_id is None, "Shipping id must not be assigned"
    assert "Shipping type is not available" in str(excinfo.value)

def test_when_place_order_then_shipping_in_queue(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()

    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )

    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    messages = response.get("Messages", [])
    assert len(messages) == 1, "Expected 1 SQS message"

    body = messages[0]["Body"]
    assert shipping_id == body

# Нові тести
# 1. Перевірка, що статус доставки оновлюється до "in progress" після створення
def test_create_shipping_updates_status_to_in_progress(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    status = shipping_service.check_status(shipping_id)
    assert status == shipping_service.SHIPPING_IN_PROGRESS

# 2. Перевірка, що доставка завершується успішно, якщо дата ще не минула
def test_process_shipping_completes_if_due_date_not_passed(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    shipping_service.process_shipping(shipping_id)
    status = shipping_service.check_status(shipping_id)
    assert status == shipping_service.SHIPPING_COMPLETED

# 3. Перевірка, що доставка провалюється, якщо дата минула
def test_process_shipping_fails_if_due_date_passed(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) - timedelta(seconds=1)
    )

    shipping_service.process_shipping(shipping_id)
    status = shipping_service.check_status(shipping_id)
    assert status == shipping_service.SHIPPING_FAILED

# 4. Перевірка, що кілька доставок обробляються коректно через чергу
def test_process_shipping_batch_with_multiple_orders(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart1 = ShoppingCart()
    cart1.add_product(Product(
        available_amount=10,
        name='Product1',
        price=random.random() * 10000),
        amount=5
    )
    cart2 = ShoppingCart()
    cart2.add_product(Product(
        available_amount=10,
        name='Product2',
        price=random.random() * 10000),
        amount=3
    )

    order1 = Order(cart1, shipping_service)
    order2 = Order(cart2, shipping_service)
    shipping_id1 = order1.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )
    shipping_id2 = order2.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    results = shipping_service.process_shipping_batch()
    # Перевіряємо, що в результатах є 2 shipping_id
    assert len([result["shipping_id"] for result in results]) == 2
    assert shipping_service.check_status(shipping_id1) == shipping_service.SHIPPING_COMPLETED
    assert shipping_service.check_status(shipping_id2) == shipping_service.SHIPPING_COMPLETED

# 5. Перевірка, що порожня черга повертає порожній список
def test_poll_shipping_with_empty_queue(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    messages = shipping_service.publisher.poll_shipping()
    assert messages == []

# 6. Перевірка, що створення доставки з порожнім списком продуктів працює
def test_create_shipping_with_empty_product_list(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    assert shipping_id is not None
    assert shipping_service.check_status(shipping_id) == shipping_service.SHIPPING_IN_PROGRESS

# 7. Перевірка, що статус доставки можна перевірити після створення
def test_check_status_after_creation(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    status = shipping_service.check_status(shipping_id)
    assert status == shipping_service.SHIPPING_IN_PROGRESS

# 8. Перевірка, що доставка не обробляється, якщо її немає в черзі
def test_process_shipping_batch_with_no_messages(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    results = shipping_service.process_shipping_batch()
    assert results == []

# 9. Перевірка, що створення доставки з моками повертає коректний статус
def test_create_shipping_with_mocked_publisher(mocker, dynamo_resource):
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(ShippingRepository(), mock_publisher)
    mock_publisher.send_new_shipping.return_value = "mock_message_id"

    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    assert shipping_service.check_status(shipping_id) == shipping_service.SHIPPING_IN_PROGRESS
    mock_publisher.send_new_shipping.assert_called_with(shipping_id)