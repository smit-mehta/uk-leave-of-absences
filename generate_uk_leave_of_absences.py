import csv
import json
import googlemaps
from datetime import date

def ReadRawLocations():
  with open('data/location_history.json', 'r') as raw_location_history_file:
    return json.load(raw_location_history_file)['locations']

def SanitizeLocations(locations):
  # TODO: Pipe this as a flag or method arg.
  start_date = date(2014, 7, 20)

  with open('data/sanitized_location_history.csv', 'w') as sanitized_location_history_file, \
       open('data/missing_days.csv', 'w') as missing_days_file:
    output_csv_writer = csv.writer(sanitized_location_history_file)
    missing_days_csv_writer = csv.writer(missing_days_file)
    missing_days_csv_writer.writerow(["start_date", "end_date"])

    previous_day = start_date
    previous_latitude = -9999999
    previous_longitude = -9999999
    previous_available_day = start_date
    num_locations_processed = 0
    num_sanitized_locations_produced = 0

    for location in locations:
      num_locations_processed = num_locations_processed + 1
      if num_locations_processed % 100000 == 0:
        print ("Processed %d location data points..." % num_locations_processed)
    
      day = date.fromtimestamp(float(location['timestampMs']) / 1000)
      latitude = float(location['latitudeE7'])/10000000
      longitude = float(location['longitudeE7'])/10000000

      # Discarding irrelevant data.
      if day < start_date:
        continue
    
      # Discarding data with bad accuracy.
      if float(location['accuracy']) > 1000:
        continue
    
      # Recording the days for which the data is missing in a separate file to audit.
      if (day - previous_available_day).days > 1:
        missing_days_csv_writer.writerow(
                [previous_available_day.strftime("%Y/%m/%d"), day.strftime("%Y/%m/%d")])
      previous_available_day = day;

      # Record only those rows where there is an interesting location change.
      if (abs(latitude - previous_latitude) > 0.3 or abs(longitude - previous_longitude) > 0.3):
        output_csv_writer.writerow([day.strftime("%Y/%m/%d"), latitude, longitude]) 
        num_sanitized_locations_produced = num_sanitized_locations_produced + 1
        previous_latitude = latitude
        previous_longitude = longitude
  
    print("Sanitized data to %d location data points." % num_sanitized_locations_produced)

def TransformLocationsToCountries():
  # gmaps = googlemaps.Client(key='foobar')

  with open('data/sanitized_location_history.csv', 'r') as sanitized_location_history_file, \
       open('data/date_with_country.csv', 'w') as date_with_country_file:
    sanitized_location_history = csv.reader(sanitized_location_history_file)
    date_with_country_file_writer = csv.writer(date_with_country_file)

    for row in sanitized_location_history:
      # reverse_geocode_result = gmaps.reverse_geocode((row[1],row[2]))
      # country = reverse_geocode_result[-1]["formatted_address"]
      country = "United Kingdom"
      date_with_country_file_writer.writerow([row[0], country])

def NormalizeLeaveOfAbsences():
  return

if __name__== "__main__":
  
  print("Loading raw location data...")
  raw_locations = ReadRawLocations()

  print("Sanitizing raw location data...")
  SanitizeLocations(raw_locations)

  print("Transforming location data to country...")
  TransformLocationsToCountries()

  print("Normalizing leave of absences to generate the final report...")
  NormalizeLeaveOfAbsences()

  print("Done! You can find the report at data/uk_leave_of_absences.csv")
