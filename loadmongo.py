"""
Load fixtures into MongoDB
"""
import json
import os
import sys

from db import db

bnf =  json.loads(
    open(os.path.join(
            os.path.dirname(__file__),
            'templates/bnf.json'
        ), 'r').read()
    )

def main():
    db.drugs.drop()
    for drug in bnf.values():
        db.drugs.save(drug)
    return 0

if __name__ == '__main__':
    db.drus.drop()
    sys.exit(main())
