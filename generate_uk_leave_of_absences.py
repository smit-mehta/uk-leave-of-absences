import countries
import csv
import json
import googlemaps
from datetime import date

def ReadRawLocations():
  with open("data/location_history.json", "r") as raw_location_history_file:
    return json.load(raw_location_history_file)["locations"]

def SanitizeLocations(locations):
  # TODO: Pipe this as a flag or method arg.
  start_date = date(2014, 7, 20)
  end_date = date(2019, 12, 1)

  with open("data/sanitized_location_history.csv", "w") as sanitized_location_history_file, \
       open("data/missing_days.csv", "w") as missing_days_file:
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
    
      day = date.fromtimestamp(float(location["timestampMs"]) / 1000)
      latitude = float(location["latitudeE7"])/10000000
      longitude = float(location["longitudeE7"])/10000000

      # Discarding data outside requested time range.
      if day < start_date or day > end_date:
        continue
    
      # Discarding data with bad accuracy.
      if float(location["accuracy"]) > 1000:
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
  with open("data/api_key.txt", "r") as key_file:  
    gmaps = googlemaps.Client(key=key_file.read())

  cache_hits = 0
  gmaps_api_calls = 0

  with open("data/sanitized_location_history.csv", "r") as sanitized_location_history_file, \
       open("data/date_with_country.csv", "w") as date_with_country_file:
    sanitized_location_history = csv.reader(sanitized_location_history_file)
    date_with_country_file_writer = csv.writer(date_with_country_file)

    for row in sanitized_location_history:
      country = countries.GetCountryFromCachedCoordinates(row[1], row[2])
      
      if country == countries.NON_CACHED_COUNTRY:
        # reverse_geocode_result = gmaps.reverse_geocode((row[1],row[2]))
        # country = reverse_geocode_result[-1]["formatted_address"]
        gmaps_api_calls = gmaps_api_calls + 1
        country = "United Kingdom"
      else:
        cache_hits = cache_hits + 1
        
      date_with_country_file_writer.writerow([row[0], country])
  
  print("Processed %d data points with cached countries list, %d with GMaps API calls." % 
          (cache_hits, gmaps_api_calls))

def NormalizeLeaveOfAbsences():
  with open("data/date_with_country.csv", "r") as date_with_country_file, \
       open("data/uk_leave_of_absences.csv", "w") as uk_leave_of_absences_file:
    date_with_country_data = csv.reader(date_with_country_file)
    uk_leave_of_absences_file_writer = csv.writer(uk_leave_of_absences_file)
  
    previous_country = "non-existent-country"

    for row in date_with_country_data:
      country = row[1]
      if country != previous_country:
        uk_leave_of_absences_file_writer.writerow([row[0], row[1]])
        previous_country = country

if __name__== "__main__":
  print("\nStage 1 / 5: Loading raw location data...\n")
  raw_locations = ReadRawLocations()

  print("\nStage 2 / 5: Sanitizing raw location data...\n")
  SanitizeLocations(raw_locations)

  print("\nStage 3 / 5: Transforming location data to country...\n")
  TransformLocationsToCountries()

  print("\nStage 4 / 5: Normalizing leave of absences to generate the final report...\n")
  NormalizeLeaveOfAbsences()

  print("\nStage 5 / 5: Done! You can find the report at data/uk_leave_of_absences.csv\n")
