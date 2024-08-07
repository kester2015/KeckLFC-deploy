import xml.etree.ElementTree as ET
import subprocess
'''
This is a simple script to strip the <period> node in the keyword xml files
and copy the xml file to irastrocombbuild
'''

# Parse the XML file
tree = ET.parse('LFCm.xml.sin')
root = tree.getroot()

# Find all keyword elements
keywords = root.findall('keyword')

# Remove the <period> node from each keyword element
for keyword in keywords:
    period = keyword.find('period')
    if period is not None:
        keyword.remove(period)

for keyword in keywords:
    period = keyword.find('fastperiod')
    if period is not None:
        keyword.remove(period)

# Write the modified XML to a new file
tree.write('LFC.xml.sin')
# subprocess.run(["scp", "LFC.xml.sin", "combbld@irastrocombbuild.keck.hawaii.edu:/kroot/src/kss/astrocomb/ktlxml/"])
# subprocess.run(["scp", "LFCm.xml.sin", "combbld@irastrocombbuild.keck.hawaii.edu:/kroot/src/kss/astrocomb/ktlxml/"])
# subprocess.run(["scp", "nslfcd", "combbld@irastrocombbuild.keck.hawaii.edu:/kroot/src/kss/astrocomb/dispatcher/nslfcd"])
# subprocess.run(["scp", "KtlIce.ice", "combbld@irastrocombbuild.keck.hawaii.edu:/kroot/src/kss/astrocomb/KtlIce.ice"])
print("Warning: scp to irastrocombbuild is not performed")