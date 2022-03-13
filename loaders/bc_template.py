import yaml
import json

def format_name(name):
    name = name.lower()
    name = name.replace(" ", "_")
    return name

nodes = { "BC_TEMPLATE": [], "BC_ITEM": [], "BC_DATA_TYPE": [], "OTHER_SOURCE": [] }
relationships = { "HAS_ITEM": [], "HAS_IDENTIFIER": [], "HAS_DATA_TYPE": [], "FROM_SOURCE": []}
with open("../data/templates.yaml") as file:
    templates = yaml.load(file, Loader=yaml.FullLoader)
    for template in templates:
        print("Template:", template[":name"])
        uri_name = format_name(template[":name"])
        base_uri = "http://id.d4k.dk/dataset/bc_template/%s" % (uri_name)
        nodes["BC_TEMPLATE"].append({"name": template[":name"], "uri": base_uri})
        
        # Source
        item_uri = "http://id.d4k.dk/dataset/source/bc_template"
        record = {
            "uri": item_uri, 
            "description": "Designed for this project."
        }
        nodes["OTHER_SOURCE"].append(record)
        relationships["HAS_IDENTIFIER"].append({"from": base_uri, "to": item_uri})

        # Identifier Node and Associated Data Type
        name = format_name(template[":identified_by"][":name"])
        item_uri = "%s/%s" % (base_uri, name)
        record = {
            "name": template[":identified_by"][":name"], 
            "mandatory": template[":identified_by"][":mandatory"],
            "enabled": template[":identified_by"][":enabled"],
            "uri": item_uri
        }
        nodes["BC_ITEM"].append(record)
        relationships["HAS_ITEM"].append({"from": base_uri, "to": item_uri})
        relationships["HAS_IDENTIFIER"].append({"from": base_uri, "to": item_uri})

        parent_uri = item_uri
        name = format_name(template[":identified_by"][":data_type"][0][":name"])
        item_uri = "%s/%s" % (parent_uri, name)
        record = {
            "name": template[":identified_by"][":data_type"][0][":name"],
            "uri": item_uri
        }
        nodes["BC_DATA_TYPE"].append(record)
        relationships["HAS_DATA_TYPE"].append({"from": parent_uri, "to": item_uri})

        # Now all the items
        for item in template[":has_items"]: 
            name = format_name(item[":name"])
            item_uri = "%s/%s" % (base_uri, name)
            record = {
                "name": item[":name"], 
                "mandatory": item[":mandatory"],
                "enabled": item[":enabled"],
                "uri": item_uri
            }
            nodes["BC_ITEM"].append(record)
            relationships["HAS_ITEM"].append({"from": base_uri, "to": item_uri})
            parent_uri = item_uri
            for data_type in item[":data_type"]: 
                name = format_name(data_type[":name"])
                item_uri = "%s/%s" % (parent_uri, name)
                record = {
                    "name": data_type[":name"],
                    "uri": item_uri
                }
                nodes["BC_DATA_TYPE"].append(record)
                relationships["HAS_DATA_TYPE"].append({"from": parent_uri, "to": item_uri})

with open("../data/bc_templates_nodes.json", 'w') as outfile:
    json.dump(nodes, outfile)
with open("../data/bc_templates_relationships.json", 'w') as outfile:
    json.dump(relationships, outfile)