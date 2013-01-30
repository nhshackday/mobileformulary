"""
OpenBNF database access
"""
from pymongo import Connection

import settings

conn = Connection(host=settings.DB_HOST, port=settings.DB_PORT)
db = getattr(conn, settings.DB)
if settings.DB_USER and settings.DB_PASS:
    db.authenticate(settings.DB_USER, settings.DB_PASS)
