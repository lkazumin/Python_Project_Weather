import open_meteo
import json

# Проверка получения погоды по координатам
latitude = 	55.7522
longitude = 37.6156

weather = open_meteo.get_weather_by_cords(latitude=latitude, longitude=longitude)

for k, v in weather.items():
    print(f"{k}: {v}")
with open('moscow_weather.json', 'w') as f:
    json.dump(weather, f)

# Проверка модели проверки качества погоды
weather_list = [
    {
        'temperature': 0,
        'relative_humidity': 20,
        'precipitation_probability': 20,
        'surface_pressure': 1000,
        'visibility': 2000,
        'wind_speed': 20
    },
    {
        'temperature': -2,
        'relative_humidity': 100,
        'precipitation_probability': 20,
        'surface_pressure': 1000,
        'visibility': 2000,
        'wind_speed': 20
    },
    {
        'temperature': 0,
        'relative_humidity': 20,
        'precipitation_probability': 100,
        'surface_pressure': 2000,
        'visibility': 100,
        'wind_speed': 202
    },
]

for ind, weather in enumerate(weather_list):
    res = open_meteo.weather_quality(weather)
    print(f"\nТест номер {ind}:")
    if res:
        for cond in res:
            print(cond)
    else:
        print("Погода хорошая")
