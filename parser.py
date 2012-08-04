"""
BNF Parser

Parsing notes:
==============

Although most of the functions in this file will deal with the raw
markup of a 'scraped' version, processing time is greatly reduced if we
do some initial classification and taxonomy.

The drugfiles command will print a list of all files believed to be drugs
in your current markup snapshot.

All other commands take a -f option which is expected to be a list of files
that we wish to work on.

Thus via simple *nix piping, we can drastically reduce time spent on pointless
I/o per run.
"""
import collections
import json
import logging
import multiprocessing
import os
import re
import sys
import unittest

import argparse
from lxml import html

log = logging.getLogger(name=__name__)
log.setLevel('ERROR')
log.addHandler(logging.StreamHandler())

# Location of the pre-parsed raw source
HTMLDIR = '/home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current'

# Alter this to run short iterations through the drug extraction
# Set to None in order to parse everything.
MAXDRUGS = None

# This is the basic set of patterns to exclude in filenames.
BASEXCLUDE = [
    r'(?<![.]htm)$', # Anything not ending in. htm
    r'alphaindex'    # Alphaindex files are a special class.
    ]

PREPS = 'See under preparations below'
DRUGSECTS = [
    'indications',
    'cautions',
    'side-effects',
    'pregnancy'
    ]

# These were used in previous iterations, useful for storing lists of interesting files.
# INTERACTIONS = 'interactions.txt'
# DRUGFILES = 'drugfiles.txt'

# Utility wrappers
def ld(fname):
    return json.loads(open(fname).read().strip())

def chunks(l, n):
    """
    A generator function for chopping up a given list into chunks of
    length n.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def pp(d):
    "JSON Pretty Print a dict"
    print json.dumps(d, indent=2)
    return

# Lambdas for extracting information from a root node
getname = lambda x: x.cssselect('h1')[0].text_content()

# def find_interactions():
#     "Print files with interactions (pre-proc)"
#     for root, dirs, files in os.walk(HTMLDIR):
#         for f in files:
#             contents = open(os.path.join(root, f)).read()
#             if contents.find('has the following interaction information:') != -1:
#                 print os.path.join(root, f)


def bnfhtml(exclude=BASEXCLUDE):
    """
    Wrap os.walk for the specific BNF HTML dir as
    a generator that yields absolute filepaths.
    """
    for root, dirs, files in os.walk(HTMLDIR):
        for f in files:
            matches = [m for m in [re.search(p, f) for p in exclude] if m is not None]
            if not matches:
                fname = os.path.join(root, f)
                yield fname

def dociter(fnames):
    """
    Given an iterable containing filenames of HTML Documents,
    yield the lxml root element
    """
    for f in fnames:
        yield html.parse(open(fname, 'r')).getroot()

def drugfile_list():
    """
    Return drug pages (pre-proc)
    """
    drugfiles = []
    for fname in bnfhtml():
        with open(fname, 'r') as dfh:
            root = html.parse(dfh).getroot()
            if root == None:
                import ipdb
                ipdb.set_trace()
            if is_drugfile(root):
                drugfiles.append(fname)
                log.debug(fname)
    return drugfiles

class DrugDocument(object):
    """
    Container class for Markup documents we want to deal with.

    Uses __slots__ as a memory & speed optimization.

    Isn't a namedtuple as this allows us to fill the slots from a
    document filename.
    """
    __slots__ = ['fname', 'name', 'markup']

    def __init__(self, fname):
        """
        Read the file, parse it as HTML and extract the Drug Name
        """
        self.fname = fname
        self.markup = markup = html.parse(open(fname, 'r')).getroot()
        self.name = getname(root)

def filter_dups(fnames):
    """
    We have a list of filenames that we think are interesting.

    We also believe that this set contains duplicate entries.

    Return a "set" of filenames with no Duplication.

    The heuristic is simple, we keep a collection of DrugDocuments.
    We enable easy searching by name (Dict key containing a list),
    and then when we create a new one, we only have to check the subset
    of DrugDocuments that share the same top level name.

    Duplicate detection itself is slightly more complicated.
    """
    # !!! This could do with a testcase TBH
    drughash = collections.defaultdict(list)
    for f in fnames:
        drugdoc = DrugDocument(f)
        if len(drughash[f.name]) == 0:
            drughash[f.name].  append(f)
        else:
            # !!! This is where we do genuine duplicate detection.
            pass

# !!! Add a step to this.

# There are many duplications, e.g.
# file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current/2840.htm
# file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current/2838.htm
# Find a heuristic to clean them out&& De-duplicate them.

# def extract_interactions():
#     "Return Drug interactions keyed by drug name"
#     drugs = {}
#     badness = {
#         'cBV': 1
#         }
#     for fname in open(INTERACTIONS, 'r').readlines():
#         root = html.parse(open(fname.strip())).getroot()
#         try:

#             drugints, genints = root.cssselect('table')
#         except:
#             drugints = root.cssselect('table')[0]
#             genints = None
#         for row in drugints.cssselect('tr'):
#             name, interaction, extra = [e.text_content() for e in row.cssselect('td')]
#             _, interact, _ = row.cssselect('td')
#             if 'class' in interact.attrib:
#                 if interact.attrib['class'] in badness:
#                     bad = badness[interact.attrib['class']]
#                 else:
#                     import pdb;pdb.set_trace()
#             else:
#                 bad = 0
#             drugs[name.upper()] = dict(name=name, interaction=interaction, extra=extra, bad=bad,
#                                        backrefs=[])

#     return drugs


# Breadcrumb lambdas
stripnums = lambda x: [re.sub(r'^(\d[.]?)+', '', b).strip() for b in x]
killif_in = lambda x, v: v in x and x.remove(v)


def clean_breadcrumb(drugdict):
    "Clean a breadcrumb trail"
    stripped = stripnums(drugdict['breadcrumbs'])
    killif_in(stripped, drugdict['name'])
    stripped.reverse()
    stripup = [x.upper() for x in stripped]
    return stripup

def breadcrumb_taxonomy(frist, other):
    """
    Given a pair of drugs with breadcrumbs, search for the first discrepancy.

    Ignore the name of the drug.
    Ignore section numbers.
    """
    cleanfrist, cleanother = clean_breadcrumb(frist), clean_breadcrumb(other)

    fristdiff = [o for o in cleanfrist if o not in cleanother]
    otherdiff = [o for o in cleanother if o not in cleanfrist]
    if len(fristdiff) > 0 and len(otherdiff) > 0:
        fristcopy, othercopy = frist.copy(), other.copy()
        fristcopy['name'] = unicode(frist['name']) + u' - {0}'.format(fristdiff[0])
        othercopy['name'] = unicode(other['name']) + u' - {0}'.format(otherdiff[0])
        return fristcopy, othercopy

    if len(cleanfrist)!= len(cleanother):
        sect = (min(len(cleanfrist), len(cleanother))) - 1
        if cleanfrist[-sect:] == cleanother[-sect:]:
            fristcopy, othercopy = frist.copy(), other.copy()
            if len(cleanfrist) > len(cleanother):
                fristcopy['name'] = unicode(frist['name']) + u' - {0}'.format(cleanfrist[0])
            else:
                othercopy['name'] = unicode(other['name']) + u' - {0}'.format(cleanother[0])
            return fristcopy, othercopy

    return None, None

def contentmatch(frist, other):
    """
    Given two dicts representing drugs, check to see if their content matches
    """
    fristkeys = [k for k in frist.keys() if k in DRUGSECTS]
    otherkeys = [k for k in other.keys() if k in DRUGSECTS]
    fristkeys.sort()
    otherkeys.sort()
    if fristkeys == otherkeys:
        match = True
        for k in fristkeys:
            try:

                if frist[k] != other[k]:
                    match = False
                    break
            except KeyError:
                raise
        return match
    else:
        return False


def merge_entries(new, drugs):
    """
    There are numerous entries with identical names.

    Our current heuristic for merging consists of:
    * If there is no useful Dosage information in one of the entries discard it.
    * If we can find a taxonomical difference in the breadcrumbs, adjust the name
    * If one is a preparation of the other, just add the preparation
    """
    nodose = lambda x: len(x['doses']) == 1 and x['doses'][0].lower() == 'see below'
    frist = drugs[new['name']]

    # No Dosage information? Ignore it.
    if nodose(frist):
        drugs[new['name']] = new
        return drugs
    elif nodose(new):
        return drugs

    # Frist real attempt is to differentiate on breadcrumbs
    # An example of this is COLESTYRAMINE:
    # file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current/88939.htm
    # file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current/2838.htm
    newfrist, newother = breadcrumb_taxonomy(frist, new)
    if newfrist and newother:
        del drugs[new['name']] # This has to come first because one of the names may be unchanged
        drugs[newfrist['name']] = newfrist
        drugs[newother['name']] = newother
        return drugs

    # On occasion a drug has no real dose other than 'See preparation below"
    # For this reason we have to deal with the case of a 'Dose Name' (It's a brand name.)
    # file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current/4834.htm
    # file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current/60882.htm
    # clean both, compare, check that dose is a "See below"
    if len(frist['doses']) == 1 and frist['doses'][0] == PREPS:
        drugs[new['name']] = new
        return drugs
    elif len(new['doses']) ==  1 and new['doses'][0] == PREPS:
        return drugs

    # In the more pathological case, there are many doses for a brand name,
    # e.g. TACROLIMUS
    # file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current/200014.htm
    # file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current/213817.htm
    # What we do here is we check to see if all the other info we're interested in is the same

    # fristkeys = [k for k in frist.keys() if k in DRUGSECTS]
    # newkeys = [k for k in new.keys() if k in DRUGSECTS]
    # if fristkeys.sort() == newkeys.sort():
    #     match = True
    #     for k in fristkeys:
    #         if frist[k] != new[k]:
    #             match = False
    #             break
    #     if match:
    if contentmatch(frist, new):
        # if one of them only has the PREPS string (pointless), then we can
        # Just take the one with the doses.
        if len(frist['doses']) == 1:
            drugs[new['name']] = new
            return drugs
        elif len(new['doses']) == 1:
            return drugs
        else:
            doselist = drugs[new['name']]['doses']
            doselist += new['doses']
            doset = list(set(doselist))
            drugs[new['name']]['doses'] = doset
            return drugs

    # Interim
    return drugs
    # That didn't work for some reason
    import ipdb
    ipdb.set_trace()
    wtf = True



# def fextract(x):
#         print x
#         return _extract_drugs(filelist=x)


def extract_drugs(args, filelist=None):
    """
    Top-level drug extraction entrypoint.

    Examine the args and decide whether to map-reduce.

    If so, set up the infrastructure and then delegate to _extract_drugs.
    """
    if args.processes == 1: # Don't bother
        return _extract_drugs(filelist=filelist)
    if args.processes !=- 1:
        nprocs = args.processes
    else:
        nprocs = workers = multiprocessing.cpu_count() * 2 + 1

    def merge_dicts(*dicts):
        """
        Merge a sequence of Drug dicts
        """
        return dicts

    pool = multiprocessing.Pool(processes=4)
    filez = filelist or list(bnfhtml())
    if MAXDRUGS:
        filez = filez[:MAXDRUGS]
    chunked = list(chunks(filez, len(filez)))

    drugdicts = pool.map(_extract_drugs, chunked)
    return None, merge_dicts(*drugdicts)


def _extract_drugs(filelist=None):
    """
    Loop through the files in our HTML dir, and attempt to parse a
    drug from each of them.

    Build up the set of drugs that are contained along with their attributres.

    The optional argument filelist is expected to be a list of strings representing
    absolute directory paths to the set of HTML files we want to parse.
    """
    drugs = {}
    subsections = collections.defaultdict(list)
    filez = filelist or bnfhtml()
    for fname in filez:
        if MAXDRUGS is not None and len(drugs) > MAXDRUGS:
            return drugs, subsections
        #print fname
        if not fname.endswith('.htm'):
            continue
        drug, parent = parse_drugfile(fname)
        if drug:
            if drug['name'] in drugs:
                if drugs[drug['name']]['doses'] == drug['doses']:
                    continue    # Who cares?
                else:
                    # !!! For now we will discount anything that contains no Dosage
                    # information. We may like to re-visit this decision later
                    drugs = merge_entries(drug, drugs)

                    # These should be dealt with by the merger
                    # Some of these cases are down to the 'sub-sections' problem.
                    # See: file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/
                    # mc/bnf/current/3530.htm
                    # file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc
                    # /bnf/current/201311.htm

                    # Others are down to the 'brand names' problem

            # No edge cases let's put 'em in
            drugs[drug['name']] = drug
        if parent:
            subsections[parent].append(drug['name'])
    return drugs, subsections

def is_drugfile(root):
    """
    Given a representation of a page's markup, decide whether it is a
    page containing individual drug information.

    The current heuristic is to check for the existence of the word 'dose'
    inside an H2 tag.

    This seems to be a good 80% solution for now, although improved taxonomy
    and classification would likely improve the extraction process.
    """
    h2s = root.cssselect('h2')
    if not h2s:
        return False
    doseh2s = [d for d in h2s if d.text_content().find('Dose')!= -1]
    if not doseh2s:
        return False
    return True


def parse_drugfile(fname):
    """
    Parse a single file.

    Extract all the information we will subsequently require from it:
    * Name (Unique ID)
    * Dose(s) (Well obviously)
    * Filename (Reference)
    * Breadcrumbs (Taxonomy)
    """
    root = html.parse(open(fname)).getroot()
    # if not root:
    #     import ipdb
    #     ipdb.set_trace()

    if not is_drugfile(root):
        return None, None

    drug = {'fname': fname, 'doses': []}
    # Get the name of the current drug.
    # The name can be convoluted and not actually what appears in the H! tag.
    # thus we deal with the 'sub-section' problem here.
    name = getname(root)
    log.debug(name)

    # !!! We need to keep a hold of breadcrumbs to construct the taxonomy later
    breadcrumbs = [b.text_content() for b in root.cssselect('#pT a')]
    drug['breadcrumbs'] = breadcrumbs
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
        name = u'{0} {1}'.format(name, subsection_name)
    drug['name'] = name

    # #get the parts
    sections = root.cssselect('div.cAF')
    for sect in sections:
        try:
            title = sect.cssselect('h2')[0].text_content()
        except:
            log.debug('Problem: {0}'.format(fname))
            #!!! Deal with this?
            continue
        if title.lower() == 'dose':
            doses = [d.text_content() for d in sect.cssselect('p')]
            drug['doses'] += doses
        elif title.lower() in DRUGSECTS:
            drug[title.lower()] = sect.text_content()

        else:
            # !!! This is where we eventually add the other sections
            pass

    # Take into acount the brand names of drugs
    # They have 'See under preparations' in the main dose
    # and a second H1
    if len(drug['doses']) == 2 and len(root.cssselect('h1')) == 2:
        if PREPS in drug['doses']:
            drug['doses'].remove(PREPS)
            drug['doses'][0] = u'Name[{0}] {1}'.format(
                root.cssselect('h1')[1].text_content(),
                drug['doses'][0]
                )

    # More Brand name dealings.... INTERFERON BETA
    # file:///home/david/src/nhshackday/bnf-html/www.medicinescomplete.com/mc/bnf/current/60791.htm
    # Special-case-y but some brands need subsection info with all details...
    if len(root.cssselect('h1')) == 3:
        brandh1 = root.cssselect('h1')[2]
        brandname = brandh1.text_content()
        doses = brandh1.getparent().cssselect('div.cAY')
        dosetext = "\n".  join([d.text_content() for d in doses])
        for dose in drug['doses']: # We've already slurped some of this. Kill it
            if dosetext.find(dose) != - 1:
                drug['doses'].remove(dose)
        drug['doses'].append(u'Name[{0}] {1}'.format(brandname, dosetext))
    log.debug(drug)
    return drug, parent_name

# def make_backrefs(interactions):
#     "Improve the data, by properly cross referencing"
#     drugs = interactions.keys()
#     for name, data in interactions.items():
#         ldesc = data['interaction'].lower()
#         for d in drugs:
#             if ldesc.find(d.lower()) != -1 and ldesc != name.lower():
#                 interactions[d]['backrefs'].append(name)
#     return interactions

# def interact():
#     "do the full interaction"
#     raw = extract_interactions()
#     interactions = make_backrefs(raw)

def drugfiles(args): # UI Helper fn
    "Print the list of files for which is_drugfile() is True"
    drugs = drugfile_list()
    print "\n".join(drugs)
    return

def drugdict(args): # UI Helper fn
    """
    Print a dictionary representing a collection of Drugs and their
    attributes.

    If the -f option was passed, assume the file to contain a collection
    of files to parse, separated by \n and iterate through this rather
    than parsing the entire Document collection.
    """
    if args.file:
        filez = open(args.file, 'r').read().split("\n")
        if args.offset:
            filez = filez[args.offset: ]
    else:
        filez = None

    drugd, subsections = extract_drugs(args, filelist=filez)
    print json.dumps(drugd,indent=2)
    log.debug(subsections)
    return

def dupdetect(args): # UI Helper
    """
    Detect Documents with duplicate worthwhile semantic content
    """
    filez = open(args.file, 'r').read().split("\n")
    thinned = filter_dups(filez)
    print "\n".join(thinned)
    return


def main():
    """
    Entrypoint to the parser.

    Parse our commandline options.
    Set up any global variables that have been set at the
    commandline and the  defer to the UI helper fn related
    to the current subcommand.
    """
    parser = argparse.ArgumentParser(description="BNF Parser")
    parser.add_argument(
        '-m', '--max', type=int,
        help='Maximum number of drugs to parse.'
        )
    parser.add_argument(
        '--htmldir', type=int,
        help='Absolute path to the root directory with our HTML Documents.'
        )
    parser.add_argument('-p', '--processes', type=int, default=-1,
                        help='Number of Processes to use')
    parser.add_argument('-d', '--debug', help='Print debugging information')
    subparsers = parser.add_subparsers(title='Actions')

    parser_drugfiles = subparsers.add_parser(
        'drugfiles',
        help='Print a list of the files we think are drugs')
    parser_drugfiles.set_defaults(func=drugfiles)

    parser_dupdetect = subparsers.add_parser(
        'dupdetect',
        help='Given a list of files, detect duplicates and remove them'
        )
    parser_dupdetect.add_argument('file', type=str,
                                  help='List of files to inspect')
    parser_dupdetect.set_defaults(func=dupdetect)

    parser_drugdict = subparsers.add_parser(
        'drugdict',
        help='Print a dict representation of the drugs as extracted'
        )
    parser_drugdict.add_argument('-f', '--file', type=str)
    parser_drugdict.add_argument('-o', '--offset', type=int,
                                 help='Begin at this offset in --file')
    parser_drugdict.set_defaults(func=drugdict)

    parser_test = subparsers.add_parser('test', help='Run our Unittests')
    parser_test.set_defaults(func=unittest.main)

    args = parser.parse_args()

    if args.max:
        global MAXDRUGS
        MAXDRUGS = args.max
    if args.htmldir:
        global HTMLDIR
        HTMLDIR = args.htmldir
    if args.debug:
        global log
        log.setLevel('DEBUG')

    args.func(args)

if __name__ == '__main__':
    main()
