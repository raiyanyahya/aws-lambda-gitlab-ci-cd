import unittest
from source.grabber import JobStorageOS, JOBS_FILENAME

class TestWebsiteMonitorList(unittest.TestCase):
    STORAGE_PATH = './source/'

    def test_load_local_jobs(self):
        storage = JobStorageOS(self.STORAGE_PATH)
        result = storage.load(JOBS_FILENAME)
        self.check_sites_information_valid(result)

    # A test for the jobs on s3 would could also be done. It would fail during development, so I have not included it.

    def check_sites_information_valid(self, yml_data: dict):
        self.assertTrue(yml_data['sites'] is not None, 'Missing sites dictionary listing the sites.')

        for site in yml_data['sites']:
            self.assertTrue(len(site) == 6)
            self.assertTrue(site['job_name'] is not None, 'Missing job_name')
            self.assertTrue(site['bucket_name'] is not None, 'Missing bucket_name')
            self.assertTrue(site['site_url'] is not None, 'Missing site_url')
            self.assertTrue(site['html_query'] is not None, 'Missing html_query')
            self.assertTrue(site['alert_whenever'] is not None, 'Missing alert_whenever')
            self.assertTrue(site['difference'] is not None, 'Missing difference')
