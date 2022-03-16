# Simple program to download the latest version of all the CDISC SDTM and
# convert into a Neo4j form.

import os
import json
import requests

 
# Get API key. Uses an environment variable.
API_KEY = os.getenv('CDISC_API_KEY')
headers =  {"Content-Type":"application/json", "api-key": API_KEY}

# Setup schema and instance namespaces
schema_ns = "http://ontologies.d4k.dk/cdisc/sdtm#"
instance_ns = "http://id.d4k.dk/dataset/cdisc/sdtm/v3-4/"

# Set up the structures for all the nodes and relationships
nodes = { "SDTM_IG": [], "SDTM_DATASET": [], "SDTM_VARIABLE": [], "API_SOURCE": []}
relationships = { "HAS_DATASET": [], "HAS_VARIABLE": [], "FROM_SOURCE": []}
    
# Get list of SDTM IGs on offer from the API
# ==========================================
# 
# Get the set of SDTM IG datasets
# CDISC API ref: https://www.cdisc.org/cdisc-library/api-documentation#/default/api.products.products.get_product_datatabulation
api_url = "https://api.library.cdisc.org/api/mdr/sdtmig/3-4/datasets?expand=false"
response = requests.get(api_url, headers=headers)
ig_body = response.json()

# Build the IG header subject
#ig = URIRef(instance_ns)
ig = { "uri": "%s" % (instance_ns) }
ig["label"] = ig_body['label']
ig["label"] = ig_body['description']
ig["label"] = ig_body['name']
ig["label"] = ig_body['effectiveDate']
nodes["SDTM_IG"].append(ig)
source = { "url": api_url, "uri": "http://id.d4k.dk/dataset/source/cdisc/sdtm/" }
nodes["API_SOURCE"].append(source)
relationships["FROM_SOURCE"].append({ "from": ig["uri"], "to": source["uri"] })        

# Process the datasets
for ds in ig_body['_links']['datasets']:

    # Get the href to get the dataset API call.
    api_url = "https://api.library.cdisc.org/api%s" % (ds['href'])
    response = requests.get(api_url, headers=headers)
    ds_body = response.json()
    domain = ds_body['name']
    print(ds_body['name'])

    # Process the dataset
    dataset = { "uri": "%s%s" % (instance_ns, domain.lower()) }
    dataset["name"] =  domain
    dataset["label"] =  ds_body['label']
    if 'description' in ds:
        dataset["description"] = ds_body['description']
    else:
        # No description, use the label.
        dataset["description"] = ds_body['label']
    dataset["structure"] = ds_body['datasetStructure']
    dataset["ordinal"] = ds_body['ordinal']
    nodes["SDTM_DATASET"].append(dataset)
    relationships["HAS_DATASET"].append({ "from": ig["uri"], "to": dataset["uri"] })
    for item in ds_body['datasetVariables']:
        variable = { "uri": "%s%s/%s" % (instance_ns, domain.lower(), item['name'].lower()) }
        variable["name"] = item['name']
        variable["name"] = item['ordinal']
        variable["name"] = item['label']
        variable["name"] = item['description']
        variable["name"] = item['simpleDatatype']
        variable["name"] = item['role']
        variable["name"] = item['core']
        variable["ct"] = ""
        if 'codelist' in item['_links']:
            # Horrid nasty fix to save time. Don't query the API to get the identifier of the linked codelist.
            # Assume the URL last part is the C code. Terrible I know but life it too short.
            parts = item['_links']['codelist'][0]['href'].split('/')
            variable["ct"] = parts[-1]

        # Set the value domain. This is for those ISO8601 and other references
        if 'describedValueDomain' in item:
            variable["described_value_domain"] = item['describedValueDomain']
        else:
            variable["described_value_domain"] = ""
        
        nodes["SDTM_VARIABLE"].append(variable)
        relationships["HAS_VARIABLE"].append({ "from": dataset["uri"], "to": variable["uri"] })
        # Print just to show things are working.
        print(variable)

with open("../data/cdisc_sdtm/cdisc_sdtm_nodes.json", 'w') as outfile:
    json.dump(nodes, outfile, sort_keys=True, indent=4)

with open("../data/cdisc_sdtm/cdisc_sdtm_relationships.json", 'w') as outfile:
    json.dump(relationships, outfile, sort_keys=True, indent=4)

