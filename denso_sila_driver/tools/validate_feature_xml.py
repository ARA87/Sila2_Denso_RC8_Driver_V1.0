# tools/validate_feature_xml.py

from lxml import etree
import os

def validate_xml(xml_path: str, xsd_path: str):
    with open(xsd_path, 'rb') as schema_file:
        schema_doc = etree.XML(schema_file.read())
        schema = etree.XMLSchema(schema_doc)

    with open(xml_path, 'rb') as xml_file:
        xml_doc = etree.XML(xml_file.read())

    try:
        schema.assertValid(xml_doc)
        print("✅ XML ist gültig gemäß dem SiLA 2 Schema.")
    except etree.DocumentInvalid as e:
        print("❌ XML ist NICHT gültig:")
        print(e)

if __name__ == "__main__":
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    xml_file = os.path.join(base_path, "features", "DensoRC8Control.sila.xml")
    xsd_file = os.path.join(base_path, "schema", "FeatureDefinition.xsd")

    validate_xml(xml_file, xsd_file)

    