import os
import time
from tests.integration import mytestutils


def run_step_function(dates_range):
    step_func_client = mytestutils.get_step_functions_client()
    arn = step_func_client.list_state_machines(
    )['stateMachines'][0]['stateMachineArn']
    execution_arn = step_func_client.start_execution(
        stateMachineArn=arn, input=dates_range)["executionArn"]
    counter = 60
    is_failed = False
    while counter > 0:
        response = step_func_client.describe_execution(
            executionArn=execution_arn)
        print(response)
        if response["status"] == "FAILED":
            is_failed = True
        if response["status"] != "RUNNING":
            break
        time.sleep(1)
        counter = counter - 1
    return is_failed


def test_step_function():
    mytestutils.create_bucket('qa-bucket')
    is_failed_state = run_step_function(
     '{"startDate": "2020-10-22T04:11:17", "endDate": "2020-10-22T04:14:16"}')

    assert is_failed_state is False
    assert len(mytestutils.list_s3_bucket_objects('qa-bucket')) == 2
    assert len(mytestutils.read_all_from_tabel()) == 2

    mytestutils.delete_all_in_table()
    mytestutils.delete_bucket('qa-bucket')

    mytestutils.create_bucket('qa-bucket')
    is_failed_state = run_step_function('{}')

    assert is_failed_state is True
    assert len(mytestutils.read_all_from_tabel()) == 0
    assert len(mytestutils.list_s3_bucket_objects('qa-bucket')) == 0
    stream = os.popen(
      'docker logs --tail 10 localstack_main | \
      grep "Request failed with status code 400" | wc -l')
    ocurrencies = stream.read()
    assert int(ocurrencies) > 0

    mytestutils.delete_all_in_table()
    mytestutils.delete_bucket('qa-bucket')
