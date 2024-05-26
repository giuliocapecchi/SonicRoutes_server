import xml.etree.ElementTree as ET
import random

def remove_namespace(elem):
    if isinstance(elem, str):
        return elem
    # Rimuovi il namespace dagli attributi
    elem.attrib = {k.split('}')[1] if '}' in k else k: v for k, v in elem.attrib.items()}
    # Rimuovi il namespace dal tag
    elem.tag = elem.tag.split('}')[1] if '}' in elem.tag else elem.tag
    # Ricorsivamente rimuovi il namespace dai figli
    for child in elem:
        remove_namespace(child)
    return elem


file_path='data/grafo_completo.graphml'
tree = ET.parse(file_path)
root = tree.getroot()
remove_namespace(root)

for edge in root.findall('.//edge'):
    # prendo count
    print(edge.findall('data')[1].text)
    edge.findall('data')[1].text = str(random.randint(0, 100))
    print(edge.findall('data')[1].text)

    # prendo amplitude
    edge.findall('data')[0].text = str(random.uniform(0, 6000))

tree.write(file_path)
