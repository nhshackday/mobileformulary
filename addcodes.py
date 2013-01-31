"""
Add bnfcodes to BNF.json
"""
import json

names = json.loads(open('templates/bnf.json', 'r').read()).keys()
codes = [d.split(',') for d in open('../data/drugs.codes.csv', 'r').readlines()]
print len(codes)
codes = set(codes)
print len(codes)
codes = [[c, n.strip().upper()] for c, n in codes[1:]]

namedict = {n: None for n in names}
for code, name in codes:
    if name in namedict:
        namedict[name] = code

print len(namedict)
print len({k: v for k, v in namedict.items() if v is not None})

import ipdb;ipdb.set_trace()
