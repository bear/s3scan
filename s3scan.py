"""
:copyright: (c) 2012 by Mike Taylor
:license: BSD, see LICENSE for more details.

Usage:

  python s3scan.py

  No parameters or options right now, just create an s3scan.cfg
  with the following:

    [aws]
    access_key = YOUR_KEY_HERE
    access_secret = YOUR_SECRETS_HERE

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

from xml.etree import cElementTree as ET

from boto.s3.connection import S3Connection

config = ConfigParser.SafeConfigParser()
config.read('s3scan.cfg')

api_key    = config.get('aws', 'access_key')
api_secret = config.get('aws', 'access_secret')

c = S3Connection(api_key, api_secret)

rs = c.get_all_buckets()

print 'Scanning', len(rs), 'buckets'

buckets = {}
maxName = 0

for o in rs:
    buckets[o.name] = {}

    if len(o.name) > maxName:
        maxName = len(o.name)

    acp = o.get_acl()
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

        if grantee['name'] not in buckets[o.name]:
            buckets[o.name][grantee['name']] = []

        buckets[o.name][grantee['name']].append((grantee['id'], grantee['permission']))

for key in buckets:
    bucket     = buckets[key]
    reads      = []
    writes     = []
    reads_acp  = []
    writes_acp = []

    for grantee in bucket:
        s = ''
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

    print s
