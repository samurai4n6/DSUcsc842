import json
import requests
import os
from datetime import date
from datetime import timedelta
from datetime import datetime
import pandas
import matplotlib.pyplot as plt

#Module to get inital and end dates of ticket requests
def get_ticket_dates(prompt):
    while True:
        try:
            date_input = input(prompt)
            date_object = datetime.strptime(date_input, "%Y-%m-%d")
            return str(date_object.date())
        except ValueError:
            print("Check date formatting. Please enter the format as YYYY-MM-DD")


print("Enter your starting date for requesting cyber security tickets requested: ")
initial_date = get_ticket_dates(">")
print("Enter your starting date for requesting cyber security tickets requested: ")
end_date = get_ticket_dates(">")

#Check if JSON file already present and remove if present.
if os.path.exists("c:\temp\zendesk_daily_tickets.json"):
    os.remove("c:\temp\zendesk_daily_tickets.json")
else:
    pass

#Build HTTPS request to Zendesk API to obtain ticket data
url = '''https://fch.zendesk.com/api/v2/search/export?query=created>'''+initial_date+'''T00:00:00Z created<'''+end_date+'''T23:59:59Z&filter[type]=ticket'''
#print(url)
headers = { 
        "Content-Type": "application/json",
         }
response = requests.request(
         "GET",
         url,
         auth=('<zendeskuser@email.com/token','<api_key'),
         headers=headers
         )

        #print(response.text)
res_json=json.loads(response.text)

#Used print function to quickly view output to confirm whther or not data was coming back.
#print(json.dumps(res_json, indent=4))
#Create a JSON file of the data
with open("c:\\temp\\zendesk_daily_tickets.json","w") as outfile:
    json.dump(res_json,outfile,indent=4)
    outfile.close()

#Set path for csv file in preparation to convert the JSON file to csv
csv_path="c:\\temp\\zendesk_tickets.csv"

#Remove/cleanup csv file in path
if os.path.exists("c:\\temp\\zendesk_tickets.csv"):
    os.remove("c:\\temp\\zendesk_tickets.csv")
else:
    pass

#Prepping JSON data to be normalized/flattened.
jsonData=res_json["results"]
#Used in troubleshooting to identify keys in JSON data. This was useful to create uselful rows and columns in the csv file.
#for x in jsonData:
    #keys= x.keys()
    #print(keys)
    #values=x.values()
    #print(values)

#Normalize and flatten nested JSON file. Utilize Pandas to create a csv only with the identified keys as columns.    
dframe = pandas.json_normalize(jsonData)
#Identify keys/columns that I want to keep in csv
keys = ['created_at','id','url', 'type', 'via.channel','via.source.from.address','subject', 'description']
if keys:
    dframe = dframe[keys]
#Write targeted JSON data to a csv
dframe.to_csv(csv_path, index=False)

#Read in the newly created csv file, look at the "created_at" field and strip the T and everything after it. This will leave me the date only.
#Count the number of tickets per date. Create and plot a bar chart of the data.
df = pandas.read_csv("c:\\temp\\zendesk_tickets.csv")
df['new_created_at'] = df['created_at'].str.split('T').str[0]
count_by_created_date = df.groupby('new_created_at').size()
#print (df)
#print(count_by_created_date)
count_by_created_date.to_csv("c:\\temp\\zendesk_tickets_count.csv", index=False)
data_set = pandas.Series(count_by_created_date)
print(data_set)
data_set.plot(kind="line")
plt.xlabel('Ticket Date')
plt.ylabel('Ticket Count')
plt.title('Overall Ticket Count')
plt.xticks(rotation=0)
plt.show()