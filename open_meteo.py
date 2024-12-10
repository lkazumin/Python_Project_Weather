import requests
import openmeteo_requests
import requests_cache
from datetime import datetime
from retry_requests import retry


# Оценка погодных условий
def weather_quality(weather):
    bad_conditions = []
    if weather['temperature'] < 0:
        bad_conditions.append(f"Температура слишком низкая: {weather['temperature']}")
    if weather['temperature'] > 35:
        bad_conditions.append(f"Температура слишком большая: {weather['temperature']}")
    if weather['wind_speed'] >= 40:
        bad_conditions.append(f"Скорость ветра слишком большая: {weather['wind_speed']} метров в секунду")
    if weather['precipitation_probability'] > 70:
        bad_conditions.append(f"Вероятность выпадения осадков слишком высока: {weather['precipitation_probability']}%")
    if weather['visibility'] < 1000:
        bad_conditions.append(f"Слишком низкая видимость: {weather['visibility']} метров")
    if weather['surface_pressure'] > 1500:
        bad_conditions.append(f"Слишком большое давление: {weather['surface_pressure']} Па")
    if weather['relative_humidity'] > 80:
        bad_conditions.append(f"Слишком большая влажность: {weather['relative_humidity']}%")

    return bad_conditions


# Получение погоды по координатам
def get_weather_by_cords(latitude, longitude, name=None):
    try:
        # Запрос к api
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability", "surface_pressure",
                       "visibility", "wind_speed_10m"],
            "temporal_resolution": "native",
            "forecast_days": 1
        }
        responses = openmeteo.weather_api(url, params=params)
        # Обработка результата
        response = responses[0]
        hourly = response.Hourly()
        weather = {
            'name': name,
            'cords': f"{response.Latitude()}°N {response.Longitude()}°E",
            'date': datetime.now().strftime("%d-%m-%Y"),
            'temperature': int(hourly.Variables(0).ValuesAsNumpy().mean()),
            'relative_humidity': int(hourly.Variables(1).ValuesAsNumpy().mean()),
            'precipitation_probability': int(hourly.Variables(2).ValuesAsNumpy().mean()),
            'surface_pressure': int(hourly.Variables(3).ValuesAsNumpy().mean()),
            'visibility': int(hourly.Variables(4).ValuesAsNumpy().mean()),
            'wind_speed': int(hourly.Variables(5).ValuesAsNumpy().mean())
        }

        weather['bad_condition'] = weather_quality(weather)
        # Возвращение результата
        return {'success': True,
                'weather': weather
                }
    except Exception as e:
        return {'success': False,
                'error': f"Проблемы с доступом к api: \n{str(e)}"
                }


# Получение координат по названию города
def cords_by_city_name(name):
    try:
        # Запрос к api
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={name}&count=1&language=en&format=json"
        request = requests.get(url).json()
        # Возвращение результата
        if request.get('results'):
            result = request['results'][0]
            latitude = result['latitude']
            longitude = result['longitude']
            return {
                'success': True,
                'latitude': latitude,
                'longitude': longitude
            }
        else:
            return {
                'success': False,
                'error': "City  not found"
            }
    except Exception as e:  # Проблемы с доступом к api
        return {
            'success': False,
            'error': f"Проблемы с доступом к api: \n{str(e)}"
        }
