from flask import Flask, request, render_template, jsonify
import open_meteo

app = Flask(__name__)

# Обработка адреса главной страницы
@app.route('/')
def hello_world():
    return render_template('main.html')

# Получение погоды в координатах
@app.route('/weather_by_cord', methods=['GET', 'POST'])
def weather_by_cord():
    if request.method == 'GET':
        return render_template('weather_by_cords.html')
    elif request.method == 'POST':
        data = request.form
        latitude = data['latitude']
        longitude = data['longitude']
        data = open_meteo.get_weather_by_cords(latitude, longitude)
        if data['success']:
            weather = data['weather']
            return render_template('weather_in_cords.html', weather=weather)
        else:
            error = data['error']
            return render_template('weather_by_cords.html', error=error)

# Получение погоды в городе
@app.route('/weather_by_city', methods=['GET', 'POST'])
def weather_by_city():
    if request.method == 'GET':
        return render_template('weather_by_city.html')
    elif request.method == 'POST':
        data = request.form
        city_name = data['city_name']

        city_cords = open_meteo.cords_by_city_name(city_name)
        if city_cords['success']:
            latitude = city_cords['latitude']
            longitude = city_cords['longitude']
            data = open_meteo.get_weather_by_cords(latitude, longitude, city_name)
            if data['success']:
                weather = data['weather']
                return render_template('weather_in_cords.html', weather=weather)
            else:
                error = data['error']
                return render_template('weather_by_city.html', error=error)

        else:
            return render_template('weather_by_city.html', error='Указанный город не найден')


# Получение погоды в начальной и конечной точках маршрута
@app.route('/weather_on_route', methods=['GET', 'POST'])
def weather_on_route():
    if request.method == 'GET':
        return render_template('get_weather_from_two_point.html')
    elif request.method == 'POST':
        form = request.form.to_dict()
        weather_list = []
        for route_point in range(1, 3):
            loc_type = form.get(f'locationType{route_point}')
            # Получение погоды в городе
            if loc_type == 'city':
                name = form.get(f'cityName{route_point}')
                if not name:
                    error = f"Не указано название города"
                    return render_template('get_weather_from_two_point.html', error=error)
                city_cords = open_meteo.cords_by_city_name(name)
                if city_cords['success']:
                    latitude = city_cords['latitude']
                    longitude = city_cords['longitude']
                    data = open_meteo.get_weather_by_cords(latitude, longitude, name)
                    if data['success']:
                        weather = data['weather']
                        weather_list.append(weather)
                    else:
                        error = data['error']
                        return render_template('get_weather_from_two_point.html', error=error)
                else:
                    error = f"Указанный город не найден"
                    return render_template('get_weather_from_two_point.html', error=error)
            # Получение погоды через координаты
            elif loc_type == 'coordinates':
                latitude = float(form.get(f'latitude{route_point}'))
                longitude = float(form.get(f'longitude{route_point}'))
                data = open_meteo.get_weather_by_cords(latitude, longitude)
                if data['success']:
                    weather = data['weather']
                    weather_list.append(weather)
                else:
                    error = data['error']
                    return render_template('get_weather_from_two_point.html', error=error)

        return render_template('weather_in_two_points.html', weather_list=weather_list)

# Обработка ошибки 404
@app.errorhandler(404)
def error_404(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()