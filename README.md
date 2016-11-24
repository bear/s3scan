s3scan
======

Generate a report of all s3 buckets and their permissions

Usage
=====

    python s3scan.py [-f <format>] [-p <profile>]

    Options:

        -f | --format  Output format
                       Default is 'text'
                       [Optional]
        -p | --profile AWS Credentials Profile
                       Default is None
                       [Optional]

Where the output format can be either 'text' or 'csv'

Requirements
============

Python 2.6+
http://python.org

Boto3 Library
https://github.com/boto/boto3
