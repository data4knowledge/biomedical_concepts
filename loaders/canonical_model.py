import yaml
import json

def format_name(name):
    name = name.lower()
    name = name.replace(" ", "_")
    return name

nodes = { "CANONICAL_MODEL": [], "CANONICAL_NODE": [], "CANONICAL_DATA_TYPE": [], "OTHER_SOURCE": [] }
relationships = { "HAS_SUB_MODEL": [], "CONSISTS_OF": [], "HAS_DATA_TYPE": [], "FROM_SOURCE": []}
repeat = {}

def process_nodes(node_set, parent_uri, rel_type, link_to_parent=True):
    for node in node_set:
        print("Node:", node[":name"])
        uri_name = format_name(node[":name"])
        node_uri = "%s/%s" % (parent_uri, uri_name)
        if not node[":name"] in repeat:
            nodes["CANONICAL_NODE"].append({ "name": node[":name"], "uri": node_uri })
            repeat[node[":name"]] = node_uri
        else:
            node_uri = repeat[node[":name"]]
        if link_to_parent:
            relationships[rel_type].append({"from": parent_uri, "to": node_uri})
        if ":nodes" in node:
            process_nodes(node[":nodes"], node_uri, "CONSISTS_OF")
        else:
            if ":data_types" in node:
                for data_type in node[":data_types"]: 
                    name = format_name(data_type)
                    item_uri = "%s/%s" % (node_uri, name)
                    record = {
                        "name": data_type,
                        "uri": item_uri
                    }
                    nodes["CANONICAL_DATA_TYPE"].append(record)
                    relationships["HAS_DATA_TYPE"].append({"from": node_uri, "to": item_uri})

with open("../data/canonical/canonical_model.yaml") as file:
    model = yaml.load(file, Loader=yaml.FullLoader)

    # Source
    source_uri = "http://id.d4k.dk/dataset/source/canonical"
    base_uri = "http://id.d4k.dk/dataset/canonical"
    common_uri = "%s/common" % (base_uri)
    record = {
        "uri": source_uri, 
        "description": "Designed for this project."
    }
    print(model.keys())
    nodes["OTHER_SOURCE"].append(record)
    nodes["CANONICAL_MODEL"].append({ "name": model[":root"][":name"], "uri": base_uri })
    relationships["FROM_SOURCE"].append({"from": base_uri, "to": source_uri})
    parent_uri = base_uri
    process_nodes(model[":common"][":nodes"], common_uri, "CONSISTS_OF", False)
    process_nodes(model[":root"][":nodes"], base_uri, "HAS_SUB_MODEL")

with open("../data/canonical/canonical_model_nodes.json", 'w') as outfile:
    json.dump(nodes, outfile, sort_keys=True, indent=4)
with open("../data/canonical/canonical_model_relationships.json", 'w') as outfile:
    json.dump(relationships, outfile, sort_keys=True, indent=4)
