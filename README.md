s3scan
======

scan s3 buckets for security issues

Usage
=====

    python s3scan.py

No parameters or options right now, just create and populate s3scan.cfg
with the following:

    [aws]
    access_key = YOUR_KEY_HERE
    access_secret = YOUR_SECRETS_HERE

Requirements
============

Python 2.6+  -- http://python.org
Boto Library -- https://github.com/boto/boto