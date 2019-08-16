import unittest
from source.grabber import LogStorageS3
import boto3


class TestLogsStorageS3(unittest.TestCase):
    S3_BUCKET = "raiyan-lambda"
    TEST_FILE = "integration-test.txt"

    def setUp(self):
        self.storage = LogStorageS3(self.S3_BUCKET)

    def tearDown(self):
        self.delete_object()

    def test_create_object(self):
        value1 = "dog"
        value2 = "cat"
        value3 = "mouse"
        value4 = "snake"
        logs = [value1, value2, value3]

        self.storage.save(self.TEST_FILE, logs)

        result = self.storage.load(self.TEST_FILE)

        self.assertIn(value1, result)
        self.assertIn(value2, result)
        self.assertIn(value3, result)
        self.assertNotIn(value4, result)

    def delete_object(self):
        s3 = boto3.resource('s3')
        obj = s3.Object(self.S3_BUCKET, self.TEST_FILE)
        obj.delete()
