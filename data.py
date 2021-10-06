import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

OSM_PATH = "denver_colorado.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.Schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


mapping = {"St": "Street",'Rd':'Road','Ave':'Avenue', 'Dr':'Drive', 'Blvd':'Boulevard', 'Fwy':'Freeway','Pkwy':'Parkway'}
def auditpostcode(value):
    value = str(value)
    p = value.find('77')
    if p == -1:
        return None
    else:
        return value[p:p+5]

def auditstreet(name, mapping):
        words = name.split()
        for i in range(len(words)):
            if words[i] in mapping:
                if i != 0 and words[i-1].lower() not in ['suite', 'ste.', 'ste']:
                    words[i] = mapping[words[i]]
        name = " ".join(words)
        return name


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []
    if element.tag == 'node':
        for key in node_attr_fields:
            node_attribs[key] = element.attrib[key]
        for tag in element.iter("tag"):
            temdic = {}
            temdic['id'] = element.attrib['id']
            temdic['value'] = tag.attrib['v']
            p = tag.attrib['k'].find(':')
            if p == -1:
                temdic['key'] = tag.attrib['k']
                temdic['type'] = 'regular'
            else:
                temdic['key'] = tag.attrib['k'][p + 1:]
                temdic['type'] = tag.attrib['k'][:p]
            if temdic['key'] == 'postcode':
                tem = auditpostcode(temdic['value'])
                if tem:
                    temdic['value'] = tem
                    tags.append(temdic)
            elif temdic['key'] == 'street':
                tem = auditstreet(temdic['value'], mapping)
                temdic['value'] = tem
                tags.append(temdic)
            else:
                tags.append(temdic)
    elif element.tag == 'way':
        for key in way_attr_fields:
            way_attribs[key] = element.attrib[key]
        position = 0
        for tag in element.iter("nd"):
            temdic = {}
            temdic['id'] = element.attrib['id']
            temdic['node_id'] = tag.attrib['ref']
            temdic['position'] = str(position)
            way_nodes.append(temdic)
            position += 1
        for tag in element.iter("tag"):
            temdic = {}
            temdic['id'] = element.attrib['id']
            temdic['value'] = tag.attrib['v']
            p = tag.attrib['k'].find(':')
            if p == -1:
                temdic['key'] = tag.attrib['k']
                temdic['type'] = 'regular'
            else:
                temdic['key'] = tag.attrib['k'][p + 1:]
                temdic['type'] = tag.attrib['k'][:p]
            if temdic['key'] == 'postcode':
                tem = auditpostcode(temdic['value'])
                if tem:
                    temdic['value'] = tem
                    tags.append(temdic)
            elif temdic['key'] == 'street':
                tem = auditstreet(temdic['value'], mapping)
                temdic['value'] = tem
                tags.append(temdic)
            else:
                tags.append(temdic)
    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}



def get_element(osm_file, tags=('node', 'way', 'relation')):

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
                                                    k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in
                                                    row.iteritems()
                                                    })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def process_map(file_in, validate):
    with codecs.open(NODES_PATH, 'w') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'w') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()
        # validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    process_map(OSM_PATH, validate=True)