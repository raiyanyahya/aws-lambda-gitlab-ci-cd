import unittest
from source.grabber import Log, LogStorageOS, LAST_EXECUTED_FILENAME
import random
import os
import json


class TestLogger(unittest.TestCase):
    STORAGE_PATH = "./tests/test-data/"
    LOGFILE_LAST_EXECUTED = STORAGE_PATH + LAST_EXECUTED_FILENAME

    def _ctor_logger(self):
        """construct Log class"""
        storage = LogStorageOS(self.STORAGE_PATH)
        return Log(storage)

    # def tearDown(self):
        # self._delete(self.LOGFILE_LAST_EXECUTED)

    def test_create_last_executed_log(self):
        if not Log.FEATURE_ENABLED:
            return

        logfile = self.LOGFILE_LAST_EXECUTED

        self._delete(logfile)

        log = self._ctor_logger()

        price = round(self.rand_float_range(80, 100), 2)
        job_name = "december"
        log.latest_execution(job_name, str(price))

        exists = os.path.isfile(logfile)

        self.assertTrue(exists, "Log file '" + logfile + "' was not created")
        self.assertTrue(str(price) in open(logfile).read(), "Couldn't find price '" + str(price) + "' in log file")
        self.assertTrue(job_name in open(logfile).read(), "Couldn't find job_name '" + job_name + "' in log file")

        with open(logfile, 'r') as fp:
            jobs = json.load(fp)
            self.assertIsNotNone(jobs)

    def test_update_last_executed_log(self):
        if not Log.FEATURE_ENABLED:
            return

        logfile = self.LOGFILE_LAST_EXECUTED

        self.test_create_last_executed_log()

        log = self._ctor_logger()

        price = round(self.rand_float_range(80, 100), 2)
        job_name = "december"
        log.latest_execution(job_name, str(price))

        exists = os.path.isfile(logfile)

        self.assertTrue(exists, "Log file '" + logfile + "' was not created")
        self.assertTrue(str(price) in open(logfile).read(), "Couldn't find price '" + str(price) + "' in log file")
        self.assertTrue(job_name in open(logfile).read(), "Couldn't find job_name '" + job_name + "' in log file")

        with open(logfile, 'r') as fp:
            jobs = json.load(fp)
            self.assertIsNotNone(jobs)

    def test_edit_two_last_executed_logs(self):
        if not Log.FEATURE_ENABLED:
            return

        logfile = self.LOGFILE_LAST_EXECUTED

        self._delete(logfile)

        log = self._ctor_logger()

        # Create log entries

        price1 = round(self.rand_float_range(80, 100), 2)
        job_name1 = "december"
        log.latest_execution(job_name1, str(price1))

        price2 = round(self.rand_float_range(80, 100), 2)
        job_name2 = "january"
        log.latest_execution(job_name2, str(price2))

        exists = os.path.isfile(logfile)

        # Ensure they were created

        self.assertTrue(exists, "Log file '" + logfile + "' was not created")
        self.assertTrue(str(price1) in open(logfile).read(), "Couldn't find price '" + str(price1) + "' in log file")
        self.assertTrue(job_name1 in open(logfile).read(), "Couldn't find job_name '" + job_name1 + "' in log file")
        self.assertTrue(str(price2) in open(logfile).read(), "Couldn't find price '" + str(price2) + "' in log file")
        self.assertTrue(job_name2 in open(logfile).read(), "Couldn't find job_name '" + job_name2 + "' in log file")

        # Update log entries

        price1 = round(self.rand_float_range(80, 100), 2)
        job_name1 = "december"
        log.latest_execution(job_name1, str(price1))

        price2 = round(self.rand_float_range(80, 100), 2)
        job_name2 = "january"
        log.latest_execution(job_name2, str(price2))

        self.assertTrue(str(price1) in open(logfile).read(), "Couldn't find price '" + str(price1) + "' in log file")
        self.assertTrue(job_name1 in open(logfile).read(), "Couldn't find job_name '" + job_name1 + "' in log file")
        self.assertTrue(str(price2) in open(logfile).read(), "Couldn't find price '" + str(price2) + "' in log file")
        self.assertTrue(job_name2 in open(logfile).read(), "Couldn't find job_name '" + job_name2 + "' in log file")

        with open(logfile, 'r') as fp:
            jobs = json.load(fp)
            self.assertIsNotNone(jobs)

    def test_job_price_log(self):
        if not Log.FEATURE_ENABLED:
            return

        log = self._ctor_logger()

        price1 = round(self.rand_float_range(80, 100), 2)
        log._append_to_job_log('white-tshirt', price1)

        price2 = round(self.rand_float_range(80, 100), 2)
        log._append_to_job_log('white-tshirt', price2)

    @staticmethod
    def _delete(logfile):
        if os.path.isfile(logfile):
            os.remove(logfile)

    @staticmethod
    def rand_float_range(start, end):
        return random.random() * (end - start) + start
