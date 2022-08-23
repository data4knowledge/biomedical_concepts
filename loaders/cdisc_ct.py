# Simple program to download the latest version of all the CDISC CT and
# convert into a semantic (SKOS) form.

import os
import json
import requests
from beautifultable import BeautifulTable
 
# Get API key. Uses an environment variable.
API_KEY = os.getenv('CDISC_API_KEY')

# Setup schema and instance namespaces
schema_ns = "http://ontologies.d4k.dk/cdisc/ct#"
instance_ns = "http://id.d4k.dk/dataset/cdisc/ct/v48/"

# Information as to when items within a packahe were introduced or withdrawn.
introduced = {"ADAM": 19, "CDASH": 19, "COA": 20, "DEFINE-XML": 40, "GLOSSARY": 44, "PROTOCOL": 29, "QRS": 22, "QS-FT": 19,"SDTM": 19, "SEND": 19}
withdrawn = {"ADAM": None, "CDASH": None, "COA": 22, "DEFINE-XML": None, "GLOSSARY": None, "PROTOCOL": None, "QRS": 24, "QS-FT": 20,"SDTM": None, "SEND": None}

# 1. Build Package List
# =====================
# 
# Process the list of CT pacakges and the items within each package. 

# 1.1 Get all the package information via the API
api_url = "https://api.library.cdisc.org/api/mdr/ct/packages"
headers =  {"Content-Type":"application/json", "api-key": API_KEY}
response = requests.get(api_url, headers=headers)
items = {}
types = {}
for item in response.json()['_links']['packages']:
    reduced_title = item['title'].replace("Controlled Terminology Package ", "")
    reduced_title = reduced_title.replace("Effective ", "")
    title_items = reduced_title.split(' ')
    type = title_items[0].upper()
    types[type] = type
    package_number = title_items[1]
    release_date = title_items[2]
    if not package_number in items:
        items[package_number] = {}
    items[package_number][type] = {'release_date': release_date, 'package_number': package_number, 'type': type, 'href': item['href']}

# 1.2 Transform into a table of package to items
results = []
final_results = {}
keys = items.keys()
for key in keys:
    results.append(int(key))
results.sort()
table = BeautifulTable()
table.columns.header = ["Pk"] + list(types.keys())
for key in results:
    for package, item in items.items():
        if int(package) == key:
            table_row = [key]
            if not package in final_results:
                final_results[package] = []
            final_results[package].append(item)
            for k,v in types.items():
                if k in item:
                    table_row.append(item[k]['release_date'])
                else:
                    if key < introduced[k]:
                        table_row.append("NA")
                    elif withdrawn[k] == None:
                        table_row.append('^')
                    elif key >= withdrawn[k]:
                        table_row.append("W")
                    else:
                        table_row.append('^')
            table.rows.append(table_row)

# 1.3 Print the table, just useful information
table.maxwidth = 150
print('')
print('Key: ')
print('')
print('Date indicates the version to be used for that package.')
print('^ = Use the previous version.') 
print('NA = Not applicable, file was not introduced at that date.')
print('W = file withdrawn, not to be used anymore.')
print('')
print(table)
print('')
print('')

# 2.1 Use the last version published by CDISC. Hard coded, naughty but it works.
#     Place each item within a package into a separate json file.
for item in final_results['48']:
    for k,v in types.items():
        if k in item:    
            # Data for the resuslting JSON files
            nodes = { "SKOS_CONCEPT_SCHEME": [], "SKOS_CONCEPT": [], "API_SOURCE": []}
            relationships = { "SKOS_HAS_TOP_CONCEPT": [], "SKOS_NARROWER": [], "FROM_SOURCE": []}
            print("Link:", item[k]['href'])
            api_url = "https://api.library.cdisc.org/api" + item[k]['href']
            headers =  {"Content-Type":"application/json", "api-key": API_KEY}
            response = requests.get(api_url, headers=headers)
            body = response.json()
            cs_concept = { "uri": "%s%s" % (instance_ns, k.lower()) }
            cs_concept["label"] =  body['label']
            cs_concept["name"] =  body['name']
            cs_concept["source"] =  body['source']
            cs_concept["effective_date"] =  body['effectiveDate']
            cs_concept["description"] =  body['description']
            cs_concept["version"] =  body['version']
            cs_concept["status"] =  body['registrationStatus']
            nodes["SKOS_CONCEPT_SCHEME"].append(cs_concept)
            source = { "url": api_url, "description": "CDISC CT for %s taken from the CDISC library API." % (k.lower()), "uri": "http://id.d4k.dk/dataset/source/cdisc/ct/%s" % (k.lower())}
            nodes["API_SOURCE"].append(source)
            relationships["FROM_SOURCE"].append({ "from": cs_concept["uri"], "to": source["uri"] })
            for cl in body['codelists']:
                cl_concept = { "uri": "%s%s/%s" % (instance_ns, k.lower(), cl['conceptId']), "alt_label": "" }
                cl_concept["label"] = cl['name']
                if "extensible" in cl:
                    cl_concept["extensible"] = cl['extensible']
                else:
                    cl_concept["extensible"] = False
                cl_concept["notation"] = cl['submissionValue']
                cl_concept["definition"] = cl['definition']
                cl_concept["identifier"] = cl['conceptId']
                if "synonyms" in cl:
                    cl_concept["alt_label"] = ';'.join(cl['synonyms'])
                cl_concept["pref_label"] = cl['preferredTerm']
                nodes["SKOS_CONCEPT"].append(cl_concept)
                relationships["SKOS_HAS_TOP_CONCEPT"].append({ "from": cs_concept["uri"], "to": cl_concept["uri"] })

            with open("data/cdisc_ct/%s/cdisc_ct_%s_nodes.json" % (k.lower(), k.lower()), 'w') as outfile:
                json.dump(nodes, outfile, sort_keys=True, indent=4)

            with open("data/cdisc_ct/%s/cdisc_ct_%s_relationships.json" % (k.lower(), k.lower()), 'w') as outfile:
                json.dump(relationships, outfile, sort_keys=True, indent=4)

            for cl in body['codelists']: 
                nodes = { "SKOS_CONCEPT": [] }
                for cli in cl['terms']:
                    cli_concept = { "uri": "%s%s/%s-%s" % (instance_ns, k.lower(), cl['conceptId'], cli['conceptId']), "alt_label": "" }
                    cli_concept["notation"] = cli['submissionValue']
                    cli_concept["definition"] = cli['definition']
                    cli_concept["identifier"] = cli['conceptId']
                    if "synonyms" in cli:
                        cli_concept["alt_label"] = ';'.join(cli['synonyms'])
                    cli_concept["pref_label"] = cli['preferredTerm']
                    nodes["SKOS_CONCEPT"].append(cli_concept)
                    with open("data/cdisc_ct/%s/cdisc_ct_%s_nodes_%s.json" % (k.lower(), k.lower(), cl['conceptId']), 'w') as outfile:
                        json.dump(nodes, outfile, sort_keys=True, indent=4)
