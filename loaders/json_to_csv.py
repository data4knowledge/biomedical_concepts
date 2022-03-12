import json
import csv

stages = [
    [ 
        { "filename": "fhir_data_type_nodes.json", "type": "nodes" },
        { "filename": "fhir_data_type_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "canonical_model_nodes.json", "type": "nodes" },
        { "filename": "canonical_model_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "cdisc_ct_nodes.json", "type": "nodes" },
        { "filename": "cdisc_ct_relationships.json", "type": "relationships" },
    ],
]

uri_to_id = {}
id_number = 1
stage_number = 1
for stage in stages:
    for file_item in stage:
        file_type = file_item["type"]
        with open("../data/%s" % (file_item["filename"])) as json_file:
            print(file_item["filename"])
            data = json.load(json_file)
            for k, v in data.items():
                csv_filename = "../data/stage_%d_%s_%s.csv" % (stage_number, k.lower(), file_type)
                with open(csv_filename, mode='w') as csv_file:
                    if file_type == "nodes":
                        fieldnames = ["id:ID"] + list(v[0].keys())
                    else:
                        fieldnames = [ ":START_ID", ":END_ID" ]
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                    writer.writeheader()
                    for row in v:
                        if file_type == "nodes":
                            row["id:ID"] = id_number
                            uri_to_id[row["uri"]] = id_number
                            print("%s = %s" % (row["uri"], id_number))
                            id_number += 1
                            writer.writerow(row)
                        else:
                            new_row = { ":START_ID": uri_to_id[row["from"]], ":END_ID": uri_to_id[row["to"]] }
                            writer.writerow(new_row)

    stage_number += 1
