import json
import pandas as pd

files = ["ta", "te", "ti", "ts", "tv"]

#ta = pd.read_sas("data/cdisc_pilot/ta.xpt", encoding="ISO-8859-1")
#te = pd.read_sas("data/cdisc_pilot/te.xpt", encoding="ISO-8859-1")
#ti = pd.read_sas("data/cdisc_pilot/ti.xpt", encoding="ISO-8859-1")
ts = pd.read_sas("data/cdisc_pilot/ts.xpt", encoding="ISO-8859-1")
#tv = pd.read_sas("data/cdisc_pilot/tv.xpt", encoding="ISO-8859-1")

#print(ts)

the_nodes = { 
    "STUDY": [],
    "STUDY_IDENTIFIER": [],
    "STUDY_TYPE": [],
    "STUDY_PHASE": [],
    "STUDY_PROTOCOL": [],
    "INDICATION": [],
    "STUDY_DESIGN": [],
    "POPULATION": [],
    "INVESTIGATIONAL_INTERVENTIONS": [],
    "CODE": [],
    "OBJECTIVE": [],
    "STUDY_ARM": [],
    "STUDY_EPOCH": [],
    "STUDY_ELEMENT": [],
    "RULE": [],
    "STUDY_CELL": [],
    "VISIT": [],
    "WORKFLOW_ITEM": [],
    "ACTIVITY": [],
    "PROCEDURE": [],
    "STUDY_DATA": [],
    "ENDPOINT": []
}

the_relationships = { 
    "HAS_IDENTIFIER": [],
    "HAS_STUDY_TYPE": [],
    "HAS_STUDY_PHASE": [],
    "HAS_PROTOCOL": [],
    "HAS_STUDY_DESIGN": [],
    "HAS_POPULATION": [],
    "HAS_INVESTIGATIONAL_INTERVENTION": [],
    "HAS_INDICATION": [],
    "HAS_OBJECTIVE": [],
    "HAS_CELL": [],
    "HAS_ARM": [],
    "HAS_EPOCH": [],
    "HAS_ELEMENT": [],
    "HAS_START_RULE": [],
    "HAS_END_RULE": [],
    "HAS_VISIT": [], 
    "HAS_ACTIVITY": [],
    "USED_IN_VISIT": [],
    "HAS_PREVIOUS_WORKFLOW": [],
    "HAS_PREVIOUS_ACTIVITY": [],
    "HAS_PROCEDURE": [],
    "HAS_STUDY_DATA": [],
    "HAS_ENDPOINT": [],
    "HAS_CODED": [] 
}

root_uri = "http://id.d4k.dk/dataset/study/cdisc/pilot"

protocol_uri = "%s/spr" % (root_uri)
record = {
    "key": protocol_uri,
        "brief_title": "CDISC PILOT", 
        "official_title": "Targeting Agents in ABTC",
        "PublicTitle": "The Lilly CDISC Pilot",
        "scientific_title": "Scientific Title",
        "amendments": ""
}
the_nodes["STUDY_PROTOCOL"].append(record)

rows = ts.loc[ts['TSPARMCD'] == 'TITLE', "TSVAL"]
study_uri = "%s" % (root_uri)
record = {
    "key": study_uri,
    "study_title": rows.tolist()[0],
    "study_version": "???",
    "study_tag": "???",
    "study_status": "???"
}
the_nodes["STUDY"].append(record)
the_relationships["HAS_PROTOCOL"].append({ "from": study_uri, "to": protocol_uri})

record = {
    "uri": "%s/sident-1" % (root_uri),
    "name": "Sponsor",
    "id_type": "SponsorID",
    "org_code": "CDISC Pilot"
}
the_nodes["STUDY_IDENTIFIER"].append(record)
the_relationships["HAS_IDENTIFIER"].append({ "from": study_uri, "to": record["uri"]})

rows = ts.loc[ts['TSPARMCD'] == 'TTYPE', "TSVAL"]
for index, row in enumerate(rows):
    record = {
        "uri": "%s/ttype-%s" % (root_uri, index + 1),
        "study_type_classification": row
    }
    the_nodes["STUDY_TYPE"].append(record)
    the_relationships["HAS_STUDY_TYPE"].append({ "from": study_uri, "to": record["uri"]})

rows = ts.loc[ts['TSPARMCD'] == 'TPHASE', "TSVAL"]
for index, row in enumerate(rows):
    record = {
        "uri": "%s/tphase-%s" % (root_uri, index + 1),
        "study_type_phase": row
    }
    the_nodes["STUDY_PHASE"].append(record)
    the_relationships["HAS_STUDY_PHASE"].append({ "from": study_uri, "to": record["uri"]})

study_design_uri = "%s/sd" % (root_uri)
record = { "uri": study_design_uri }
the_nodes["STUDY_DESIGN"].append(record)
the_relationships["HAS_STUDY_DESIGN"].append({ "from": study_uri, "to": record["uri"]})

rows = ts.loc[ts['TSPARMCD'] == 'INDIC', "TSVAL"]
for index, row in enumerate(rows):
    record = {
        "uri": "%s/indic-%s" % (root_uri, index + 1),
        "indication_desc": row
    }
    the_nodes["INDICATION"].append(record)
    the_relationships["HAS_INDICATION"].append({ "from": study_design_uri, "to": record["uri"]})

population_uri = "%s/spop" % (root_uri)
record = {
    "uri": population_uri,
    "population_desc": "Not known"
}
the_nodes["POPULATION"].append(record)
the_relationships["HAS_POPULATION"].append({ "from": study_design_uri, "to": record["uri"]})

rows = ts.loc[ts['TSPARMCD'] == 'TRT', "TSVAL"]
for index, row in enumerate(rows):
    record = {
        "uri": "%s/trt-%s" % (root_uri, index + 1),
        "indication_desc": row
    }
    the_nodes["INVESTIGATIONAL_INTERVENTIONS"].append(record)
    the_relationships["HAS_INVESTIGATIONAL_INTERVENTION"].append({ "from": study_design_uri, "to": record["uri"]})

array = ['OBJPRIM', 'OBJSEC']
rows = ts.loc[ts['TSPARMCD'].isin(array), "TSVAL"]
for index, row in enumerate(rows):
    record = {
        "uri": "%s/obj-%s" % (root_uri, index + 1),
        "objective_desc": row
    }
    the_nodes["OBJECTIVE"].append(record)
    the_relationships["HAS_OBJECTIVE"].append({ "from": study_design_uri, "to": record["uri"]})

# Now output the JSON files
with open("data/cdisc_pilot/cdisc_pilot_nodes.json", 'w') as outfile:
    json.dump(the_nodes, outfile, sort_keys=True, indent=4)
with open("data/cdisc_pilot/cdisc_pilot_relationships.json", 'w') as outfile:
    json.dump(the_relationships, outfile, sort_keys=True, indent=4)