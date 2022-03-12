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

stage_number = 1
for stage in stages:
    for file_item in stage:
        with open("../data/%s" % (file_item["filename"])) as json_file:
            print(file_item["filename"])
            data = json.load(json_file)
            for k, v in data.items():
                csv_filename = "../data/stage_%d_%s_%s.csv" % (stage_number, k.lower(), file_item["type"])
                with open(csv_filename, mode='w') as csv_file:
                    #fieldnames = ["label"] + list(v[0].keys())
                    fieldnames = list(v[0].keys())
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in v:
                        #row["label"] = k
                        writer.writerow(row)
    stage_number += 1
