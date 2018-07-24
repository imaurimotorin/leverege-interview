import json
import pandas as pd
from pandas.io.json import json_normalize


# Reading in JSON data from link
data = pd.read_json('http://pinpointapi.cox2m.com/v1/association?q=all')

# Building list of rowindex that need to be dropped
rowToDrop = []
for i in range(data.shape[0]):
    if "workOrderId" not in data['items'][i]['tracker']:
        rowToDrop.append(i)
    elif "id" not in data['items'][i]['tracker']:
        rowToDrop.append(i)
    elif str(data['items'][i]['workOrder']) in ['None','nan']:
        rowToDrop.append(i)
    elif 'Model' not in data['items'][i]['workOrder']['vinData']:
        rowToDrop.append(i)
    elif str(data['items'][i]['workOrder']['vinData']['Make']) in ['None','nan']:
        rowToDrop.append(i)


# Dropping the rows from the data using rowToDrop
for number in rowToDrop:
    del data['items'][number]

# Converting the JSON data into pandas dataframe 
df = pd.DataFrame(json_normalize(data['items']))

# Creating a dictionary which stores each lot as a key and storing workOrderId, trackerId, model, color, battery status as tuple in a list for a lot key
lotDict = {}

# Accessing the dataframe rowindex
for row in df.index:
# Processing the data value for storing into dictionary and accessing the dataframe column name
    for column in df.columns:
# Checking if the lot name is the column name
        if column == "tracker.data.lot.name":
            lotName = df[column][row]
# Checking if tracker.id is the column name
        elif column == "tracker.id":
            trackerId = df[column][row]
# Checking if latitude is the column name
        elif column == "tracker.data.position.lat":
            lat = df[column][row]
# Checking if battery status is the column name
        elif column == "tracker.data.battery":
            battery = df[column][row]
# Checking if longitude is the column name
        elif column == "tracker.data.position.lon":
            lon = df[column][row]
# Checking tracker and workorderId association, so if workOrderId is 'None' or 'nan' tracker is ignored because it is not associated with a car
        elif column == "tracker.workOrderId":
            #ignoring the data in case of None or nan workorderId
            if str(df[column][row]) in ['None','nan']:
                break
# Else processing that row
            else:
                workerid = df[column][row]
# Checking if Car Maker name is the column name
        elif column == "workOrder.vinData.Make":
            carModel = df[column][row]
# Checking if Car Model year is the column name
        elif column == "workOrder.vinData.ModelYear":
            carModelYear = df[column][row]
# Checking if Car Color is the column name
        elif column == "workOrder.color":
            carColor = df[column][row]

# Updating the dictionary from processed row of dataframe if lotName not in the dictionary, update key and value as list which has stored all information as tuple in a list for each tracker.
    if lotName not in lotDict:
        lotDict[lotName] = [(lat,lon,workerid,trackerId,carModel,carColor,carModelYear,battery)]
    else:
        lotDict[lotName].append((lat,lon,workerid,trackerId,carModel,carColor,carModelYear,battery))

# Printing the all the lot name and information stored for a lot
for lotName,list1 in lotDict.items():
    number = len(list1)
    print(lotName,number,list1)

# Printing the top 5 lots, and most popular make of cars in each lot
count = 0
print("\nTop 5 lot according to number of tracker available")
for lotName,list1 in sorted(lotDict.items(),key = lambda x : len(x[1]),reverse=True):
    if count < 5:
        count += 1
        carList = [ tuple1[4] for tuple1 in list1]
        carName = max(carList,key=carList.count)
        print("{}. LotName : {} Tracker Frequency : {} Most Popular Car: {} " .format(count,lotName,len(list1),carName))
    else:
        break