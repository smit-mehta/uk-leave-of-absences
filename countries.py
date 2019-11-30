from country import Country

NON_CACHED_COUNTRY = "NonCachedCountry"

# Caching biggest possible "rectangular" boundary of coordinates for ten largest countries
# and UK such that all points within this rectangle belong to the said country.
CACHED_COUNTRIES = {
  Country("United Kingdom", -1, 5, 10, 20),
  Country("India", -2, 3, 44, 55)
}

def GetCountryFromCachedCoordinates(latitude, longitude):
  for country in CACHED_COUNTRIES:
    if country.isLocationWithinCountry(latitude, longitude):
      return country.name

  return NON_CACHED_COUNTRY
