#====================== #
#   Imports libraries   #
#=======================#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""
audit the OSMFILE and find the possible data-formating problems in that file. Use the variable 'mapping' to reflect the changes needed 
to fix the unexpected street types to the appropriate ones in the expected list. Print out the original street names and the new street
names after updating.
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "denver_colorado.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Alley", "Park", "Way", "Walk", "Circle", "Highway",
            "Plaza", "Center", "East", "West", "South", "North"]


mapping = { "Ave": "Avenue",
            "Ave.": "Avenue",
            "avenue": "Avenue",
            "ave": "Avenue",
           "Blvd": "Boulevard",
           "Blvd.": "Boulevard",
           "Blvd,": "Boulevard",
           "BLVD": "Boulevard",
           "blvd.": "Boulevard",
           "blvd,": "Boulevard",
           "Boulavard": "Boulevard",
           "Boulvard": "Boulevard",
           "Ct": "Court",
           "ct": "Court",
           "Dr": "Drive",
           "Dr.": "Drive",
           "dr": "Drive",
           "E": "East", 
           "Hwy": "Highway",
           "hwy": "Highway",
           "Ln": "Lane",
           "Ln.": "Lane",
           "ln": "Lane",
           "N": "North",
           "n": "North",
           "pkway": "Parkway",
           "pkwy": "Parkway",
           "Pkwy": "Parkway",
           "Prkwy": "Parkway",
           "prkwy": "Parkway",
           "parkway": "Parkway",
           "Pl": "Place",
           "pl": "Place",
           "Plz": "Plaza",
           "Rd": "Road", 
           "Rd.": "Road",
           "rd": "Road",
           "RD": "Road",
           "St": "Street",
           "St.": "Street",
           "st": "Street",
           "street": "Street",
           "square": "Square",
           "s": "South",
           "S": "South",
           "w": "West",
           "W": "West"
          }


"""This code finds all the streets that need to be changed"""
def audit_street_type(street_types, street_name):
      m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

"""This code audits the OSM file and finds the street elements"""
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types

"""This code fixes street names"""
def update_name(name, mapping):
    name_split = name.split(' ')
    name_new = ''
    for item in name_split:
        if item in mapping:
            item_new = mapping[item]
            name_new = name_new + item_new + ' '
        else:
            name_new = name_new + item + ' '
    name = name_new.strip(' ')
    return name


def test():
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name

if __name__ == '__main__':
    test()