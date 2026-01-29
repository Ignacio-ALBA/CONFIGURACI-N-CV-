import xml.etree.ElementTree as ET

# Crear el elemento raíz del árbol XML
root = ET.Element("SCAIZEN")

# Agregar subelementos al elemento raíz
child1 = ET.SubElement(root, "child1")
child2 = ET.SubElement(root, "child2")



# Agregar atributos a los subelementos
child1.attrib["name"] = "value1"
child2.attrib["name"] = "value2"

# Crear el objeto ElementTree
tree = ET.ElementTree(root)

# Escribir el XML en un archivo
tree.write("archivo.xml")