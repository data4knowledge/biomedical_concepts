import json
import csv

filenames = ["canonical_model_nodes.json", "cdisc_ct_nodes.json", "fhir_data_type_nodes.json"]
for filename in filenames:
    with open("../data/%s" % (filename)) as json_file:
        print(filename)
        data = json.load(json_file)
        for k, v in data.items():
            #print(k)
            #print(v)
            with open("../data/%s_nodes.csv" % (k.lower()), mode='w') as csv_file:
                fieldnames = ["label"] + list(v[0].keys())
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for row in v:
                    row["label"] = k
                    writer.writerow(row)
