import xml.etree.ElementTree as ET
from lxml import etree
from collections import OrderedDict
import copy
import pandas as pd

def iter_docs(author):
    # author_attr = author.attrib
    for doc in author.iterfind('.//item'):

        entry = OrderedDict()
        for x in doc.iterfind('.//field'):
            x_dict = copy.copy(doc.attrib)
            x_dict.update(x.attrib)
            entry[x_dict['name']] = x.text
        yield(entry)

def extract(source_path):
    # Define xml parser (to ignore errors)
    parser = etree.XMLParser(recover=True)

    # Read xml file
    with open(source_path, 'r') as the_file:
        xml_data = the_file
        tree = ET.parse(xml_data, parser=parser) #create an ElementTree object
        the_file.close()

    # Transform to df
    return pd.DataFrame(list(iter_docs(tree.getroot())))

# Used to generate xml, see below
def func(row):
    xml = ['<item>']
    for field in row.index:
        xml.append('  <field name="{0}">{1}</field>'.format(field, row[field]))
    xml.append('</item>')
    return '\n'.join(xml)

def generate_xml_from_df(df, target_path):
    # Generate xml data
    xml_output = '\n'.join(df.apply(func, axis=1))

    # Save xml data in new file
    with open(target_path, 'w') as the_file:
        the_file.write(xml_output)
        the_file.close()
