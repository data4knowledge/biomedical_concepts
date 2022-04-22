import yaml
import json

files = ["vital_signs/weight.yaml", "demographics/dm.yaml", "laboratory/lb.yaml", "adverse_events/ae.yaml", "exposure/ex.yaml"]

def format_name(name):
    name = name.lower()
    name = name.replace(" ", "_")
    return name

nodes = { "BC_INSTANCE": [], "BC_ITEM": [], "BC_DATA_TYPE": [], "BC_VALUE_SET": [], "OTHER_SOURCE": [] }
relationships = { "HAS_ITEM": [], "HAS_IDENTIFIER": [], "HAS_QUALIFIER": [], "BC_NARROWER": [], "HAS_DATA_TYPE": [], "HAS_RESPONSE": [], "FROM_SOURCE": []}
bc_uri = {}

# Source
source_uri = "http://id.d4k.dk/dataset/source/bc_instance"
record = {
    "url": "",
    "uri": source_uri, 
    "description": "Designed for this project."
}
nodes["OTHER_SOURCE"].append(record)

for filename in files:

    with open("../data/bc/%s" % (filename)) as file:
        narrower = {}
        instances = yaml.load(file, Loader=yaml.FullLoader)

        for instance in instances:
            print("instance:", instance[":name"])
            uri_name = format_name(instance[":name"])
            base_uri = "http://id.d4k.dk/dataset/bc_instance/%s" % (uri_name)
            nodes["BC_INSTANCE"].append({"name": instance[":name"], "based_on": instance[":based_on"], "uri": base_uri})           
            relationships["FROM_SOURCE"].append({"from": base_uri, "to": source_uri})
            bc_uri[uri_name] = base_uri
            narrower[base_uri] = []
            if ":narrower" in instance:
                for children in instance[":narrower"]:
                    narrower[base_uri].append(format_name(children))
            # Identifier Node and Associated Data Type
            item = instance[":identified_by"]
            qualifier_item = ""
            if ":qualified_by" in item:
                qualifier_item = item[":qualified_by"]
            name = format_name(item[":name"])
            item_uri = "%s/%s" % (base_uri, name)
            identifier_uri = item_uri
            record = {
                "name": item[":name"], 
                "collect": item[":collect"],
                "enabled": item[":enabled"],
                "uri": item_uri
            }
            nodes["BC_ITEM"].append(record)
            relationships["HAS_ITEM"].append({"from": base_uri, "to": item_uri})
            relationships["HAS_IDENTIFIER"].append({"from": base_uri, "to": item_uri})
            if ":data_type" in item:
                for data_type in item[":data_type"]: 
                    #print(item[":data_type"])
                    name = format_name(data_type[":name"])
                    data_type_uri = "%s/%s" % (item_uri, name)
                    record = {
                        "name": data_type[":name"],
                        "uri": data_type_uri
                    }
                    nodes["BC_DATA_TYPE"].append(record)
                    relationships["HAS_DATA_TYPE"].append({"from": item_uri, "to": data_type_uri})
                    if ":value_set" in data_type:
                        #print(data_type[":value_set"])
                        for term in data_type[":value_set"]: 
                            #print(term)
                            cl = term[":cl"]
                            cli = term[":cli"]
                            term_uri = "%s/%s-%s" % (data_type_uri, cl.lower(), cli.lower())
                            record = {
                                "cl": cl,
                                "cli": cli,
                                "uri": term_uri
                            }
                            nodes["BC_VALUE_SET"].append(record)
                            relationships["HAS_RESPONSE"].append({"from": data_type_uri, "to": term_uri})

            # Now all the items
            for item in instance[":has_items"]: 
                name = format_name(item[":name"])
                collect = False
                if ":collect" in item:
                    collect = item[":collect"]
                item_uri = "%s/%s" % (base_uri, name)
                record = {
                    "name": item[":name"], 
                    "collect": collect,
                    "enabled": item[":enabled"],
                    "uri": item_uri
                }
                nodes["BC_ITEM"].append(record)
                relationships["HAS_ITEM"].append({"from": base_uri, "to": item_uri})
                if qualifier_item == item[":name"]:
                    relationships["HAS_QUALIFIER"].append({"from": identifier_uri, "to": item_uri})
                if ":data_type" in item:
                    for data_type in item[":data_type"]: 
                        name = format_name(data_type[":name"])
                        data_type_uri = "%s/%s" % (item_uri, name)
                        record = {
                            "name": data_type[":name"],
                            "uri": data_type_uri
                        }
                        nodes["BC_DATA_TYPE"].append(record)
                        relationships["HAS_DATA_TYPE"].append({"from": item_uri, "to": data_type_uri})
                        if ":value_set" in data_type:
                            #print(data_type[":value_set"])
                            for term in data_type[":value_set"]: 
                                #print(term)
                                cl = term[":cl"]
                                cli = term[":cli"]
                                term_uri = "%s/%s-%s" % (data_type_uri, cl.lower(), cli.lower())
                                record = {
                                    "cl": cl,
                                    "cli": cli,
                                    "uri": term_uri
                                }
                                nodes["BC_VALUE_SET"].append(record)
                                relationships["HAS_RESPONSE"].append({"from": data_type_uri, "to": term_uri})
    for k, v in narrower.items():
        if len(v) > 0:
            from_uri = k
            for bc in v:
                to_uri = bc_uri[bc]
                print("Narrower from %s to %s" % (from_uri, to_uri))
                relationships["BC_NARROWER"].append({"from": from_uri, "to": to_uri})

                
with open("../data/bc/bc_instances_nodes.json", 'w') as outfile:
    json.dump(nodes, outfile, sort_keys=True, indent=4)
with open("../data/bc/bc_instances_relationships.json", 'w') as outfile:
    json.dump(relationships, outfile, sort_keys=True, indent=4)
