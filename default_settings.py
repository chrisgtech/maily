# Incoming email to process
# Will be matched with .endswith()
FILTERS = ['@example.com', 'user@example.edu']
# String format for forwarding mail
FORWARDS = ['{1}{2}@example.net']
# Bucket ID format
BUCKET_ID = '{0}/{1}'
# Your bucket name on AWS
BUCKET = 'bucket-name'