import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSMFILE = "denver_colorado_osm.xml"  # Replace this with your osm file
SAMPLE_FILE = "denver_colorado.osm"


def get_element(osm_file, tags=('node', 'way', 'relation')):
     context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every 10th top level element
    for i, element in enumerate(get_element(OSMFILE)):
        if i % 100 == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')