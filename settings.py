"""
Settings for OPENBNF
"""
import os
import urlparse

DB = 'openbnf'
DB_HOST = 'localhost'
DB_PORT = 27017
DB_USER = None
DB_PASS = None


if 'MONGOHQ_URL' in os.environ:
    url = urlparse.urlparse(os.environ['MONGOHQ_URL'])
    DB = url.path[1:]
    DB_HOST = url.hostname
    DB_PORT = url.port
    DB_USER = url.username
    DB_PASS = url.password

