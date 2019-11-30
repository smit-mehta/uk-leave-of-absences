from country import Country

NON_CACHED_COUNTRY = "NonCachedCountry"

CACHED_COUNTRIES = {
  Country("United Kingdom", -1, 5, 10, 20),
  Country("India", -2, 3, 44, 55)
}

def GetCountryFromCachedCoordinates(latitude, longitude):
  for country in CACHED_COUNTRIES:
    if country.isLocationWithinCountry(latitude, longitude):
      return country.name

  return NON_CACHED_COUNTRY
