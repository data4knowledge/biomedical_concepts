import yaml
import json
 
nodes = { "SKOS_CONCEPT_SCHEME": [], "SKOS_CONCEPT": [], "OTHER_SOURCE": []}
relationships = { "SKOS_HAS_TOP_CONCEPT": [], "SKOS_NARROWER": [], "FROM_SOURCE": []}

with open("../data/sponsor_ct/sponsor_ct.yaml") as file:
    model = yaml.load(file, Loader=yaml.FullLoader)

    # Source
    source_uri = "http://id.d4k.dk/dataset/source/ct"
    base_uri = "http://id.d4k.dk/dataset/ct/main"

    cs_concept = { "uri": source_uri }
    cs_concept["label"] =  ""
    cs_concept["name"] =  model[":root"][":name"]
    cs_concept["source"] =  "Made up"
    cs_concept["effective_date"] =  "2022-03-21"
    cs_concept["description"] =  "Sponsor CT for the demo"
    cs_concept["version"] =  "0.1"
    cs_concept["status"] =  "Draft"
    nodes["SKOS_CONCEPT_SCHEME"].append(cs_concept)
    source = { "description": "Made up for the demo", "uri": source_uri }
    nodes["OTHER_SOURCE"].append(source)
    relationships["FROM_SOURCE"].append({ "from": cs_concept["uri"], "to": source["uri"] })
    parent_uri = base_uri
    for cl in model[":root"][":code_lists"]:
        cl_concept = { "uri": "%s/%s" % (parent_uri, cl[':identifier']), "alt_label": "", "extensible": False }
        cl_concept["label"] = cl[':pref_label']
        if "extensible" in cl:
            cl_concept["extensible"] = cl['extensible']
        cl_concept["notation"] = cl[':notation']
        cl_concept["definition"] = cl[':definition']
        cl_concept["identifier"] = cl[':identifier']
        if ":alt_label" in cl:
            cl_concept["alt_label"] = cl[':alt_label']
        else:
            cl_concept["alt_label"] = ""
        cl_concept["pref_label"] = cl[':pref_label']
        nodes["SKOS_CONCEPT"].append(cl_concept)
        relationships["SKOS_HAS_TOP_CONCEPT"].append({ "from": cs_concept["uri"], "to": cl_concept["uri"] })
        parent_uri = cl_concept["uri"]
        for cli in cl[":terms"]:
            cli_concept = { "uri": "%s-%s" % (parent_uri, cli[':identifier']), "alt_label": "" }
            cli_concept["label"] = cli[':pref_label']
            cli_concept["notation"] = cli[':notation']
            cli_concept["definition"] = cli[':definition']
            cli_concept["identifier"] = cli[':identifier']
            if ":alt_label" in cl:
                cli_concept["alt_label"] = cli[':alt_label']
            cli_concept["pref_label"] = cli[':pref_label']
            nodes["SKOS_CONCEPT"].append(cli_concept)
            relationships["SKOS_HAS_TOP_CONCEPT"].append({ "from": cl_concept["uri"], "to": cli_concept["uri"] })


with open("../data/sponsor_ct/sponsor_ct_nodes.json", 'w') as outfile:
    json.dump(nodes, outfile, sort_keys=True, indent=4)

with open("../data/sponsor_ct/sponsor_ct_relationships.json", 'w') as outfile:
    json.dump(relationships, outfile, sort_keys=True, indent=4)

