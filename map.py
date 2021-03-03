import requests

def get_coord_by_address(address):
    api_url = 'https://nominatim.openstreetmap.org/search?q=%s&format=json&countrycodes=kr'
    response = requests.get(api_url % address)
    if response.status_code == 200:
        json = response.json()
        if len(json) > 0:
            first = json[0]
            return (first['lat'], first['lon'])
        else:
            return None
    else:
        return None
