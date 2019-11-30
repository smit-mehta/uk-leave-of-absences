class Country:

  def __init__(self, name, lat_start, lat_end, long_start, long_end):
    self.name = name
    self.lat_start = lat_start
    self.lat_end = lat_end
    self.long_start = long_start
    self.lonng_end = long_end

  def isLocationWithinCountry(self, latitude, longitude):
    return latitude >= self.lat_start and latitude <= self.lat_end and longitude >= self.long_start and longitude <= self.long_end
