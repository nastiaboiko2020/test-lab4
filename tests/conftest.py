import boto3
import pytest
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_TABLE, SHIPPING_QUEUE


@pytest.fixture(scope="session", autouse=True)
def setup_localstack_resources():
    dynamo_client = boto3.client(
        "dynamodb",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    print("Creating DynamoDB table...")
    existing_tables = dynamo_client.list_tables()["TableNames"]
    if SHIPPING_TABLE not in existing_tables:
        dynamo_client.create_table(
            TableName=SHIPPING_TABLE,
            KeySchema=[
                {"AttributeName": "shipping_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "shipping_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        dynamo_client.get_waiter("table_exists").wait(TableName=SHIPPING_TABLE)
    print("Table ShippingTable created successfully.")

    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    print("Creating SQS queue...")
    try:
        queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    except sqs_client.exceptions.QueueDoesNotExist:
        queue_url = sqs_client.create_queue(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    print(f"Queue ShippingQueue created at {queue_url}")

    yield

    print("Cleaning up resources...")
    dynamo_client.delete_table(TableName=SHIPPING_TABLE)
    sqs_client.delete_queue(QueueUrl=queue_url)


@pytest.fixture(autouse=True)
def purge_sqs_queue():
    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    sqs_client.purge_queue(QueueUrl=queue_url)


@pytest.fixture
def dynamo_resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )