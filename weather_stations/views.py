from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
from django.views.decorators.cache import cache_page
from django.conf import settings
import redis
from functools import wraps

def index(request):
    return HttpResponse("Hello, You're at the index page.")


def ping_response(request):
    responseData = {
        'data': 'pong'
    }
    return JsonResponse(responseData)

def cache_page_from_params(*cache_args, **cache_kwargs):
    def inner_decorator(func):
        @wraps(func)
        def inner_function(request, *args, **kwargs):
            if 'nocache' not in request.GET or request.GET['nocache'] != '1':
                return cache_page(*cache_args, **cache_kwargs)(func)(request, *args, **kwargs)
            return func(request, *args, **kwargs)
        return inner_function
    return inner_decorator


@cache_page_from_params(60 * 5)
def weather_response(request, *args, **kwargs):
    try: 
        if 'scode' not in request.GET:
            return JsonResponse({'msg' : 'Query parameter is not provided','status_code': 400})

        else:
            query_param = request.GET['scode'].upper()
            data = requests.get('https://tgftp.nws.noaa.gov/data/observations/metar/stations/' + query_param + '.TXT')

            response_data = data.text
            response= response_data.split()
            temperature = response[8].split('/')
            if temperature[0].startswith('M'):
                centigrade = temperature[0].replace('M', '-')
            else: 
                centigrade = temperature[0]
            centigrade = float(centigrade) 
            Fahrenheit = (centigrade * 1.8) + 32
            wind_len = len(response[5])
            if wind_len == 7:
                direction = response[5][0:3]
                velocity = response[5][3:5]
                gusts = 0
            if wind_len == 10:
                direction = response[5][0:3]
                gusts = response[5][3:6]
                velocity = response[5][6:8]
            val=int((int(direction)/22.5)+.5)
            direction_int = int(direction)
            arr=["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
            direction_degree = arr[(val % 16)]
            mph= float(velocity) * 1.151
            responseData = {
                'station': response[2],
                'last_observation': response[0] + ' at ' + response[1] + ' GMT',
                'temperature': str(centigrade) + '°C' + ' (' + str(Fahrenheit) + '°F)',
                'direction_angle': direction,
                'gusts': str(gusts),
                'velocity' : str(int(velocity)) + 'knots',
                'direction_degree': direction_degree,
                'mph': mph,
                'wind': direction_degree + ' at ' + str(mph) + ' mph' + '(' + velocity + ' knots)',
                'status_code': 200
            }
            print(responseData)
            return JsonResponse(responseData)
    except Exception as e:
        return JsonResponse({'message': e.msg})
