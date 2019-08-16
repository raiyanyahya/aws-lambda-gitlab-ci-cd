from grabber import Invoker, JobStorageS3


def lambda_handler(event, context):
    assert_required(event)
    storage = JobStorageS3(event['bucket_name'])
    job = Invoker(storage)
    return job.grab()


def assert_required(event):
    if 'bucket_name' not in event:
        raise Exception("The 'bucket_name' key is missing from the event dictionary.")


if __name__ == '__main__':
    events = {
        "bucket_name": "aws-lambda-price-grabber"
    }

    result = lambda_handler(events, "")

    print(result)
