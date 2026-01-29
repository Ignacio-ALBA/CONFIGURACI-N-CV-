import xml.etree.ElementTree as ET

# Crear el elemento raíz
root = ET.Element("Datos")

# Agregar elementos con acentos
ET.SubElement(root, "Nombre").text = "José"
ET.SubElement(root, "Ciudad").text = "Mérida"

# Convertir a cadena XML
xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')

# Mostrar el resultado
print(xml_str)

# (Opcional) Guardar en un archivo XML
with open("datos.xml", "w", encoding="utf-8") as f:
    f.write(xml_str)
