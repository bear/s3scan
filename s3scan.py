"""
:copyright: (c) 2012-2015 by Mike Taylor
:license: BSD, see LICENSE for more details.

Usage:

  python s3scan.py [-f <format>]

Options:

  -f | --format  Output format
                 [Optional]

  Where the output format can be either 'text' or 'csv'
"""

VERSION = (0, 1, 2, '')

__author__    = 'bear (Mike Taylor)'
__contact__   = 'bear@bear.im'
__copyright__ = 'Copyright 2012-2016, Mike Taylor'
__license__   = 'BSD 2-Clause'
__site__      = 'https://github.com/bear/s3scan'
__version__   = u'.'.join(map(str, VERSION[0:3])) + u''.join(VERSION[3:])


import os
import ConfigParser
import boto3

from optparse import OptionParser

def getConfig():
    parser = OptionParser()
    # Read API Key & Secret from Environment...
    parser.add_option('-f', '--format', dest='format',     default='text', help='Output format: text, csv')
    options, args = parser.parse_args()

    format = options.format
    return format

def discoverBuckets():
    s3  = boto3.resource('s3')
    rs = s3.buckets.all()

    buckets = {}
    maxName = 0 #use pprint instead?

    for b in rs:
        bucketName          = b.name
        buckets[bucketName] = {}

        #keep track of longest bucketName for textFormat
        if len(bucketName) > maxName:
            maxName = len(bucketName)

        for grant in b.Acl().grants:
            grantee_name = 'None'
            grantee_id = 'None'

            grantee = grant['Grantee']
            if 'DisplayName' in grantee:
                grantee_name = grantee['DisplayName']
                grantee_id = grantee['ID']
            elif 'URI' in grantee:
                grantee_name = grantee['URI'].split('/')[-1]
                grantee_id = grantee['URI']

            if grantee_name not in buckets[bucketName]:
                buckets[bucketName][grantee_name] = []

            buckets[bucketName][grantee_name].append((grantee_id,grant['Permission']))

    return buckets, maxName

def csvFormat(bucket):
    reads      = []
    writes     = []
    reads_acp  = []
    writes_acp = []

    for grantee in bucket:
        for grantee_id, permission in bucket[grantee]:
            if 'READ' == permission:
                reads.append(grantee)
            if 'WRITE' == permission:
                writes.append(grantee)
            if 'READ_ACP' ==  permission:
                reads_acp.append(grantee)
            if 'WRITE_ACP' == permission:
                writes_acp.append(grantee)
            if 'FULL_CONTROL' == permission:
                reads.append(grantee)
                writes.append(grantee)
                writes_acp.append(grantee)
                reads_acp.append(grantee)

    l = [key,
         ';'.join(writes),
         ';'.join(reads),
         ';'.join(writes_acp),
         ';'.join(reads_acp),
        ]

    return ','.join(l)

def textFormat(bucket, maxName):
    reads      = []
    writes     = []
    reads_acp  = []
    writes_acp = []

    # Adding full_control
    # see: http://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#permissions
    for grantee in bucket:
        for grantee_id, permission in bucket[grantee]:
            if 'READ' == permission:
                reads.append(grantee)
            if 'WRITE' == permission:
                writes.append(grantee)
            if 'READ_ACP' == permission:
                reads_acp.append(grantee)
            if 'WRITE_ACP' == permission:
                writes_acp.append(grantee)
            if 'FULL_CONTROL' == permission:
                reads.append(grantee)
                writes.append(grantee)
                reads_acp.append(grantee)
                writes_acp.append(grantee)

    s = '{0:>{1}} --'.format(key, maxName)
    t = '\n' + ' '*(maxName + 4)
    if len(writes) > 0:
        s += ' Write: %s;' % ','.join(writes)
    if len(reads) > 0:
        s += ' Read: %s;' % ','.join(reads)
    if len(writes_acp) > 0:
        s += t + 'ACP Write: %s' % ','.join(writes_acp)
    if len(reads_acp) > 0:
        s += t + 'ACP Read: %s' % ','.join(reads_acp)

    return s

if __name__ == '__main__':
    format = getConfig()

    buckets, maxName = discoverBuckets()

    for key in buckets:
        bucket = buckets[key]

        if format == 'csv':
            print csvFormat(bucket)
        else:
            print textFormat(bucket, maxName)
