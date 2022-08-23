import json
import yaml

nodes = { "SDTM_MODEL": [], "SDTM_CLASS": [], "SDTM_MODEL_VARIABLE": [], "CANONICAL_REF": [], "OTHER_SOURCE": [] }
relationships = { "HAS_CLASS": [], "HAS_VARIABLE": [], "HAS_CANONICAL_REF": [], "FROM_SOURCE": []}
repeat = {}

with open("data/cdisc_sdtm/cdisc_sdtm_model.yaml") as file:
    model = yaml.load(file, Loader=yaml.FullLoader)

    # Source
    source_uri = "http://id.d4k.dk/dataset/source/sdtm_model"
    base_uri = "http://id.d4k.dk/dataset/sdtm_model"
    record = {
        "url": "",
        "uri": source_uri, 
        "description": "Designed for this project."
    }
    nodes["OTHER_SOURCE"].append(record)
    nodes["SDTM_MODEL"].append({ "name": model[":root"][":name"], "uri": base_uri })
    relationships["FROM_SOURCE"].append({"from": base_uri, "to": source_uri})
    for the_class in model[":root"][":classes"]:
        class_uri = "%s/%s" % (base_uri, the_class[":name"])
        nodes["SDTM_CLASS"].append({ "name": the_class[":name"], "uri": class_uri })
        relationships["HAS_CLASS"].append({"from": base_uri, "to": class_uri})
        for variable in the_class[":variables"]:
            variable_uri = "%s/%s" % (class_uri, variable[":name"])
            nodes["SDTM_MODEL_VARIABLE"].append({ "name": variable[":name"], "bc": variable[":bc"], "uri": variable_uri })
            relationships["HAS_VARIABLE"].append({"from": class_uri, "to": variable_uri})
            index = 1
            for canonical in variable[":canonical"]:
                canonical_uri = "%s/%s" % (variable_uri, "c%i" % (index))
                nodes["CANONICAL_REF"].append({ "node": canonical[":node"], "data_type": canonical[":data_type"], "property": canonical[":property"], "uri": canonical_uri })
                relationships["HAS_CANONICAL_REF"].append({"from": variable_uri, "to": canonical_uri})
                index += 1

with open("data/cdisc_sdtm/cdisc_sdtm_model_nodes.json", 'w') as outfile:
    json.dump(nodes, outfile, sort_keys=True, indent=4)
with open("data/cdisc_sdtm/cdisc_sdtm_model_relationships.json", 'w') as outfile:
    json.dump(relationships, outfile, sort_keys=True, indent=4)
