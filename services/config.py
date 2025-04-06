import os

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SHIPPING_TABLE = os.getenv("SHIPPING_TABLE", "ShippingTable")
SHIPPING_QUEUE = os.getenv("SHIPPING_QUEUE", "ShippingQueue")