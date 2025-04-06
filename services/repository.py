import boto3  # Додаємо імпорт boto3
from datetime import datetime
from typing import List
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_TABLE


class ShippingRepository:
    def __init__(self):
        self.table = self._get_table()

    def _get_table(self):
        dynamodb = boto3.resource(
            "dynamodb",
            endpoint_url=AWS_ENDPOINT_URL,
            region_name=AWS_REGION,
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )
        return dynamodb.Table(SHIPPING_TABLE)

    def create_shipping(
        self,
        shipping_id: str,
        shipping_type: str,
        product_ids: List[str],
        order_id: str,
        status: str,
        due_date: datetime,
    ):
        self.table.put_item(
            Item={
                "shipping_id": shipping_id,
                "shipping_type": shipping_type,
                "product_ids": product_ids,
                "order_id": order_id,
                "status": status,
                "due_date": due_date.isoformat(),
            }
        )

    def get_status(self, shipping_id: str) -> str:
        response = self.table.get_item(Key={"shipping_id": shipping_id})
        return response["Item"]["status"]

    def get_shipping(self, shipping_id: str) -> dict:
        response = self.table.get_item(Key={"shipping_id": shipping_id})
        item = response["Item"]
        item["due_date"] = datetime.fromisoformat(item["due_date"])
        return item

    def update_status(self, shipping_id: str, status: str):
        self.table.update_item(
            Key={"shipping_id": shipping_id},
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": status},
        )