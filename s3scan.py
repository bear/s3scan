"""
:copyright: (c) 2012 by Mike Taylor
:license: BSD, see LICENSE for more details.

Usage:

  python s3scan.py [-k <api_key>] [-s <api_secret>] [-f <format>]

Options:

  -k | --key     S3 Access Key
  -s | --secret  S3 Access Secret
  -f | --format  Output format
                 [Optional]

  Where the output format can be either 'text' or 'csv'

If no parameters are given, the configuration file 's3scan.cfg' will
be loaded and should contain:

    [aws]
    access_key = YOUR_KEY_HERE
    access_secret = YOUR_SECRETS_HERE
    format = text

"""

VERSION = (0, 1, 0, '')

__author__    = 'bear (Mike Taylor)'
__contact__   = 'bear@bear.im'
__copyright__ = 'Copyright 2013, Mike Taylor'
__license__   = 'BSD 2-Clause'
__site__      = 'https://github.com/bear/s3scan'
__version__   = u'.'.join(map(str, VERSION[0:3])) + u''.join(VERSION[3:])


import os
import ConfigParser

from optparse import OptionParser
from xml.etree import cElementTree as ET

from boto.s3.connection import S3Connection, OrdinaryCallingFormat


def getConfig():
    parser = OptionParser()

    parser.add_option('-k', '--key',    dest='api_key',    default='',     help='S3 Access Key')
    parser.add_option('-s', '--secret', dest='api_secret', default='',     help='S3 Access Secret')
    parser.add_option('-f', '--format', dest='format',     default='text', help='Output format: text, csv')

    options, args = parser.parse_args()

    api_key    = options.api_key
    api_secret = options.api_secret
    format     = options.format

    if os.path.isfile('s3scan.cfg'):
        config = ConfigParser.SafeConfigParser({ 'access_key':    api_key,
                                                 'access_secret': api_secret,
                                                 'format':        format,
                                               })
        config.read('s3scan.cfg')

        api_key    = config.get('aws', 'access_key')
        api_secret = config.get('aws', 'access_secret')
        format     = config.get('aws', 'format').lower()

    return (api_key, api_secret, format)


def discoverBuckets(api_key, api_secret):
    c  = S3Connection(api_key, api_secret, calling_format=OrdinaryCallingFormat())
    rs = c.get_all_buckets()

    buckets = {}
    maxName = 0

    for b in rs:
        bucketName          = b.name
        buckets[bucketName] = {}

        if len(bucketName) > maxName:
            maxName = len(bucketName)

        acp = b.get_acl()
        xml = acp.acl.to_xml()

        xRoot = ET.fromstring(xml)
        for grant in xRoot:
            grantee = { 'id': None, 'name': None, 'permission': [] }

            for item in grant:
                if item.tag == 'Grantee':
                    for element in item:
                        if element.tag == 'ID':
                            grantee['id'] = element.text
                        elif element.tag == 'DisplayName':
                            grantee['name'] = element.text
                        elif element.tag == 'URI':
                            grantee['id']   = element.text
                            grantee['name'] = element.text.split('/')[-1]
                elif item.tag == 'Permission':
                    grantee['permission'].append(item.text)

            if grantee['name'] not in buckets[bucketName]:
                buckets[bucketName][grantee['name']] = []

            buckets[bucketName][grantee['name']].append((grantee['id'], grantee['permission']))

    return buckets, maxName

def csvFormat(bucket):
    reads      = []
    writes     = []
    reads_acp  = []
    writes_acp = []

    for grantee in bucket:
        for grantee_id, permission in bucket[grantee]:
            if 'READ' in permission:
                reads.append(grantee)
            if 'WRITE' in permission:
                writes.append(grantee)
            if 'READ_ACP' in permission:
                reads_acp.append(grantee)
            if 'WRITE_ACP' in permission:
                writes_acp.append(grantee)

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

    for grantee in bucket:
        for grantee_id, permission in bucket[grantee]:
            if 'READ' in permission:
                reads.append(grantee)
            if 'WRITE' in permission:
                writes.append(grantee)
            if 'READ_ACP' in permission:
                reads_acp.append(grantee)
            if 'WRITE_ACP' in permission:
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
    api_key, api_secret, format = getConfig()

    buckets, maxName = discoverBuckets(api_key, api_secret)

    for key in buckets:
        bucket = buckets[key]

        if format == 'csv':
            print csvFormat(bucket)
        else:
            print textFormat(bucket, maxName)
