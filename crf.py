from mmap import MADV_DONTNEED
from neo4j import GraphDatabase
import lxml.etree as ElementTree
import datetime
import yaml
import os

# Get a timestamp and set the ODM namespace.
odm_datatype = { "CD": { "code": "text" }, "PQR": { "value": "float", "code": "text" }, "DATETIME": { "value": "date" } }
odm_namespace = "http://www.cdisc.org/ns/odm/v1.3"
NEO4J_TEST_PWD = os.getenv('NEO4J_TEST')

# Series of methods to build ODM. Pretty simple.
def odm(oid):
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

def form_def(name):
    element = ElementTree.Element("{%s}FormDef" % (odm_namespace))
    element.set("OID", "DDF_F_%s" % (len(the_forms) + 1)) 
    element.set("Name", name) 
    element.set("Repeating", "No") 
    the_forms.append(element)
    return element

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

def item_group_def(name):
    element = ElementTree.Element("{%s}ItemGroupDef" % (odm_namespace))
    element.set("OID", "DDR_IG_%s" % (len(the_item_groups) + 1)) 
    element.set("Name", name) 
    element.set("Repeating", "No")
    the_item_groups.append(element)
    return element

def item_ref(parent, oid, order):
    element = ElementTree.SubElement(parent, "{%s}ItemRef" % (odm_namespace))
    element.set("ItemOID", oid) 
    element.set("Mandatory", "Yes")
    element.set("OrderNumber", order)
    return element
    
def item_def(name, data_type, length, question_text):
    element = ElementTree.Element("{%s}ItemDef" % (odm_namespace))
    element.set("OID", "DDF_I_%s" % (len(the_items) + 1)) 
    element.set("Name", name) 
    element.set("Datatype", data_type) 
    element.set("Length", length) 
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

def code_list():
    element = ElementTree.Element("{%s}CodeList" % (odm_namespace))
    element.set("OID", "DDF_CL_%s" % (len(the_code_lists) + 1)) 
    element.set("DataType", "text") 
    element.set("Name", "To Be Provided")
    the_code_lists.append(element)
    return element

def code_list_ref(parent, oid):
    element = ElementTree.SubElement(parent, "{%s}CodeListRef" % (odm_namespace))
    element.set("CodeListOID", oid) 

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

def get_forms():
    the_results = []
    with driver.session() as session:
        query = """MATCH (sf:STUDY_FORM) RETURN sf.name as form"""
        result = session.run(query)
        for record in result:
            the_results.append(record["form"])
    driver.close()
    return the_results

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
            -[:HAS_ITEM]->(bci:BC_ITEM {enabled: "True", collect: "True"})-[*]->(bcp:BC_DATA_TYPE_PROPERTY)
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

def get_form_property_cli(property_uri):
    the_results = []
    with driver.session() as session:
        query = """MATCH (bcp:BC_DATA_TYPE_PROPERTY {uri: '%s'})<-[]-(:BC_DATA_TYPE)-[]->(sc:SKOS_CONCEPT)
            RETURN DISTINCT sc.notation as submission, sc.pref_label as pt
        """ % (property_uri) 
        result = session.run(query)
        for record in result:
            the_results.append({ "submission": record["submission"], "pt": record["pt"]  })
    driver.close()
    return the_results

with open("data/form/bc_extra.yaml") as file:
    extra_info = yaml.load(file, Loader=yaml.FullLoader)

driver = GraphDatabase.driver("neo4j+s://b0320659.databases.neo4j.io", auth=("neo4j", NEO4J_TEST_PWD))
print(driver)
#create_study_form("Demographics")
#add_group_to_form("Demographics", "Main Group")
#add_bc_to_group("Main Group", "Age")

# Set of arrays for holding the new items
the_forms = []
the_item_groups = []
the_items = []
the_code_lists = []

root = odm("DDR")
st = study(root, "DDR_S_001")
gv = global_variables(st)
study_name(gv, "DDR")
study_description(gv, "Something")
protocol_name(gv, "Something")
bd = basic_definitions(st)
mdv = metadata_version(st, "DDR_MDV_001", "DDR Metadata")
pr = protocol(mdv)
ser = study_event_ref(pr, "DDR_SE_001")
sed = study_event_def(mdv, "DDR_SE_001", "CRF Book")

forms= get_forms()
for f_index, form in enumerate(forms):
    fd = form_def(form)
    form_ref(sed, fd.get("OID"), "%s" % (f_index + 1 ))
    groups = get_form_groups(form)
    print(groups)
    for g_index, group in enumerate(groups):
        igd = item_group_def(group)
        item_group_ref(fd, igd.get("OID"), "%s" % (g_index + 1 ))
        items = get_form_group_items(form, group)
        print(items)
        for i_index, the_item in enumerate(items):
            properties = get_form_item_properties(form, group, the_item)
            for p_index, property in enumerate(properties):
                details = extra_info[property["uri"]]
                id = item_def(property["name"], details["data_type"], details["length"], details["question_text"])
                item_ref(igd, id.get("OID"), "%s" % (p_index + 1))
                print("%s = %s, %s " % (the_item, property["name"], property["uri"]))
                if property["name"] == "code":
                    clis= get_form_property_cli(property["uri"])
                    cl = code_list()
                    code_list_ref(id, cl.get("OID"))
                    for cl_index, cli in enumerate(clis):
                        print("%s" % cli["submission"]) 
                        cl_item = code_list_item(cl, cli["submission"],  "%s" % (cl_index + 1))
                        dec = decode(cl_item)
                        translated_text(dec, cli["pt"])


# Add the items into the core ODM
for form in the_forms:
    mdv.append(form)
for item_group in the_item_groups:
    mdv.append(item_group)
for item in the_items:
    mdv.append(item)
for clx in the_code_lists:
    mdv.append(clx)

# Write out the XML merged file
the_odm = ElementTree.ElementTree(root)
the_odm.write("ddf_crf.xml", xml_declaration=True, encoding='utf-8', method="xml")

# Transform the XML into an HTML rendering using a style sheet
xslt = ElementTree.parse("crf.xsl")
transform = ElementTree.XSLT(xslt)
the_crf = transform(root)
the_crf.write("study.html", xml_declaration=True, encoding='utf-8', method="html")