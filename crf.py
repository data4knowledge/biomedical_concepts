from neo4j import GraphDatabase
import lxml.etree as ElementTree
import datetime

from numpy import rec
#import yaml

# Get a timestamp and set the ODM namespace.

odm_datatype = { "CD": { "code": "text" }, "PQR": { "value": "float", "code": "text" }, "DATETIME": { "value": "date" } }

def odm(oid):
    odm_namespace = "http://www.cdisc.org/ns/odm/v1.3"
    ElementTree.register_namespace("odm", odm_namespace)
    exported_at = datetime.datetime.now().replace(microsecond=0).isoformat()
    nsmap = {None: odm_namespace}
    odm = ElementTree.Element("{%s}ODM" % (odm_namespace), nsmap=nsmap)
    odm.set("FileOID", oid) 
    odm.set("FileType", "Snapshot") 
    odm.set("Granularity", "Metadata") 
    odm.set("CreationDateTime", exported_at)
    return odm

def study(parent, oid):
    element = ElementTree.SubElement(parent, "{%s}Study" % (odm_namespace))
    element.set("OID", oid)
    return element

def global_variables(parent):
    element = ElementTree.SubElement(parent, "{%s}GlobalVariables" % (odm_namespace))
    return element

def study_name(parent, text):
    element = ElementTree.SubElement(parent, "{%s}StudyName" % (odm_namespace))
    element.text = text
    return element

def study_description(parent, text):
    element = ElementTree.SubElement(parent, "{%s}StudyDescription" % (odm_namespace))
    element.text = text
    return element

def protocol_name(parent, text):
    element = ElementTree.SubElement(parent, "{%s}ProtocolName" % (odm_namespace))
    element.text = text
    return element

def basic_definitions(parent):
    element = ElementTree.SubElement(parent, "{%s}BasicDefinitions" % (odm_namespace))
    return element

def metadata_version(parent, oid, name):
    element = ElementTree.SubElement(parent, "{%s}MetaDataVersion" % (odm_namespace))
    element.set("OID", oid)
    element.set("Name", name)
    return element

def protocol(parent):
    element = ElementTree.SubElement(parent, "{%s}Protocol" % (odm_namespace))
    return element

def study_event_ref(parent, oid):
    element = ElementTree.SubElement(parent, "{%s}StudyEventRef" % (odm_namespace))
    element.set("StudyEventOID", oid)
    element.set("Mandatory", "Yes")
    element.set("OrderNumber", "1")
    return element

def study_event_def(parent, oid, name):
    element = ElementTree.SubElement(parent, "{%s}StudyEventDef" % (odm_namespace))
    element.set("OID", oid)
    element.set("Name", name)
    element.set("Repeating", "No")
    element.set("Type", "Scheduled")
    return element

def blank_form(study_event_def, form_name, the_forms, the_item_groups, the_items, the_code_lists):
    form = ElementTree.Element("{%s}FormDef" % (odm_namespace))
    form.set("OID", "DDF_F_%s" % (len(the_forms) + 1)) 
    form.set("Name", form_name) 
    form.set("Repeating", "No") 
    the_forms.append(form)

def form_ref(parent, form_oid, order_number):
    element = ElementTree.SubElement(parent, "{%s}FormRef" % (odm_namespace))
    element.set("FormOID", form_oid)
    element.set("Mandatory", "Yes")
    element.set("OrderNumber", order_number)
    return element

def item_group_ref(parent, item_group_oid, order_number):
    element = ElementTree.SubElement(parent, "{%s}ItemGroupRef" % (odm_namespace))
    element.set("ItemGroupOID", item_group_oid) 
    element.set("OrderNumber", order_number) 
    return element

def form(name):
    element = ElementTree.Element("{%s}FormDef" % (odm_namespace))
    element.set("OID", "DDF_F_%s" % (len(the_forms) + 1)) 
    element.set("Name", name) 
    element.set("Repeating", "No") 
    the_forms.append(element)
    return element

def item_group(name):
    element = ElementTree.Element("{%s}ItemGroupDef" % (odm_namespace))
    element.set("OID", "DDF_F_%s_IG" % (len(the_item_groups) + 1)) 
    element.set("Name", name) 
    element.set("Repeating", "No")
    the_item_groups.append(element)
    return element

def item_ref(parent, item_oid, order):
    element = ElementTree.SubElement(parent, "{%s}ItemRef" % (odm_namespace))
    element.set("ItemOID", item_oid) 
    element.set("Mandatory", "Yes")
    element.set("OrderNumber", order)
    return element
    
def item(name, data_type, question_text):
    element = ElementTree.Element("{%s}ItemDef" % (odm_namespace))
    element.set("OID", "DDF_F_%s_IG_I" % (len(the_forms) + 1)) 
    element.set("Name", name) 
    element.set("Datatype", data_type) 
    question(element, question_text)
    the_items.append(element)
    return element

def question(parent, text):
    element = ElementTree.SubElement(parent, "{%s}Question" % (odm_namespace))
    translated_text(element, text)
    return element

def translated_text(parent, text):
    element = ElementTree.SubElement(parent, "{%s}TranslatedText" % (odm_namespace))
    element.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "en"
    element.text = "%s" % (text)
    return element

def code_list(oid):
    element = ElementTree.Element("{%s}CodeList" % (odm_namespace))
    element.set("OID", oid) 
    element.set("DataType", "text") 
    element.set("Name", "To Be Provided")
    the_code_lists.append(code_list)
    return element

def code_list_ref():
    element = ElementTree.SubElement(item_def, "{%s}CodeListRef" % (odm_namespace))
    element.set("CodeListOID", "DDF_F_%s_IG_I_%s_CL" % (len(the_forms) + 1, index)) 

def code_list_item(parent, coded, order_number):
    element = ElementTree.SubElement(parent, "{%s}CodeListItem" % (odm_namespace))
    element.set("CodedValue", coded) 
    element.set("OrderNumber", order_number)
    return element
    
def decode(parent):
    element = ElementTree.SubElement(parent, "{%s}Decode" % (odm_namespace))
    return element

def create_study_form(name):
    with driver.session() as session:
        query = """CREATE (n:STUDY_FORM {name: '%s'})""" % (name) 
        result = session.run(query)
    driver.close()

def add_group_to_form(form_name, group_name):
    with driver.session() as session:
        query = """MATCH (n:STUDY_FORM {name: '%s'})
            CREATE (n)-[:HAS_GROUP]->(:STUDY_FORM_GROUP {name: '%s'})
        """ % (form_name, group_name) 
        result = session.run(query)
    driver.close()

def add_bc_to_group(group_name, bc_name):
    with driver.session() as session:
        query = """MATCH (n:STUDY_FORM_GROUP {name: '%s'}), (m:STUDY_BC_INSTANCE {name: '%s'})
            CREATE (n)-[:HAS_BC]->(m)
        """ % (group_name, bc_name) 
        result = session.run(query)
    driver.close()

def get_form_groups(name):
    the_results = []
    with driver.session() as session:
        query = """MATCH (sf:STUDY_FORM {name: '%s'})-[]->(sfg:STUDY_FORM_GROUP)
            RETURN sfg.name as group
        """ % (name) 
        result = session.run(query)
        for record in result:
            the_results.append(record["group"])
    driver.close()
    return the_results

def get_form_group_items(form_name, group_name):
    the_results = []
    with driver.session() as session:
        query = """MATCH (sf:STUDY_FORM {name: '%s'})-[]->(sfg:STUDY_FORM_GROUP {name: '%s'})-[]->(bc:STUDY_BC_INSTANCE)
            -[:HAS_ITEM]->(bci:BC_ITEM {enabled: "True"})-[*]->(bcp:BC_DATA_TYPE_PROPERTY)
            WHERE bcp.name = "value" OR bcp.name = "code"
            RETURN DISTINCT bci.name as item
        """ % (form_name, group_name) 
        result = session.run(query)
        for record in result:
            the_results.append(record["item"])
    driver.close()
    return the_results

def get_form_item_properties(form_name, group_name, item_name):
    the_results = []
    with driver.session() as session:
        query = """MATCH (sf:STUDY_FORM {name: '%s'})-[]->(sfg:STUDY_FORM_GROUP {name: '%s'})-[]->(bc:STUDY_BC_INSTANCE)
            -[:HAS_ITEM]->(bci:BC_ITEM {enabled: "True", name: '%s'})-[*]->(bcp:BC_DATA_TYPE_PROPERTY)
            WHERE bcp.name = "value" OR bcp.name = "code"
            RETURN DISTINCT bcp.name as property, bcp.uri as uri
        """ % (form_name, group_name, item_name) 
        result = session.run(query)
        for record in result:
            the_results.append({ "name": record["property"], "uri": record["uri"] })
    driver.close()
    return the_results

# DB Read
# -------

driver = GraphDatabase.driver("neo4j+s://b0320659.databases.neo4j.io", auth=("neo4j", "x93TyR6B0pkDc5sHp6gvxAbCeCEOuUQQc2x5NDTwg-M"))

#create_study_form("Demographics")
#add_group_to_form("Demographics", "Main Group")
#add_bc_to_group("Main Group", "Age")
groups = get_form_groups("Demographics")
print(groups)
for group in groups:
    items = get_form_group_items("Demographics", group)
    print(items)
    for the_item in items:
        properties = get_form_item_properties("Demographics", group, the_item)
        for property in properties:
            print("%s = %s, %s " % (the_item, property["name"], property["uri"]))

# Set of arrays for holding the new items
the_forms = []
the_item_groups = []
the_items = []
the_code_lists = []

# Build the ODM
#root = odm() 
#st = study(odm, "DDR_S_001")
#gv = global_variables(st)
#study_name(gv, "")
#study_description(gv, "")
#protocol_name(gv, "")
#bd = basic_definitions(st)
#mdv = metadata_version(st, "DDR_MDV_001", "DDR Metadata")
#sed = study_event_def(mdv, "DDR_SED_001", "")
#pr = protocol(mdv)
#ser = study_event_ref(pr, "DDR_SE_001")
#sed = study_event_def(mdv, "DDR_SE_001", "CRF Book")



#                        for ct in property[":has_coded_value"]:
#                        cli_info = cdisc_ct(ct[":cl"], ct[":cli"])
#"DDF_ODM_001"
#"DDF_S_001"

# Add the items into the core ODM
for form in the_forms:
    metadata_version.append(form)
for item_group in the_item_groups:
    metadata_version.append(item_group)
for item in the_items:
    metadata_version.append(item)
for code_list in the_code_lists:
    metadata_version.append(code_list)

# Write out the XML merged file
#the_odm = ElementTree.ElementTree(root)
#the_odm.write("ddf_crf.xml", xml_declaration=True, encoding='utf-8', method="xml")

# Transform the XML into an HTML rendering using a style sheet
#xslt = ElementTree.parse("crf.xsl")
#transform = ElementTree.XSLT(xslt)
#the_crf = transform(odm)
#the_crf.write("study.html", xml_declaration=True, encoding='utf-8', method="html")