# DSUcsc842
Code for DSU CSC 842 course


_**Cycle2 - Zendesk Ticket Collection**_

**What is the purpose of the project?**

The purpose of the project came from a need that I have in collecting metrics for cyber security tickets that our SOC performs.
Management was asking how many tickets our SOC was receiving to be worked, which aided in showing how many more positions we needed for hire.

The Zendesk API is required, and hte following link is beneficial:
https://developer.zendesk.com/api-reference/

**Why is project the useful?**

This project is use for cyber security management. I need to understand how many tickets we receive to gauge work load, identify trends and increases in work, and effectively
manage work in our SOC.

**What does the project do?**

This project does the following:

-Identifies an initial and end dates that pertain to the timeframe you would like cyber security tickets to be collected.

-Checks and cleans up JSON and CSV files that may be present from a previous run.

-Builds an HTTPS connection to the Zendesk API to pull ticket related data in JSON format within the requested time frame.

-Creates a JSON file of the ticket data.

-Creates a CSV with targeted fields/keys from the JSON data.

-Utilizes pandas to count tickets by date and generating a line graph of the count by date.

**Future Work**

-Integrate more API calls to further enrich the ticket data for metrics.

-Perform additional statistical analysis via pandas for metrics.

_**Cycle4 - E01/EWF File Image Mounter**_

**What is the purpose of the project?**

Forensic examiners and analysts need to be able to mount images in order to analyze content as it relates to an investigation. The focus was to mount and handle Expert Witness Format (EWF / E01 / Encase images) images to a Windows or Linux environment.

**Why is project the useful?**

This project is useful, becasue you never know when a tool may fail, have complicaitons, or some other issue is present that causes a tool to fail image mounting. This tool will determine if you are on a Linux or Windows host and attempt to mount the EWF/E01 file and provide options. Within Windows there are options that once the image mounts, you can unmount and exit, display current volumes, and collect files. For Linux the only options right now are to unmount and exit and display current volumes. 

**What does the project do?**

This project does the following:

-Mounts an EWF/E01 forensic image in either a Linux or Windows environment.

-Mounting in either Windows or Linux requires elevated privileges. The code will attempt to elevate with running as admin in Windows or leveraging sudo in Linux.

-Once the image is mounted, a menu is provided to perform certain actions.

-Both Windows and Linux have unmount and exit option.

-Both Winbdows and Linux have show current volumes options (this may be useful if you need to navigate the file system)

-For just Windows there is a triage collection option, that utilizes KAPE to collect the files.

**Future Work**

-Add cross-platform functionality for MacOS

-Build in other image file formats like Raw/dd, AFF4, and others.

  -With Windows and AIM, many of hte formats will work, but with Linux there will likely be subtle differences in hte needed options to mount.
  
-There is a python libary called pyewf, and while I attempted to use, I ran into error after error trying it. 
-Add auto installer for dependencies.

-Perhaps compile into a stand-alone binary.

-Make tool portable. KAPE and AIM can already be used in a portable way.

**Dependeices**

-For Windows,

  -It is assumed that you Arsenal Image Mounter available for the Python code to call the cli tool. Arsenal is one the best free and paid image mounter available. Having a CLI binary allows for scripting and automating tasks.
  
  -KAPE for file collection https://www.kroll.com/en/services/cyber-risk/incident-response-litigation-support/kroll-artifact-parser-extractor-kape
  
-For Linux,

  -sudo apt install tsk TSKs (The Sleuth's Kit) MMLS, do determine sector size and byte count.
  
  -sudo apt install ewf-tools ewf-tools contains the needed files to interact with the EWF/E01 file
  
  -I leveraged SANS SIFT for testing since most of what I need is already there.
  
References
https://www.kroll.com/en/services/cyber-risk/incident-response-litigation-support/kroll-artifact-parser-extractor-kape

https://github.com/dlcowen/dfirwizard

https://github.com/libyal/libewf

https://wiki.sleuthkit.org/index.php?title=Mmls

https://realpython.com/command-line-interfaces-python-argparse/

https://stackoverflow.com/questions/70300494/how-do-i-run-a-script-with-elevated-uac-permissions-using-ctypes

https://arsenalrecon.com/products/arsenal-image-mounter


_**Cycle6 - Image Mapper And eXif eXtractor (IMAXX)**_

**What is the purpose of the project?**

JPEG (also JPG) files takes from phones and camera may provide crucial metadata that may be relevant in an investigation. Exif data such as Camera Model, Software, Orientation GPS cordinates, and much more could be within EXIF data of a JPEG. This tool will extract targeted metadata from JPEG files, display the targeted metadata, if GPS coordinates are identified they will extracted, and mapped with the Python libarary Folium.

**Why is project the useful?**

These exif data points can be crucial in an investigation. From a law enforcement perspective let's say a mobile device or phone was recovered. Well if pictures were taken recently on the device, there could be exif data that could be extracted and provide possible leads for either a victim or subject of an ivestigation. From a corporate perspective, the same may be true. Perhaps a subject took a picture with their phone, which contained sensitive data, and emailed the picture from their email client to a personal email address. This exif data could show their specific phone model, phone version, and software, GPS coordinates, date and time of picture taken (which could be correlated to other evidence), and more.

Also while most websites will strip all or some of hte exif data from JPEGs, there are some sites that may keep it, and you never know when that might be useful.

**What does the project do?**

This project does the following:

-Parses either (1) JPEG file or a directory of JPEG files.

-Extracts all Exif data from the JPEG, and places into variables, and returns hte targeted metadata.

-If GPS coordinates are found they will be converted in a format that Google Maps and Folium can plot.

-If GPS coordinates are found a Google Maps URL will be created.

-A table of the results will, which includes the file name and associated metadata identified will be displayed in console.

-A csv of the same results shown in the table will be created for furhter manipulation.

-If there are images with GPS information a map with plotted GPS points will be provided, along with assoicated metadata and a hyperlink to the JPEG.

-Outputs csv and html map to folder named 'picutre_results_ISODATE_ISOTIME'

**Future Work**

-Perhaps compile into a stand-alone binary.

-Consider other metadata to include in the results.

-Add a thumbnail in the pop-up for the folium map.

**_Video Link_**

https://www.youtube.com/watch?v=AV0qPDKohFQ

**Resources/References/Inspiration**

https://exiftool.org/

https://exiftool.org/TagNames/EXIF.html

https://caseguard.com/articles/digital-evidence-exif-data/

https://www.thepythoncode.com/article/extracting-image-metadata-in-python

https://medium.com/spatial-data-science/how-to-extract-gps-coordinates-from-images-in-python-e66e542af354

https://medium.com/geekculture/extract-gps-information-from-photos-using-python-79288c58ccd9

Cycle8 - 

Cycle10 -
