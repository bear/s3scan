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

        buckets[o.name][grantee['name']] = grantee

for key in buckets:
    bucket = buckets[key]
    reads  = []
    writes = []
    for grantee in bucket:
        s = ''
        permission = bucket[grantee]['permission']
        if 'READ' in permission:
            reads.append(grantee)
        if 'WRITE' in permission:
            writes.append(grantee)

    s = '{0:>{1}} -- '.format(key, maxName)
    if len(reads) + len(writes) == 0:
        s += 'owner only'
    else:
        if len(writes) > 0:
            s += 'Write: %s' % ','.join(writes)
        if len(reads) > 0:
            s += 'Read: %s' % ','.join(reads)
    print s
