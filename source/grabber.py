"""Grabber web scrapper functions

"""
from abc import ABC, abstractmethod
from urllib.request import urlopen
import lxml.html
import re
import boto3
from botocore.exceptions import ClientError
from datetime import date, datetime
import json
import yaml
from pathlib import Path

JOBS_FILENAME: str = "website-monitor-list.yml"
LAST_EXECUTED_FILENAME: str = "job-last-executed.json"
AWS_REGION: str = "eu-central-1"

class AbstractLogStorage(ABC):
    """
    Log storage can be implemented for S3 or local hard disk (JSON files)
    """

    @abstractmethod
    def load(self, object_name: str) -> []:
        pass

    @abstractmethod
    def save(self, object_name: str, logs: []):
        pass

    @abstractmethod
    def check_exists(self, object_name: str) -> bool:
        pass


class AbstractJobsStorage(ABC):
    """
    Jobs can be loaded from S3 or local hard disk (YML files)
    """

    @abstractmethod
    def load(self, object_name: str) -> dict:
        pass


class Invoker(object):
    """
    Calls web crawler using the list found in the JOBS_FILENAME
    """

    def __init__(self, storage: AbstractJobsStorage):
        self.storage = storage

    def get_website_monitor_list(self):
        return self.storage.load(JOBS_FILENAME)

    def grab(self) -> str:
        """
        Grabs prices from websites listed in the yaml file. Returns json list if job_name and HTTP status code
        """
        website_list = self.get_website_monitor_list()
        result = []
        for site in website_list['sites']:
            events = {
                'job_name': site['job_name'],
                'site_url': site['site_url'],
                'html_query': site['html_query'],
                'bucket_name': site['bucket_name']
            }
            events_payload = json.dumps(events)
            response = self._invoke_lambda(events_payload)
            status = self._decode_status_code(response)
            job_status = {
                'job_name': site['job_name'],
                'status': status
            }
            result.append(job_status)
        return json.dumps(result)

    @staticmethod
    def _invoke_lambda(json_payload: str):
        client = boto3.client('lambda', region_name=AWS_REGION)
        return client.invoke(FunctionName='grab-price',
                             InvocationType='RequestResponse',
                             Payload=json_payload)

    @staticmethod
    def _decode_payload(response):
        return response['Payload'].read().decode("utf-8")

    @staticmethod
    def _decode_status_code(response):
        return response['StatusCode']


class Crawler(object):
    """
    Gets a web page, parses using the lxml query you give, logs execution/price and returns a price
    """

    def __init__(self, storage: AbstractLogStorage):
        self.storage = storage

    def grab_price(self, job_name, url, query):
        page = self.get_web_page(url)
        data = self.parse_html(page, query)
        price = self.parse_price(data)
        Log(self.storage).latest_execution(job_name, price)
        return price

    @staticmethod
    def get_web_page(url):
        response = urlopen(url)
        return response.read()

    @staticmethod
    def parse_html(page, find):
        doc = lxml.html.document_fromstring(page)
        result = doc.xpath(find)
        if len(result) != 1:
            raise Exception("Couldn't find string in HTML: " + find)
        return result[0]

    @staticmethod
    def parse_price(value):
        result = re.findall(r"\d+\.\d+", value)
        if len(result) != 1:
            raise Exception("Couldn't parse the price from value :" + value)
        return result[0]


class JobStorageS3(AbstractJobsStorage):
    """
    Load jobs from Amazon S3
    """

    def __init__(self, s3_bucket: str):
        self.s3_bucket = s3_bucket

    def load(self, object_name):
        s3 = boto3.resource('s3', region_name=AWS_REGION)
        obj = s3.Object(self.s3_bucket, object_name)
        stream = obj.get()['Body'].read().decode('utf-8')
        return yaml.load(stream)


class JobStorageOS(AbstractJobsStorage):
    """
    Load jobs from local hard disk
    """

    def __init__(self, filepath):
        self.filepath = filepath

    def load(self, object_name):
        with open(self.filepath + object_name, 'r') as logfile:
            return yaml.load(logfile)


class LogStorageS3(AbstractLogStorage):
    """
    Load and save logs to Amazon S3
    """

    def __init__(self, s3_bucket: str):
        self.s3_bucket = s3_bucket

    def load(self, object_name):
        if self.check_exists(object_name):
            s3 = boto3.resource('s3', region_name=AWS_REGION)
            obj = s3.Object(self.s3_bucket, object_name)
            stream = obj.get()['Body'].read().decode('utf-8')
            return json.loads(stream)
        return []

    def check_exists(self, object_name):
        s3 = boto3.resource('s3', region_name=AWS_REGION)
        try:
            s3.Object(self.s3_bucket, object_name).load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            raise

    def save(self, object_name, logs):
        s3 = boto3.resource('s3', region_name=AWS_REGION)
        obj = s3.Object(self.s3_bucket, object_name)
        obj.put(Body=json.dumps(logs))


class LogStorageOS(AbstractLogStorage):
    """
    Load and save logs to local hard disk
    """

    def __init__(self, filepath):
        self.filepath = filepath

    def load(self, object_name):
        if self.check_exists(object_name):
            with open(self.filepath + object_name, 'r') as logfile:
                return json.load(logfile)
        return []

    def check_exists(self, object_name):
        my_file = Path(self.filepath + object_name)
        return my_file.is_file()

    def save(self, object_name, logs):
        with open(self.filepath + object_name, 'w') as outfile:
            json.dump(logs, outfile)


class Log(object):
    """
    Stores latest execution information

    Note: The central log file is not supposed to be kept forever. You need to aggregate the data and empty it. If
    you don't, then your program will become slower and also cost more to run over the long term.
    """

    FEATURE_ENABLED = True  # can be removed once S3 bucket is integrated

    def __init__(self, storage: AbstractLogStorage):
        self.storage = storage

    def latest_execution(self, job_name, price):
        if not self.FEATURE_ENABLED:
            return
        self._append_to_job_log(job_name, price)  # each job gets its own file with price history
        self._update_central_job_log(job_name, price)  # goes into the LAST_EXECUTED_FILENAME

    def _append_to_job_log(self, job_name, price):
        log_file = job_name + ".json"
        jobs = self.storage.load(log_file)
        jobs.append(self._create_job_executed_log(price))
        self.storage.save(log_file, jobs)

    def _update_central_job_log(self, job_name, price):
        jobs = self.storage.load(LAST_EXECUTED_FILENAME)
        self._update(jobs, job_name, price)
        self.storage.save(LAST_EXECUTED_FILENAME, jobs)

    def _update(self, jobs, job_name, price):
        pos = self._find(jobs, 'job_name', job_name)
        if pos == -1:
            new_job = self._create_job_name_executed_log(job_name, price)
            jobs.append(new_job)
        else:
            data = jobs[pos]
            self._update_job_executed_log(data, price)

    def _create_job_name_executed_log(self, job_name, price) -> dict:
        return {'job_name': job_name, 'executed': self._json_serial(datetime.utcnow()), 'price': price}

    def _create_job_executed_log(self, price) -> dict:
        return {'executed': self._json_serial(datetime.utcnow()), 'price': price}

    def _update_job_executed_log(self, data, price):
        data['executed'] = self._json_serial(datetime.utcnow())
        data['price'] = price

    @staticmethod
    def _json_serial(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))

    @staticmethod
    def _find(job_list, key, value):
        if len(job_list) == 0:
            return -1
        for i, dic in enumerate(job_list):
            if dic[key] == value:
                return i
        return -1
