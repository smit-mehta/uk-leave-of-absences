import csv
import json
from datetime import date

# TODO: Pipe this as a flag or method arg.
start_date = date(2014, 7, 20)

print ("Loading raw location history...")
with open('data/location_history.json', 'r') as raw_location_history_file:
  locations = json.load(raw_location_history_file)['locations']

with open('data/sanitized_location_history.csv', 'w') as sanitized_location_history_file, open('data/missing_days.csv', 'w') as missing_days_file:
  output_csv_writer = csv.writer(sanitized_location_history_file)
  missing_days_csv_writer = csv.writer(missing_days_file)
  missing_days_csv_writer.writerow(["start_date", "end_date"])

  previous_day = start_date
  previous_lat = -9999999
  previous_long = -9999999
  previous_available_day = start_date
  num_locations_processed = 0
  num_sanitized_locations_produced = 0

  for location in locations:
    num_locations_processed = num_locations_processed + 1
    if num_locations_processed % 100000 == 0:
      print ("Processed %d location data points...", num_locations_processed)
    
    day = date.fromtimestamp(float(location['timestampMs']) / 1000)
    lat = float(location['latitudeE7'])/10000000
    long = float(location['longitudeE7'])/10000000

    # Discarding irrelevant data.
    if day < start_date:
      continue
    
    # Discarding data with bad accuracy.
    if float(location['accuracy']) > 1000:
      continue
    
    # Recording the days for which the data is missing in a separate file to audit.
    if (day - previous_available_day).days > 1:
      missing_days_csv_writer.writerow([previous_available_day.strftime("%Y/%m/%d"), day.strftime("%Y/%m/%d")])
    previous_available_day = day;

    # Record only those rows where there is an interesting location change.
    if (abs(lat - previous_lat) > 0.3 or abs(long - previous_long) > 0.3):
      output_csv_writer.writerow([day.strftime("%Y/%m/%d"), lat, long]) 
      num_sanitized_locations_produced = num_sanitized_locations_produced + 1
      previous_lat = lat
      previous_long = long
  
  print("Done! Sanitized data to %d location data points." , num_sanitized_locations_produced)
