import os
import pytest
import boto3


def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"



def setup_db(ep):
    aws_credentials()
    print("In setup db")
    print(os.getenv("AWS_DEFAULT_REGION"))
    dynamodb = boto3.resource('dynamodb')
    table_name = 'eurlex_documents'
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{'AttributeName': 'cellarId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'cellarId', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )

    return dynamodb.Table(table_name)
