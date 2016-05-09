# maily

This is a simple mail forwarder for AWS Lambda/SES written in Python. It is functionally very similar to the
existing [aws-lambda-ses-forwarder](https://github.com/arithmetric/aws-lambda-ses-forwarder) project but has
better support for myparticular setup (catch-all domain forwarding). Plus the logic is slightly simpler given
that Python has built-in support for parsing email headers and content.

## Setup

Edit the settings_default.py file to include your own configuration and save it as settings.py, then upload
both settings.py and service.py to Lambda. You will need to have your incoming emails saved in an S3 bucket.
