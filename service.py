# -*- coding: utf-8 -*-
from __future__ import print_function
print('Maily Service!')
import email
import settings

boto = [None]

class FakeBoto:
    def client(self, ignore):
        return FakeClient()

class FakeClient:
    def send_raw_email(self, Source, Destinations, RawMessage):
        print('Sent fake raw email')
    def get_object(self, Bucket, Key):
        return {'Body':FakeObject()}
        
class FakeObject:
    def read(self):
        with open('email.txt', 'r') as email:
            return email.read()
            
def fakeboto():
    print('Fake!')
    boto[0] = FakeBoto()

def parse(event):
    print('Parsing email')
    if not 'Records' in event or len(event['Records']) != 1:
        raise Exception('Invalid SES message (invalid records)')
    record = event['Records'][0]
    if 'fakeMessage' in record:
        fakeboto()
    else:
        import boto3
        boto[0] = boto3
    if not 'eventSource' in record or record['eventSource'] != 'aws:ses':
        raise Exception('Invalid SES message (invalid source)')
    mail, recipients = record['ses']['mail'], record['ses']['receipt']['recipients']
    print('Parsing email succeeded')
    return mail, recipients
    
def forwards(recipients):
    print('Finding forwards')
    fwds = []
    originals = []
    for recipient in recipients:
        matched = None
        for filter in settings.FILTERS:
            if recipient.endswith(filter):
                matched = filter
                break
        if not matched:
            continue
        emailparts = recipient.split('@')
        username = emailparts[0].lower()
        domain = emailparts[-1].lower()
        originals.append(recipient)
        newname = domain.split('.')[-2]
        tld = domain.split('.')[-1]
        for forwarder in settings.FORWARDS:
            newemail = forwarder.format(username, newname, tld)
            fwds.append(newemail)
    for original in originals:
        print('Sent to %s' % original)
    for fwd in fwds:
        print('Forwarding to %s' % fwd)
    print('Finding forwards succeeded')
    return fwds, originals
    
def fetch(mail, originals):
    print('Fetching email')
    s3 = boto[0].client('s3')
    bucketkey = originals[0].split('@')[-1].split('.')[-2]
    id = settings.BUCKET_ID.format(bucketkey, mail['messageId'])
    raw = None
    fetched = s3.get_object(Bucket=settings.BUCKET, Key=id)
    raw = fetched['Body'].read()
    print('Fetching email succeeded')
    return raw
    
def modify(raw, newfrom):
    print('Modifying email')
    message = email.message_from_string(raw)
    fromemail = message['From']
    replyto = 'Reply-To'
    if message.has_key(replyto):
        message.replace_header(replyto, fromemail)
    else:
        message.add_header(replyto, fromemail)
    frommod = fromemail.replace('<','[').replace('>',']').replace('@','#')
    frommod = '%s <%s>' % (frommod, newfrom)
    message.replace_header('From', frommod)
    toremove = ['Return-Path', 'Sender']
    for header in message.keys():
        if 'DKIM-Signature' in header:
            toremove.append(header)
    for badheader in toremove:
        del message[badheader]
    print('Modifying succeeded')
    return message.as_string()
    
def sendraw(raw, newfrom, destinations):
    print('Sending raw email')
    ses = boto[0].client('ses')
    ses.send_raw_email(Source=newfrom, Destinations=destinations, RawMessage={'Data':raw.encode('utf-8')})

def handler(event, context):
    print('Processing event')
    mail, recipients = parse(event)
    fwds, originals = forwards(recipients)
    if not fwds:
        raise Exception('No forwards found for this email: %s' % str(recipients))
    newfrom = originals[0]
    raw = fetch(mail, originals)
    modified = modify(raw, newfrom)
    sendraw(modified, newfrom, fwds)
    print('Processing complete!')
