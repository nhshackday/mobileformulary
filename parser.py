"""
BNF Parser
"""
import collections
import json
import multiprocessing
import os
import sys

from lxml import html

# Location of the pre-parsed raw source
HTMLDIR = '/home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current'

# Alter this to run short iterations through the drug extraction
# Set to None in order to parse everything.
MAXDRUGS = None

# These were used in previous iterations, useful for storing lists of interesting files.
# INTERACTIONS = 'interactions.txt'
# DRUGFILES = 'drugfiles.txt'

# Utility wrappers
def ld(fname):
    return json.loads(open(fname).read().strip())


def find_interactions():
    "Print files with interactions (pre-proc)"
    for root, dirs, files in os.walk(HTMLDIR):
        for f in files:
            contents = open(os.path.join(root, f)).read()
            if contents.find('has the following interaction information:') != -1:
                print os.path.join(root, f)

def find_drugs():
    "Return drug pages (pre-proc)"
    print "Locating Drugs"
    drugfiles = []
    for root, dirs, files in os.walk(HTMLDIR):
        for f in files:
            if MAXDRUGS and len(drugfiles) > MAXDRUGS:
                break
            contents = open(os.path.join(root, f)).read()
            soup = BeautifulSoup.BeautifulSoup(contents)
            if soup.find('h3', text="Dose"):
                drugfiles.append(os.path.join(root, f))
    return drugfiles

def extract_interactions():
    "Return Drug interactions keyed by drug name"
    drugs = {}
    badness = {
        'cBV': 1
        }
    for fname in open(INTERACTIONS, 'r').readlines():
        root = html.parse(open(fname.strip())).getroot()
        try:

            drugints, genints = root.cssselect('table')
        except:
            drugints = root.cssselect('table')[0]
            genints = None
        for row in drugints.cssselect('tr'):
            name, interaction, extra = [e.text_content() for e in row.cssselect('td')]
            _, interact, _ = row.cssselect('td')
            if 'class' in interact.attrib:
                if interact.attrib['class'] in badness:
                    bad = badness[interact.attrib['class']]
                else:
                    import pdb;pdb.set_trace()
            else:
                bad = 0
            drugs[name.upper()] = dict(name=name, interaction=interaction, extra=extra, bad=bad,
                                       backrefs=[])

    return drugs

def extract_drugs():
    drugs = {}
    subsections = collections.defaultdict(list)
    for r, dirs, files in os.walk(HTMLDIR):
        for fname in files:
            print fname
            if not fname.endswith('.htm'):
                continue
            drug, parent = parse_drugfile(os.path.join(r, fname))
            if drug:
                if drug['name'] in drugs:
                    if drugs[drug['name']]['doses'] == drug['doses']:
                        continue    # Who cares?
                    else:
                        # Some of these cases are down to the 'sub-sections' problem.
                        # See: file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/
                        # mc/bnf/current/3530.htm
                        # file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc
                        # /bnf/current/201311.htm

                        # Others are down to the 'brand names' problem
                        import ipdb
                        ipdb.set_trace()
                # No edge cases let's put 'em in
                drugs[drug['name']] = drug
            if parent:
                subsections[parent].append(drug['name'])

def is_drugfile(root):
    "Predicate!"
     # This is the main test for this being an interesting drug
    # This could almost certainly be improved.
    h3s = root.cssselect('h3')
    if not h3s:
        return False
    doseh3s = [d for d in h3s if d.text_content().find('Dose')!= -1]
    if not doseh3s:
        return False
    return True

def parse_drugfile(fname):
    "Parse a single file"
    root = html.parse(open(fname)).getroot()
    if not root:
        import ipdb
        ipdb.set_trace()

    if not is_drugfile(root):
        return None, None

    drug = {'fname': fname}
    #get the name of the current drug.
    # The name can be convoluted and not actually what appears in the H! tag.
    # thus we deal with the 'sub-section' problem here.
    name = root.cssselect('h1')[0].text_content()
    print name
    breadcrumbs = [b.text_content() for b in root.cssselect('#pT a')]
    if name not in breadcrumbs:
        # For whatever chronically idiotic reason, this means that we're
        # dealing with a top-level drug with sub-sections.

        # For other equally incomprehensible reasons, the sub-section machinery
        # is in fact fundamentally broke on some sort of CMS level, so we'll have to
        # Re-construct it ourselves.
        pass
    parent_name = None
    if name in breadcrumbs and not breadcrumbs.index(name) == len(breadcrumbs) - 1:
        subsection_name = breadcrumbs[breadcrumbs.index(name) + 1]
        parent_name = name
        name = '{0} {1}'.format(name, subsection_name)
    drug['name'] = name

    # #get the parts
    sections = root.cssselect('div.cAF')
    for sect in sections:
        try:
            title = sect.cssselect('h2')[0].text_content()
        except:
            print 'Problem:', fname
            continue
        if title.lower() == 'dose':
            doses = [d.text_content() for d in sect.cssselect('p')]
            drug['doses'] = doses
    print drug
    return drug, parent_name

def make_backrefs(interactions):
    "Improve the data, by properly cross referencing"
    drugs = interactions.keys()
    for name, data in interactions.items():
        ldesc = data['interaction'].lower()
        for d in drugs:
            if ldesc.find(d.lower()) != -1 and ldesc != name.lower():
                interactions[d]['backrefs'].append(name)
    return interactions

def interact():
    "do the full interaction"
    raw = extract_interactions()
    interactions = make_backrefs(raw)

def main():
    "Entrypoint to the parser"
    pool = []
    q = multiprocessing.JoinableQueue()
    # drugfiles = find_drugs()
    drugs = extract_drugs()
    with open('bnf.json', 'w') as fh:
        fh.write(json.dumps(drugs))

    print 'Wrote data to bnf.json'

if __name__ == '__main__':
    main()
