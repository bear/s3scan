s3scan
======

Generate a report of all s3 buckets and their permissions

Usage
=====

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

Requirements
============

Python 2.6+ 
http://python.org

Boto Library
https://github.com/boto/boto
