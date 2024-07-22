''' check if every keyword in the xml file is present as KeckLFC method'''

import xml.etree.ElementTree as ET
import subprocess

# Parse the XML file
tree = ET.parse('LFCm.xml.sin')
root = tree.getroot()

# Find all keyword elements
keywords = root.findall('keyword')

keyword_names = [keyword.find('name').text for keyword in keywords]
    # print(name)

import ast
import os

def get_class_methods(filepath, classname):
    with open(filepath, "r") as file:
        file_content = file.read()
    
    tree = ast.parse(file_content)
    class_methods = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == classname:
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    class_methods.append(class_node.name)
    
    return class_methods

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
kecklfc_filepath = os.path.join(parent_dir, "KeckLFC.py")

methods = get_class_methods(kecklfc_filepath, "KeckLFC")


def find_missing_methods(method_list, class_methods):
    missing_methods = [method for method in method_list if method not in class_methods]
    return missing_methods

missing_methods = find_missing_methods(keyword_names, methods)

if len(missing_methods) > 0:
    print("List of missing methods:")
    print(missing_methods)
else:
    print("all methods are defined. good to go!")