import json
import csv

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
        { "filename": "cdisc_ct/sdtm/cdisc_ct_sdtm_nodes_C66741.json", "type": "nodes" }
    ]
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
                csv_filename = "../data/csv_load/stage_%d_%s_%s.csv" % (stage_number, k.lower(), file_type)
                with open(csv_filename, mode='w', newline='') as csv_file:
                    if file_type == "nodes":
                        fields = list(v[0].keys())
                        #print([s + ":STRING" for s in fields])
                        #fieldnames = ["id:ID"] + list(v[0].keys())
                        fieldnames = ["id:ID"] + fields
                    else:
                        fieldnames = [ ":START_ID", ":END_ID" ]
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, lineterminator="\n")
                    writer.writeheader()
                    for row in v:
                        if file_type == "nodes":
                            row["id:ID"] = id_number
                            uri_to_id[row["uri"]] = id_number
                            #print("%s = %s" % (row["uri"], id_number))
                            id_number += 1
                            writer.writerow(row)
                        else:
                            new_row = { ":START_ID": uri_to_id[row["from"]], ":END_ID": uri_to_id[row["to"]] }
                            writer.writerow(new_row)

    stage_number += 1
