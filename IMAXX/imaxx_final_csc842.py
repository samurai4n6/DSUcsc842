import os
import argparse
import csv
import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from rich.console import Console
from rich.table import Table
from rich import box
import folium
from folium.plugins import MarkerCluster

#Extract metada from JPEG or JPEG files.
def extract_metadata(image_path):
    try:
        image = Image.open(image_path)
        metadata = image._getexif()
        if metadata is not None:
            original_date = metadata.get(36867)  # EXIF tag for original date and time
            if original_date is not None:
                original_date = datetime.datetime.strptime(original_date, "%Y:%m:%d %H:%M:%S")
            make = metadata.get(271)  # EXIF tag for camera make
            model = metadata.get(272)  # EXIF tag for camera model
            lens_model = metadata.get(42036)  # EXIF tag for lens model
            software = metadata.get(305)  # EXIF tag for software
            offset_time = metadata.get(36880)  # EXIF tag for offset time
            return metadata, original_date, make, model, lens_model, software, offset_time
        else:
            print(f"No EXIF metadata found in {image_path}")
            return None, None, None, None, None, None, None
    except Exception as e:
        print(f"Failed to extract metadata from {image_path}: {e}")
        return None, None, None, None, None, None, None

#Obtain  Latitude and Longitude Coordinates, if found in a JPEG.
def get_coordinates(metadata):
    if metadata is not None:
        latitude_ref = None
        longitude_ref = None
        latitude = None
        longitude = None
        for tag, value in metadata.items():
            if TAGS.get(tag) == 'GPSInfo':
                for key in value.keys():
                    if key == 1:
                        latitude_ref = value[key]
                    elif key == 3:
                        longitude_ref = value[key]
                    elif key == 2:
                        degrees = value[key][0].numerator / value[key][0].denominator
                        minutes = value[key][1].numerator / value[key][1].denominator
                        seconds = value[key][2].numerator / value[key][2].denominator
                        latitude = degrees + (minutes / 60) + (seconds / 3600)
                    elif key == 4:
                        degrees = value[key][0].numerator / value[key][0].denominator
                        minutes = value[key][1].numerator / value[key][1].denominator
                        seconds = value[key][2].numerator / value[key][2].denominator
                        longitude = degrees + (minutes / 60) + (seconds / 3600)

        if latitude is not None and longitude is not None:
            if latitude_ref == 'S':
                latitude = -latitude
            if longitude_ref == 'W':
                longitude = -longitude

            return latitude, longitude

    return None, None

#Generate valid Google Maps URL.
def map_coordinates(latitude, longitude):
    map_url = f"https://www.google.com/maps?q={latitude},{longitude}"
    return map_url

#Argparse command line arguments.
parser = argparse.ArgumentParser(description='Extract metadata and optionally generate a Google Maps URL and Folium map.')
parser.add_argument('path', help='path to the image directory or an individual image file')
parser.add_argument('--map', action='store_true', help='generate a Google URL and Folium map')
parser.add_argument('--output', help='output file name')
args = parser.parse_args()

#Create a nice looking table. Got the idea from another student.
console = Console()
table = Table(show_header=True, header_style="bold", box=box.MINIMAL)
table.add_column("Image",width=50, style="cyan")
table.add_column("Latitude", style="green")
table.add_column("Longitude", style="green")
table.add_column("Original Date", style="yellow")
table.add_column("Make", style="magenta")
table.add_column("Camera Model", style="magenta")
table.add_column("Lens Model", style="magenta")
table.add_column("Software", style="magenta")
table.add_column("Offset Time Original", style="red")
table.add_column("Map URL", width=70, style="blue")

#Create a list to store the metadata results.
results = []

#Check if the provided path is a directory or a file.
if os.path.isdir(args.path):
    image_dir = args.path
    for filename in os.listdir(image_dir):
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            image_path = os.path.join(image_dir, filename)
            metadata, original_date, make, model, lens_model, software, offset_time = extract_metadata(image_path)
            latitude, longitude = get_coordinates(metadata)
            if latitude is not None and longitude is not None:
                map_url = ""
                if args.map:
                    map_url = map_coordinates(latitude, longitude)
                #Append the image information to the results list.
                results.append((image_path, str(latitude), str(longitude), original_date, make, model, lens_model, software, offset_time, map_url))
            else:
                #Append the image information with "N/A" for latitude, longitude, and Google Maps URL.
                results.append((image_path, "N/A", "N/A", original_date, make, model, lens_model, software, offset_time, "N/A"))
else:
    image_path = args.path
    if image_path.endswith(".jpg") or image_path.endswith(".jpeg"):
        metadata, original_date, make, model, lens_model, software, offset_time = extract_metadata(image_path)
        latitude, longitude = get_coordinates(metadata)
        if latitude is not None and longitude is not None:
            map_url = ""
            if args.map:
                map_url = map_coordinates(latitude, longitude)
            #Append the image information to the results list.
            results.append((image_path, str(latitude), str(longitude), original_date, make, model, lens_model, software, offset_time, map_url))
        else:
            #Append the image information with "N/A" for latitude, longitude, and Google Maps URL.
            results.append((image_path, "N/A", "N/A", original_date, make, model, lens_model, software, offset_time, "N/A"))

#Create a folder to store the results of hte csv and optional html map.
current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
folder_name = f"picture_results_{current_datetime}"
os.makedirs(folder_name, exist_ok=True)

#Print metadata results to a table.
if len(results) > 0:
    for result in results:
        #Convert datetime objects to strings due to error recieved.
        original_date_str = result[3].strftime("%Y-%m-%d %H:%M:%S") if result[3] else "N/A"
        result = list(result)
        result[3] = original_date_str
        
        #Check if metadata values are None and replace with "N/A"
        #This allows for cleaner viewing of hte data in the console.
        for i in range(4, len(result) - 1):
            if result[i] is None:
                result[i] = "N/A"
                
        table.add_row(*result)
        
    console.print(table)
    console.rule()
else:
    console.print("No images found.")

#Write metadata results to a CSV file.
if len(results) > 0:
    #Create the CSV file path within the created folder.
    csv_file_path = os.path.join(folder_name, args.output if args.output else "metadata_results.csv")
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Image', 'Latitude', 'Longitude', 'Original Date', 'Make', 'Camera Model', 'Lens Model', 'Software', 'Offset Time Original', 'Map URL'])
        
        #Write rows to the CSV file.
        for result in results:
            #Convert datetime objects to strings due to error received.
            original_date_str = result[3].strftime("%Y-%m-%d %H:%M:%S") if result[3] else "N/A"
            result = list(result)
            result[3] = original_date_str
            
            #Check if metadata values are None and replace with "N/A"
            #This will provide consistency with the dispayed table.
            for i in range(4, len(result) - 1):
                if result[i] is None:
                    result[i] = "N/A"
                    
            writer.writerow(result)
            
    console.print(f"Results written to CSV file: '{csv_file_path}'.")
else:
    console.print("No images found.")
#Generate Folium map only if --map option is provided.
if args.map and len(results) > 0:
    #Find the first valid latitude and longitude for setting the map center.
    valid_coordinates = [(float(result[1]), float(result[2])) for result in results if result[1] != 'N/A' and result[2] != 'N/A']
    
    if valid_coordinates:
        map_center = [valid_coordinates[0][0], valid_coordinates[0][1]]
    else:
        #Set a default map center if no valid coordinates are found.
        map_center = [0, 0]
        
    folium_map = folium.Map(location=map_center, zoom_start=12)

    #Create a MarkerCluster group for clustering the markers.
    #This shows the heatmap/spotlight on the map.
    marker_cluster = MarkerCluster().add_to(folium_map)

    #Add markers for each image coordinates and include assoicated metadata for the JPEG.
    for result in results:
        latitude, longitude = result[1], result[2]
        if latitude != 'N/A' and longitude != 'N/A':
            latitude, longitude = float(latitude), float(longitude)
            filename = os.path.basename(result[0])
            original_date = result[3]
            camera_model = result[5]
            map_url = result[9]

            #Fix file path slashes for the hyperlink, otherwise the slashes were "/".
            #Previously caused hte hyperlink to not work.
            file_url = "file:///" + os.path.abspath(result[0]).replace("\\", "/")

            popup_content = f"<b>Filename:</b> <a href='{file_url}' target='_new'>{filename}</a><br>" \
                            f"<b>Original Date:</b> {original_date}<br>" \
                            f"<b>Latitude:</b> {latitude}<br>" \
                            f"<b>Longitude:</b> {longitude}<br>" \
                            f"<b>Camera Model:</b> {camera_model}<br>" \
                            f"<b>Google Maps URL:</b> <a href='{map_url}'>{map_url}</a>"

            #Add a marker for the image coordinates.
            folium.Marker([latitude, longitude],
                          popup=popup_content,
                          icon=folium.Icon(color='blue', icon='camera', prefix='fa')).add_to(marker_cluster)

    #Save the map to file.
    folium.LayerControl().add_to(folium_map)
    image_map = os.path.join(folder_name, "metadata_image_map.html")
    folium_map.save(image_map)
    console.print(f"Folium map generated and saved as '{image_map}'.")