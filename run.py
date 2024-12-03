from collections import defaultdict
import csv
import json
import io
import os
import shutil
import zipfile

# from lxml import etree
import requests

url = "https://docs.google.com/spreadsheets/d/1KBG5nGxsBq-ivVje0_U3TOr1sf8dDKWSyBxJ2qq-Wh4/export?format=csv&gid=718331842"



FIELDS = ['ID', 'Waterway', 'City, State', 'GPS Coords', 'River Miles', 'Class I?', 'Bathroom?', 'Camping?', 'Power Boats?', 'Details']

# def prettyprint(source):
#   element = etree.fromstring(source.encode())
#   return etree.tostring(element, pretty_print=True).decode()

def clean(text):
    return "".join([c for c in text if c in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz,? -.']).strip()

def clean_dict(row):
    return dict([(clean(k), v.strip()) for k, v in row.items()])

def Name(text):
  return f"<name>{clean(text)}</name>"

def Data(name, value):
    name = clean(name)
    value = clean(value)
    return f'<Data name="{name}"><value>{value}</value></Data>'

def ExtendedData(row, fields):
  return f'<ExtendedData>{"".join([Data(f, row[f]) for f in fields if f in row])}</ExtendedData>'

def DescriptionPart(name, value):
  name = clean(name)
  value = clean(value)
  return f'{name}: {value}'

def Description(row, fields):
  return f'<description><![CDATA[{"<br>".join([DescriptionPart(f, row[f]) for f in fields if f in row])}]]></description>'

def styleUrl(url):
  return f"<styleUrl>{url}</styleUrl>"

def Point(longitude, latitude):
  return f"<Point><coordinates>{longitude},{latitude},0</coordinates></Point>"

def Placemark(row, fields, icon):
  return "<Placemark>\n" + "\n".join([
    Name(row['Name']),
    Description(row, fields),
    styleUrl(icon),
    ExtendedData(row, fields),
    Point(row["Longitude"], row["Latitude"])
  ]) + "\n</Placemark>"    

def Folder(name, rows, fields, default_style):
  inner = '\n\n'.join([Placemark(row, fields, default_style) for row in rows])
  return f"\n<Folder>\n<name>{name}</name>\n{inner}\n</Folder>"



response = requests.get(url)
text = response.text

# print('text:', text)

rows = list(csv.DictReader(io.StringIO(text)))

# sanitize for cyber security purposes
rows = [clean_dict(row) for row in rows]

# dump rows for troubleshooting purposes
with open("blueways.json", "w") as f:
  json.dump(rows, f, indent=4)

# print("rows:", rows)

layer_rows = defaultdict(list)
for row in rows:
  layer = row['Layer']
  layer_rows[layer].append(row)

layer_seen_fields = defaultdict(set)
for layer, rows in layer_rows.items():
  for row in rows:
    for key, value in row.items():
      if value:
        layer_seen_fields[layer].add(key)

layer_display_fields = {}
for layer, seen_fields in layer_seen_fields.items():
  layer_display_fields[layer] = [f for f in FIELDS if f in seen_fields]
print("layer_display_fields:", layer_display_fields)

kml_output = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">,
  <Document>
    <name>Chattanooga Area Water Trails</name>
    <description><![CDATA[Comprehensive view of access points for Chattanooga area water trails.  Includes Points of Interest (POI) where services like camping, restaurants, and outfitters (rentals, shuttles, tours) can be found.  USGS river gauges are also shown. Some sightseeing opportunities are included. Suggestions and edits to this guide are welcome.  Contact Eric Fleming, 598eric@gmail.com for suggested edits, copy of data, or additional information.								<br><br>DISCLAIMER:  When paddling, be prepared for high or low water issues, wildlife, possible portages, blockages and current (strainers), and other challenges.  USGS river gauges are shown where available and can be used to check current conditions.  Everyone is responsible for their own safety.  Do not attempt a trip without the appropriate skills, equipment, and supplies.  River miles are approximate and measured from the Mouth of the river (indicated for all waterways).  Use River Miles data at various points along the same waterway to calculate approximate trip length for the planned paddle.  Subtract the River Miles values to determine the length of a trip.  		<br>]]></description>
    <Style id="icon-1502-000000-normal">
      <IconStyle>
        <scale>1</scale>
        <Icon>
          <href>images/icon-7.png</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <scale>0</scale>
      </LabelStyle>
    </Style>
    <Style id="icon-1502-000000-highlight">
      <IconStyle>
        <scale>1</scale>
        <Icon>
          <href>images/icon-7.png</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <scale>1</scale>
      </LabelStyle>
    </Style>
    <StyleMap id="icon-1502-000000">
      <Pair>
        <key>normal</key>
        <styleUrl>#icon-1502-000000-normal</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#icon-1502-000000-highlight</styleUrl>
      </Pair>
    </StyleMap>
    <Style id="icon-1535-9C27B0-labelson">
      <IconStyle>
        <scale>1</scale>
        <Icon>
          <href>images/icon-6.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="icon-1536-F9A825-labelson">
      <IconStyle>
        <scale>1</scale>
        <Icon>
          <href>images/icon-4.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="icon-1577-795548-labelson">
      <IconStyle>
        <scale>1</scale>
        <Icon>
          <href>images/icon-5.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="icon-1765-0F9D58-labelson">
      <IconStyle>
        <scale>1</scale>
        <Icon>
          <href>images/icon-3.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="icon-1899-0288D1-normal">
      <IconStyle>
        <scale>1</scale>
        <Icon>
          <href>images/icon-1.png</href>
        </Icon>
        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>
      </IconStyle>
      <LabelStyle>
        <scale>0</scale>
      </LabelStyle>
    </Style>
    <Style id="icon-1899-0288D1-highlight">
      <IconStyle>
        <scale>1</scale>
        <Icon>
          <href>images/icon-1.png</href>
        </Icon>
        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>
      </IconStyle>
      <LabelStyle>
        <scale>1</scale>
      </LabelStyle>
    </Style>
    <StyleMap id="icon-1899-0288D1">
      <Pair>
        <key>normal</key>
        <styleUrl>#icon-1899-0288D1-normal</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#icon-1899-0288D1-highlight</styleUrl>
      </Pair>
    </StyleMap>
    <Style id="icon-1899-FF5252-labelson">
      <IconStyle>
        <scale>1</scale>
        <Icon>
          <href>images/icon-2.png</href>
        </Icon>
        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>
      </IconStyle>
    </Style>
    {Folder('Flatwater Access Ramps', layer_rows['Flatwater Access Ramps'], layer_display_fields.get('Flatwater Access Ramps', FIELDS), "#icon-1899-0288D1")}
    {Folder('Class I Access Ramps', layer_rows['Class I Access Ramps'], layer_display_fields.get('Class I Access Ramps', FIELDS), "#icon-1899-FF5252-labelson")}
    {Folder('Camping Sites', layer_rows['Camping Sites'], layer_display_fields.get('Camping Sites', FIELDS), "#icon-1765-0F9D58-labelson")}
    {Folder('Outfitters', layer_rows['Outfitters'], layer_display_fields.get('Outfitters', FIELDS), "#icon-1536-F9A825-labelson")}
    {Folder('Food and Convenience Services', layer_rows['Food and Convenience Services'], layer_display_fields.get('Food and Convenience Services', FIELDS), "#icon-1577-795548-labelson")}
    {Folder('Sightseeing Opportunities', layer_rows['Sightseeing Opportunities'], layer_display_fields.get('Sightseeing Opportunities', FIELDS), "#icon-1535-9C27B0-labelson")}
    {Folder('USGS River Gauges', layer_rows['USGS River Gauges'], layer_display_fields.get('USGS River Gauges', FIELDS), "#icon-1502-000000")}
  </Document>
</kml>
'''

# print("kml_output", kml_output)

# prettify xml
# kml_output = prettyprint(kml_output)

with open("./data/doc.kml", "w") as f:
  f.write(kml_output)

shutil.make_archive("./blueways.kmz", 'zip', "./data")
os.replace("blueways.kmz.zip", "blueways.kmz")