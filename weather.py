import requests
import voice
import map

def get_weather_by_code(code):
    api_url = "https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s&units=%s"
    app_id = "6e25184efbbc99d3f4752aa0c0e36b3b"
    unit = "metric"

    response = requests.get(api_url % (code, app_id, unit))
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_weather_by_coord(lat, lon):
    api_url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=%s"
    app_id = "6e25184efbbc99d3f4752aa0c0e36b3b"
    unit = "metric"

    response = requests.get(api_url % (lat, lon, app_id, unit))
    if response.status_code == 200:
        return response.json()
    else:
        return None

def create_weather_text(weather_info, address):
    response = "현재 %s의 온도는 %d도이고, 습도는 %d퍼센트입니다."
    if weather_info != None:
        return response % (address, weather_info['main']['temp'], weather_info['main']['humidity'])
    else:
        return "죄송합니다. 날씨를 알 수 없습니다."
    
def main():
    voice.speech("어디의 날씨를 알려드릴까요? ")
    address = voice.get_text_from_voice()

    coord = map.get_coord_by_address(address)
    if coord == None:
        voice.speech("죄송합니다. %s 를 찾지 못했습니다." %address)
    else:
        weather_info = get_weather_by_coord(coord[0], coord[1])

        response_text = create_weather_text(weather_info, address)
        voice.speech(response_text)


if __name__ == "__main__":
    main()
