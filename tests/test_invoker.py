import unittest
from source.grabber import Invoker, JobStorageOS
from mock import patch
import json

class TestInvokerMethods(unittest.TestCase):
    STORAGE_PATH = "./tests/test-data/"

    def _ctor_invoker(self):
        """
        construct Crawler class
        """

        storage = JobStorageOS(self.STORAGE_PATH)
        return Invoker(storage)

    def test_load_local_get_website_monitor_list(self):
        grabber = self._ctor_invoker()
        yml_data = grabber.get_website_monitor_list()

        # a comprehensive test of the yml data is done in test_website_monitor_list.py

        self.assertTrue(yml_data['sites'] is not None, 'Missing sites dictionary listing the sites.')

        for site in yml_data['sites']:
            self.assertTrue(site['job_name'] is not None, 'Missing job_name')

    def test_invoker_returns_jobs_with_a_result(self):
        lambda_result = "none"
        success = "200"

        with patch.object(Invoker, '_invoke_lambda', return_value=lambda_result), \
                patch.object(Invoker, '_decode_status_code', return_value=success):
            grabber = self._ctor_invoker()

            result = grabber.grab()

            test_result = json.loads(result)

            for item in test_result:
                self.assertTrue(item['job_name'] is not None, 'Missing job_name')
                self.assertEqual(item['status'], "200", 'Missing status')
