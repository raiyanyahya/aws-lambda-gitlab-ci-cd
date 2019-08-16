
## Deployment

can be created with cloud formation?

notification group with email
alarm when Errors >= 0 for 1 datapoints within 5 minutes
trigger-grabber every 2 hours with test data FunctionName = aws-lambda-price-grabber, Resource = aws-lambda-price-grabber

tag services being used

"Tags": [
                    {
                        "Key": "Environment",
                        "Value": {
                            "Ref": "Environment"
                        }
                    },
                    {
                        "Key": "Purpose",
                        "Value": "CustomerXYZ VPC"