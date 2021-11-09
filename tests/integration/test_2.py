import time
from unittest import TestCase
from tests.integration import mytestutils

class Test2(TestCase):    

    @classmethod
    def setup_class(cls):        
        print('\r\nSetting up the class')        
        mytestutils.create_bucket('qa-bucket')
        step_func_client = mytestutils.get_step_functions_client()
        arn = step_func_client.list_state_machines()['stateMachines'][0]['stateMachineArn']
        execution_arn = step_func_client.start_execution(stateMachineArn=arn,input='{}')["executionArn"]
        counter = 60
        while counter > 0:
            response = step_func_client.describe_execution(executionArn=execution_arn)
            if response["status"] != "RUNNING":
                break
            time.sleep(1)
            counter = counter - 1

    @classmethod
    def teardown_class(cls):
        print('\r\nTearing down the class')
        mytestutils.delete_all_in_table()
        mytestutils.delete_bucket('qa-bucket')

    def test_that_two_objects_in_s3(self):
        bucket_objects = mytestutils.list_s3_bucket_objects('qa-bucket')
        self.assertEqual(len(bucket_objects), 0)

    def test_that_two_records_in_table(self):
        table = mytestutils.get_table()
        response = table.scan()
        data = response['Items']        
        self.assertEqual(len(data), 0) 
        