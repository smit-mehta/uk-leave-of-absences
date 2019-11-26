import csv
import json
from datetime import date

with open('data/location_history.json', 'r') as input_file:
  locations = json.load(input_file)['locations']

with open('data/truncated_location_history.csv', 'w') as output_file:
  output_csv_writer = csv.writer(output_file)
  previous_day = date(2014, 7, 19)
  previous_lat = -9999999
  previous_long = -9999999
  previous_available_day = date(2014, 7, 19)
  for location in locations:
    day = date.fromtimestamp(float(location['timestampMs']) / 1000)
    lat = float(location['latitudeE7'])/10000000
    long = float(location['longitudeE7'])/10000000

    if day < date(2014, 7, 20):
      continue
    
    if float(location['accuracy']) > 1000:
      continue
    
    timedelta = day - previous_available_day
    if timedelta.days > 1:
      print "Data missing between " + previous_available_day.strftime("%Y/%m/%d") + " and " + day.strftime("%Y/%m/%d")
    previous_available_day = day;  

    if day != previous_day and (abs(lat - previous_lat) > 0.3 or abs(long - previous_long) > 0.3):
      output_csv_writer.writerow([day.strftime("%Y/%m/%d"), lat, long])
      previous_day = day
      previous_lat = lat
      previous_long = long
  
  print("Done!")
