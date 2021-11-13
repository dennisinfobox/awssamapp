import json
import boto3
import botocore

CONFIG = botocore.config.Config(retries={'max_attempts': 0})


def get_lambda_client():
    return boto3.client(
        'lambda',
        aws_access_key_id='',
        aws_secret_access_key='',
        region_name='eu-west-2',
        endpoint_url='http://localhost:4574',
        config=CONFIG
    )


def get_step_functions_client():
    return boto3.client('stepfunctions', endpoint_url='http://localhost:4566')


def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id='',
        aws_secret_access_key='',
        region_name='',
        endpoint_url='http://localhost:4566'
    )


def get_dynamodb():
    dynamodb = boto3.client('dynamodb',
                            aws_access_key_id='',
                            aws_secret_access_key='',
                            region_name='us-east-1',
                            endpoint_url='http://localhost:4566')
    return dynamodb


def get_table():
    # print(os.environ['LOCALSTACK_HOSTNAME'])
    # print("################################################")
    dynamodb = boto3.resource(
        'dynamodb', region_name='us-east-1',
        endpoint_url='http://localhost:4566')
    # print(list(dynamodb.tables.all()))
    table = dynamodb.Table('eurlex_documents')
    return table


def delete_all_in_table():
    table = get_table()
    scan = table.scan()
    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(
                Key={
                    'cellarId': each['cellarId']
                }
            )


def read_all_from_tabel():
    table = get_table()
    response = table.scan()
    data = response['Items']
    return data


def invoke_function_and_get_message(function_name):
    lambda_client = get_lambda_client()
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse'
    )
    return json.loads(
        response['Payload']
        .read()
        .decode('utf-8')
    )


def create_bucket(bucket_name):
    s3_client = get_s3_client()
    s3_client.create_bucket(
        Bucket=bucket_name
    )


def list_s3_bucket_objects(bucket_name):
    s3_client = get_s3_client()
    items_list = s3_client.list_objects_v2(
        Bucket=bucket_name
    )

    if 'Contents' not in items_list:
        return []

    return items_list['Contents']


def delete_bucket(bucket_name):
    s3_client = get_s3_client()
    bucket_objects = list_s3_bucket_objects(bucket_name)
    a = [s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
         for obj in bucket_objects]
    print(a)
    s3_client.delete_bucket(
        Bucket=bucket_name
    )