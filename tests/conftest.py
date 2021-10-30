import os
from unittest import mock

import boto3


@mock.patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "testing",
                              "AWS_SECRET_ACCESS_KEY": "testing",
                              "AWS_SESSION_TOKEN": "testing",
                              "AWS_SECURITY_TOKEN": "testing"})
def aws_credentials():
    """Mocked AWS Credentials for moto."""


def setup_db(ep):
    dynamodb = boto3.resource('dynamodb', ep)
    table_name = 'eurlex_documents'
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{'AttributeName': 'cellarId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'cellarId', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )

    return dynamodb.Table(table_name)
