import csv
import requests

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """[out:csv(::lat, ::lon, "ref", name, ::count)]; \n ( \n"""
overpass_end = "\n ); \n out; \n out count; \n"

dotaz = """area[name = "Česko"]; \n
node(area)["removed:highway" = "emergency_access_point"];"""

overpass_query = overpass_query + dotaz + overpass_end

response = requests.get(overpass_url, params={'data': overpass_query})
data = [row.split('\t') for row in response.text.split('\n')]
m = sum(1 for line in data)
print(str(m))
# for x in data[.m]


