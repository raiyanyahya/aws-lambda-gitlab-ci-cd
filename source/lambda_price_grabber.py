from grabber import Crawler, LogStorageS3
import json


def lambda_handler(event, context):
    assert_required(event)
    storage = LogStorageS3(event['bucket_name'])
    web = Crawler(storage)
    price = web.grab_price(event['job_name'], event['site_url'], event['html_query'])
    return json.dumps({'site_url': event['site_url'], 'price': price})


def assert_required(event):
    if 'bucket_name' not in event:
        raise Exception("The 'bucket_name' key is missing from the event dictionary.")
    if 'job_name' not in event:
        raise Exception("The 'job_name' key is missing from the event dictionary.")
    if 'site_url' not in event:
        raise Exception("The 'site_url' key is missing from the event dictionary.")
    if 'html_query' not in event:
        raise Exception("The 'html_query' key is missing from the event dictionary.")


if __name__ == '__main__':
    events = {
        "job_name": "test",
        "site_url": "https://www.amazon.com/tshirt.html",
        "html_query": "//div[contains(@class, 'h-product-price')]/div/text()",
        "bucket_name": "aws-lambda-price-grabber"
    }

    result = lambda_handler(events, "")

    print(result)
