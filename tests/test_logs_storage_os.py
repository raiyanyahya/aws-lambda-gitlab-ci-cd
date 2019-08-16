import unittest
from source.grabber import LogStorageOS
import os


class TestLogsStorageOS(unittest.TestCase):
    STORAGE_PATH = "./tests/test-data/"
    TEST_FILE = "integration-test.txt"

    def setUp(self):
        self.storage = LogStorageOS(self.STORAGE_PATH)

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
        os.remove(self.STORAGE_PATH + self.TEST_FILE)
