from unittest.mock import patch

import requests
from moto import mock_dynamodb2, mock_s3
import os
from unittest import mock
import boto3

from tests.conftest import setup_db, aws_credentials
from functions.ingest_metadata_downloader.app import get_endpoints, get_dyname_table_name, get_s3_bucket_name, \
    upload_content, lambda_handler

aws_credentials()


def setup_aws():
    setup_db(None)
    s3_client = boto3.client('s3', "us-east-1")
    s3_client.create_bucket(Bucket='notices-bucket')


def setup_bucket():
    s3_client = boto3.client('s3', "us-east-1")

    bucket_name = get_s3_bucket_name()
    s3_client.create_bucket(Bucket=bucket_name)

    return s3_client


@mock_s3
@mock_dynamodb2
@mock.patch.dict(get_endpoints(), {"aws": None})
@patch('functions.ingest_metadata_downloader.app.requests.get')
def test_lambda_handler(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = "fake content"
    setup_aws()

    result = lambda_handler({'cellarId': '94a481c6-1298-11eb-9a54-01aa75ed71a1'}, "")

    assert result['downloaded']


@mock_s3
@mock_dynamodb2
@mock.patch.dict(get_endpoints(), {"aws": None})
@patch('functions.ingest_metadata_downloader.app.requests.get')
def test_lambda_handler_when_exception_raised(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError()
    setup_aws()

    result = lambda_handler({'cellarId': '94a481c6-1298-11eb-9a54-01aa75ed71a1'}, "")

    assert not result['downloaded']


@mock_s3
@mock.patch.dict(get_endpoints(), {"aws": None})
def test_upload_content():
    s3_client = setup_bucket()

    cellar_id = "testcelarid"
    upload_content("", cellar_id)
    object_key = f'notice_{cellar_id}.xml'
    bucket_name = get_s3_bucket_name()
    response = s3_client.list_objects(Bucket=bucket_name, Prefix=object_key)

    assert response['Contents'][0]['Key'] == object_key


@mock_s3
@mock.patch.dict(get_endpoints(), {"aws": None})
def test_upload_content_when_item_exists():
    s3_client = setup_bucket()
    cellar_id = "testcelarid"
    object_key = f'notice_{cellar_id}.xml'
    s3_client.put_object(Bucket=get_s3_bucket_name(), Key=object_key, Body="some fake")

    upload_content("", cellar_id)

    response = s3_client.list_objects(Bucket=get_s3_bucket_name(), Prefix=object_key)

    assert response['Contents'][0]['Key'] == object_key


@mock_dynamodb2
def test_save_record():
    table = setup_db(None)
    test_doc_name = "test"
    from functions.ingest_metadata_downloader.app import save_record
    save_record(test_doc_name)

    response = table.get_item(Key={
        'cellarId': test_doc_name
    })

    assert response['Item']['cellarId'] == test_doc_name


def test_get_s3_bucket_name():
    assert get_s3_bucket_name() == "notices-bucket"


def test_get_dyname_table_name():
    assert get_dyname_table_name() == "eurlex_documents"


@mock.patch.dict(os.environ, {"LOCALSTACK_HOSTNAME": "somehost"})
def test_get_endpoints():
    assert get_endpoints() == {"aws": "http://somehost:4566", "notice": "https://eur-lex.europa.eu"}
