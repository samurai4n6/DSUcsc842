import argparse
import os
import json
import csv
import plistlib
import sqlite3
import datetime
import folium
from collections import defaultdict
import sys

''' References:
https://www.usatoday.com/story/tech/nation-now/2016/07/11/while-you-track-pokmon-pokmon-go-tracks-you/86955092/
https://www.sans.org/blog/a-sneak-peek-at-pokemon-go-application-forensics/

Testing Conditions
iPhone 11.8
iOS 16.5.1
iTunes 12.9.0

Acquisition Method iTunes Backup
Acquired via Magnet Acquire
YMMV on Android
'''

# Create the argument parser and arse the command-line arguments
parser = argparse.ArgumentParser(description='Recursively search for "databaseFile:" field in plist files.')
parser.add_argument('--folder', metavar='FOLDER', required=True, help='path to the folder containing plist files')
parser.add_argument('--output', metavar='OUTPUT', help='path to the output folder')

args = parser.parse_args()

#Get the current timestamp in the YYYYMMDDhhmmss format
current_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

#Set the output folder path
output_folder_path = args.output or os.path.join(os.getcwd(), 'PokemonGo_results')
os.makedirs(output_folder_path, exist_ok=True)

#Set the output csv file name
output_csv_name = f"pokemongo_output_{current_timestamp}.csv"
output_csv_path = os.path.join(output_folder_path, output_csv_name)

#Set the output HTML file name
output_html_name = f"pokemongo_map_{current_timestamp}.html"
output_html_path = os.path.join(output_folder_path, output_html_name)

#Fields to include in the csv
fields_to_include = ['event_type', 'timestamp', 'service', 'latitude', 'longitude', 'context']

#Recursively search for the field name 'databaseFile:' in plist files
def search_plist_files(folder):
    result = []

    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith('.plist'):
                plist_file_path = os.path.join(root, file)
                with open(plist_file_path, 'rb') as plist_file:
                    plist_data = plistlib.load(plist_file)

                field_value = search_field_in_plist(plist_data, 'databaseFile')
                if field_value:
                    result.append((plist_file_path, field_value))
                else:
                    print(f"No valid Pokemon Go database found in {plist_file_path}")

    if not result:
        print("No valid Pokemon Go database found in the provided folder.")
        sys.exit(1)

    return result

#Recursively search for the field name in the plist data
def search_field_in_plist(data, field_name):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == field_name:
                return value
            elif isinstance(value, (dict, list)):
                found = search_field_in_plist(value, field_name)
                if found:
                    return found
    elif isinstance(data, list):
        for item in data:
            found = search_field_in_plist(item, field_name)
            if found:
                return found

    return None

#Recursively search for the SQLite database file and extract the JSON column
def process_database_file(folder, file_name, output_file):
    json_records = []
    valid_coordinates = defaultdict(lambda: defaultdict(list))

    for root, _, files in os.walk(folder):
        for file in files:
            if file == file_name:
                db_file_path = os.path.join(root, file)

                print(f"Found database file: {db_file_path}")

                #Connect to the SQLite database with custom text_factory
                conn = sqlite3.connect(db_file_path)
                conn.text_factory = bytes
                cursor = conn.cursor()

                #Retrieve the JSON and TIMESTAMP_MS columns from the EVENT_RECORDS table
                cursor.execute("SELECT JSON, TIMESTAMP_MS, LATITUDE, LONGITUDE FROM EVENT_RECORDS")
                rows = cursor.fetchall()

                #Extract JSON values and convert timestamp
                for row in rows:
                    json_record = row[0].decode('utf-8')
                    timestamp = row[1]
                    latitude = row[2]
                    longitude = row[3]

                    #Skip records with latitude or longitude equal to 0
                    if latitude == 0 or longitude == 0:
                        continue

                    converted_timestamp = datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

                    record = json.loads(json_record)
                    filtered_record = {field: record.get(field, '') for field in fields_to_include}
                    filtered_record['converted_timestamp'] = converted_timestamp
                    json_records.append(filtered_record)

                    valid_coordinates[(latitude, longitude)][converted_timestamp[:10]].append(filtered_record)

                #Close the database connection
                conn.close()

                #Write processed JSON records to the output CSV file
                with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fields_to_include + ['converted_timestamp'])
                    writer.writeheader()
                    writer.writerows(json_records)

                print(f"Processed JSON data written to {output_file}")
                return valid_coordinates

    print("No valid Pokemon Go database found.")
    sys.exit(1)

#Start searching for the 'databaseFile:' field in plist files
result_files = search_plist_files(args.folder)

#Process the SQLite3 database file and extract the JSON column
valid_coordinates = defaultdict(lambda: defaultdict(list))
for file_path, field_value in result_files:
    coordinates = process_database_file(args.folder, field_value, output_csv_path)
    for (latitude, longitude), records_by_date in coordinates.items():
        valid_coordinates[(latitude, longitude)].update(records_by_date)

#Create a folium map centered around the first valid coordinate
if valid_coordinates:
    map_center = list(valid_coordinates.keys())[0]
    map_obj = folium.Map(location=map_center, zoom_start=12)

    #Add markers for each unique coordinate
    for (latitude, longitude), records_by_date in valid_coordinates.items():
        popup_texts = []
        for date, records in records_by_date.items():
            popup_texts.append('<b>Date and Time: {}</b>'.format(date))
            popup_texts.append('<ul>')
            popup_texts.append('<li>{}</li>'.format(records[0]['converted_timestamp']))
            for record in records:
                popup_texts.append(
                    '<li>Context: {} | Event Type: {} | Service: {}</li>'.format(
                        record['context'],
                        record['event_type'],
                        record['service']
                    )
                )
            popup_texts.append('</ul>')
        popup_text = ' '.join(popup_texts)

        folium.Marker(
            location=(latitude, longitude),
            popup=folium.Popup(popup_text, parse_html=False),
            icon=folium.Icon(color='blue')
        ).add_to(map_obj)

    #Save the map as an HTML file
    map_obj.save(output_html_path)
    print(f"Map saved as {output_html_path}")

else:
    print("No valid coordinates found.")
