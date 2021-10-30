import os
from unittest import mock

from moto import mock_dynamodb2

from functions.ingest_alert_filter.app import get_endpoint, get_dynamo_table_name
from tests.unit.conftest import setup_db

test_event = {'cellarId': '94a481c6-1298-11eb-9a54-01aa75ed71a1'}


@mock_dynamodb2
def test_lambda_handler_when_record_exists():
    eurlex_documents = setup_db(get_endpoint())
    eurlex_documents.put_item(Item=test_event)

    from functions.ingest_alert_filter.app import lambda_handler
    result = lambda_handler(event=test_event, context={})

    assert result['exists']


@mock_dynamodb2
def test_lambda_handler_when_record_not_exists():
    setup_db(get_endpoint())

    from functions.ingest_alert_filter.app import lambda_handler
    result = lambda_handler(event=test_event, context={})

    assert not result['exists']


def test_get_dynamo_table_name():
    assert get_dynamo_table_name() == "eurlex_documents"


def test_get_endpoint_when_localstack_is_none():
    assert get_endpoint() is None


@mock.patch.dict(os.environ, {"LOCALSTACK_HOSTNAME": "somehost"})
def test_get_endpoint_when_localstack_is_none():
    assert get_endpoint() == "http://somehost:4566"
