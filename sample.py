import xml.etree.cElementTree as ET # Use cElementTree or lxml if too slow

OSMFILE = "denver_colorado_osm.xml"  # Replace this with your osm file


for event,element in ET.iterparse(OSMFILE):
    print element.tag
    print element.attrib
    break

SAMPLE_FILE = "denver_colorado.osm"

k = 100 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSMFILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')