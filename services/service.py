import uuid
from datetime import datetime, timezone
from typing import List


class ShippingService:
    SHIPPING_CREATED = "created"
    SHIPPING_IN_PROGRESS = "in_progress"
    SHIPPING_COMPLETED = "completed"
    SHIPPING_FAILED = "failed"

    def __init__(self, repository, publisher):
        self.repository = repository
        self.publisher = publisher

    @staticmethod
    def list_available_shipping_type() -> List[str]:
        return ["Нова Пошта", "Укрпошта"]

    def create_shipping(self, shipping_type: str, product_ids: List[str], order_id: str, due_date: datetime, shipping_id: str = None) -> str:
        if shipping_id is None:
            shipping_id = str(uuid.uuid4())
        self.repository.create_shipping(
            shipping_id=shipping_id,
            shipping_type=shipping_type,
            product_ids=product_ids,
            order_id=order_id,
            status=self.SHIPPING_CREATED,
            due_date=due_date
        )
        self.repository.update_status(shipping_id, self.SHIPPING_IN_PROGRESS)
        self.publisher.send_new_shipping(shipping_id)
        return shipping_id

    def check_status(self, shipping_id: str) -> str:
        return self.repository.get_status(shipping_id)

    def process_shipping(self, shipping_id: str):
        shipping = self.repository.get_shipping(shipping_id)
        due_date = shipping["due_date"]

        # Перевіряємо, чи due_date у минулому
        if due_date < datetime.now(timezone.utc):
            self.repository.update_status(shipping_id, self.SHIPPING_FAILED)
        else:
            self.repository.update_status(shipping_id, self.SHIPPING_COMPLETED)

    def process_shipping_batch(self) -> List[dict]:
        shipping_ids = self.publisher.poll_shipping()
        results = []
        for shipping_id in shipping_ids:
            self.process_shipping(shipping_id)
            results.append({"shipping_id": shipping_id})
        return results