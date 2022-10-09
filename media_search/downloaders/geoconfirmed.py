# https://www.google.com/maps/d/kml?forcekml=1&mid=10YK14-QB25penu8jeS4hBVarzGKZsVgj
# import xml.etree.cElementTree as ET
#
# def parseXML(file_name):
#     # Parse XML with ElementTree
#     tree = ET.ElementTree(file=file_name)
#     print(tree.getroot())
#     root = tree.getroot()
#     print("tag=%s, attrib=%s" % (root.tag, root.attrib))
#
#     # get the information via the children!
#     print("-" * 25)
#     print("Iterating using getchildren()")
#     print("-" * 25)
#     users = root.getchildren()
#     for user in users:
#         user_children = user.getchildren()
#         for user_child in user_children:
#             print("%s=%s" % (user_child.tag, user_child.text))
#
#
# def parse(filename):
#     tree = ET.ElementTree(file=filename)
#     root = tree.getroot()
#     places = root.findall('.//{http://www.opengis.net/kml/2.2}Folder')
#     # for line in root.iter('*'):
#     #     print(line.text)
#     for p in places:
#         print(p.__dir__())
#
#
# if __name__ == "__main__":
#     # parseXML("geoconfirmed.kml")
#     parse("geoconfirmed.kml")

import xmltodict
with open('geoconfirmed.kml', 'r') as f:
    doc = xmltodict.parse(f.read())

# print(doc['kml']['Document'][0])  # ['Folder'])
import pprint as pp
pp.pprint(doc['kml']['Document']['Folder'][3]['Placemark'][0], indent=2)

# import json
# print(json.dumps(doc))
