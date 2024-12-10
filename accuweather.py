import requests
import json
from datetime import datetime

api_key = "uAcd5AjbGMNkcrcihvy1ZS8QXSzhVUS5"


# Получение ключа локации по координатам
def lock_key_by_cords(latitude, longitude):
    location_url = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
    params = {
        "apikey": api_key,
        "q": f"{latitude},{longitude}"
    }
    response = requests.get(location_url, params=params)
    response = response.json()

    code = response.get('Code')
    if code == 'ServiceUnavailable':
        return {
            'success': False,
            'error': response.get('Message')
        }

    location_key = response.get('Key')
    return {
            'success': True,
            'key': location_key
        }


# Получение погоды по ключу локации
def get_weather(location_key):
    params = {
        "apikey": api_key,
        "details": True,
        'metric': True
    }
    url = f'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}'

    response = requests.get(url, params=params)
    return response.json()


def main():
    # Получение погоды в Москве
    latitude = 55.7522
    longitude = 37.6156

    result = lock_key_by_cords(latitude, longitude)
    if not result['success']:
        print(result['error'])
    else:
        location_key = result['key']
        weather = get_weather(location_key)
        weather_json = {
            'cord': f"{latitude}; {longitude}",
            'date': datetime.now().strftime("%d-%m-%Y"),
            'temperature': int(
                (
                        weather['DailyForecasts'][0]['Temperature']['Minimum']['Value'] +
                        weather['DailyForecasts'][0]['Temperature']['Maximum']['Value']
                )/2
            ),
            'relative_humidity': int(
                weather['DailyForecasts'][0]['Day']['RelativeHumidity']['Average']
            ),
            'precipitation_probability': int(
                weather['DailyForecasts'][0]['Day']['PrecipitationProbability']
            ),
            'wind_speed': int(
                weather['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']
            )
        }
        print(weather_json)
        with open('accu_weather_msk.json', 'w') as f:
            json.dump(weather_json, f, indent=4)


if __name__ == '__main__':
    main()
