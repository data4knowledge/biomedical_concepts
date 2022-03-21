import os
import json
import csv

uri_to_id = {}
id_number = 1

stages = [
    [ 
        { "filename": "fhir/fhir_data_type_nodes.json", "type": "nodes" },
        { "filename": "fhir/fhir_data_type_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "canonical/canonical_model_nodes.json", "type": "nodes" },
        { "filename": "canonical/canonical_model_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "cdisc_ct/sdtm/cdisc_ct_sdtm_nodes.json", "type": "nodes" },
        { "filename": "cdisc_ct/sdtm/cdisc_ct_sdtm_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "cdisc_ct/adam/cdisc_ct_adam_nodes.json", "type": "nodes" },
        { "filename": "cdisc_ct/adam/cdisc_ct_adam_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "cdisc_ct/cdash/cdisc_ct_cdash_nodes.json", "type": "nodes" },
        { "filename": "cdisc_ct/cdash/cdisc_ct_cdash_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "cdisc_ct/define-xml/cdisc_ct_define-xml_nodes.json", "type": "nodes" },
        { "filename": "cdisc_ct/define-xml/cdisc_ct_define-xml_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "cdisc_ct/glossary/cdisc_ct_glossary_nodes.json", "type": "nodes" },
        { "filename": "cdisc_ct/glossary/cdisc_ct_glossary_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "cdisc_ct/protocol/cdisc_ct_protocol_nodes.json", "type": "nodes" },
        { "filename": "cdisc_ct/protocol/cdisc_ct_protocol_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "cdisc_ct/send/cdisc_ct_send_nodes.json", "type": "nodes" },
        { "filename": "cdisc_ct/send/cdisc_ct_send_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "bc/bc_templates_nodes.json", "type": "nodes" },
        { "filename": "bc/bc_templates_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "bc/bc_instances_nodes.json", "type": "nodes" },
        { "filename": "bc/bc_instances_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "study/study_1_nodes.json", "type": "nodes" },
        { "filename": "study/study_1_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "cdisc_sdtm/cdisc_sdtm_ig_nodes.json", "type": "nodes" },
        { "filename": "cdisc_sdtm/cdisc_sdtm_model_nodes.json", "type": "nodes" },
        { "filename": "cdisc_sdtm/cdisc_sdtm_ig_relationships.json", "type": "relationships" },
        { "filename": "cdisc_sdtm/cdisc_sdtm_model_relationships.json", "type": "relationships" },
    ],
    [ 
        { "filename": "sponsor_ct/sponsor_ct_nodes.json", "type": "nodes" },
        { "filename": "sponsor_ct/sponsor_ct_relationships.json", "type": "relationships" },
    ]
]
code_lists = [
    [ 
        { "filename": "cdisc_ct/sdtm/cdisc_ct_sdtm_nodes_C66741.json", "type": "nodes" },
        { "filename": "cdisc_ct/sdtm/cdisc_ct_sdtm_nodes_C66770.json", "type": "nodes" }
    ]
]

def delete_dir(dir_path):
    root_path = os.path.dirname( __file__ )
    root_path = os.path.dirname(root_path) 
    target_dir = "%s/%s" % (root_path, dir_path)
    files = os.listdir(target_dir)
    for f in files:
        os.remove("%s/%s" % (target_dir, f))
        print("Deleted %s" % (f))

def process_file(file_item, the_data, csv_filename, id_field="id:ID"):
    if len(the_data) == 0:
        return 
    global id_number
    file_type = file_item["type"]
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode='a', newline='') as csv_file:
        if file_type == "nodes":
            fields = list(the_data[0].keys())
            fieldnames = [id_field] + fields
        else:
            fieldnames = [ ":START_ID", ":END_ID" ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        for row in the_data:
            if file_type == "nodes":
                row[id_field] = id_number
                uri_to_id[row["uri"]] = id_number
                id_number += 1
                writer.writerow(row)
            else:
                new_row = { ":START_ID": uri_to_id[row["from"]], ":END_ID": uri_to_id[row["to"]] }
                writer.writerow(new_row)

# Delete all the csv files. Do this in case some are no longer used.
delete_dir("data/csv_load")

# Now process the files
stage_number = 1
for stage in stages:
    for file_item in stage:
        with open("../data/%s" % (file_item["filename"])) as json_file:
            print(file_item["filename"])
            data = json.load(json_file)
            for k, v in data.items():
                csv_filename = "../data/csv_load/stage_%d_%s_%s.csv" % (stage_number, k.lower(), file_item["type"])
                process_file(file_item, v, csv_filename)
    stage_number += 1

# Process the code list files.
for code_list in code_lists:
    for file_item in code_list:
        filename = "../data/%s" % (file_item["filename"])
        output_filename = file_item["filename"].split("/")[-1]
        output_filename = output_filename.split(".")[0]
        with open(filename) as json_file:
            print(file_item["filename"])
            data = json.load(json_file)
            for k, v in data.items():
                csv_filename = filename = "../data/csv_load/%s.csv" % (output_filename)
                process_file(file_item, v, csv_filename, "id")