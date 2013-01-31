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

bnfcodes = json.loads(
    open('data/bnfcodes.json', 'r').read()
    )

def main():
    db.drugs.drop()
    db.codes.drop()
    for drug in bnf.values():
        db.drugs.save(drug)
    for codemap in bnfcodes:
        db.codes.save(codemap)
    return 0

if __name__ == '__main__':
    db.drus.drop()
    sys.exit(main())
