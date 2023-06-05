"""
Weather Report and Forecast Application

This Python script allows you to retrieve and share weather reports and forecasts for a given city. It leverages an weather API to fetch current weather data and forecast information.

Prerequisites:
- Python 3.x
- pyowm, argparse, datetime modules

Usage:
1. Set up an account and obtain an API key from a weather API provider.
2. Pass your actual API key as a command line argument.
3. Pass the city name as a command line argument.
4. The script will fetch the current weather report and display it, along with a forecast for +3 hours and rain, fog predictions next few days.

Note: This script assumes a stable internet connection for accessing the weather API.

Running from command line:
$ python weatherForecastTool.py -k <api_key> -c <city_name>
Example:
$ python weatherForecastTool.py -k 5adaceb79e5cb497b69d64fa00f45b01 -c Bangalore

Author: Dementors
Date: 05-June-2023
"""

import pyowm
from pyowm.utils import timestamps
import argparse
from datetime import datetime


# parse command line args
def cmd_line_parser():
    parser = argparse.ArgumentParser()
    # get city name
    parser.add_argument('-c', '--city', help='city to get weather for', required=True)
    # get api key for OpenWeatherMap API
    parser.add_argument('-k', '--api_key', help='api key for OpenWeatherMap API', required=True)
    args = parser.parse_args()
    return args


# get weather object
def get_weather_obj(api_key):
    # error handling for invalid API key
    try:
        owm = pyowm.OWM(api_key)
    except:
        print('Invalid API key')
        exit()

    # use the pyowm API to get the current weather for a city
    weather_manager = owm.weather_manager()
    return weather_manager


def get_current_time():
    # get current time in %Y-%m-%d %H:%M:%S format
    curr_hour, curr_min = datetime.now().hour, datetime.now().minute
    if curr_min >= 30:
        curr_hour += 1
    curr_time = datetime.now().replace(hour=curr_hour, minute=0, second=0, microsecond=0)
    return curr_time


def get_time_three_hours_later():
    curr_time = get_current_time()
    future_time = curr_time.replace(hour=curr_time.hour + 3)
    return future_time


def jump_to_entry():
    three_hours_later = get_time_three_hours_later().hour
    number_of_hours = three_hours_later - 9
    return three_hours_later, int(number_of_hours / 3)


# get weather or forecast of a city
def get_weather(args, hours='0'):
    weather_manager = get_weather_obj(args.api_key)
    if hours == '0':
        # error handling for invalid city name
        try:
            weather = weather_manager.weather_at_place(args.city).weather
        except:
            print("Please enter a valid city name")
            exit()
    else:
        # error handling for invalid city name
        try:
            weather = weather_manager.forecast_at_place(args.city, hours).forecast
        except:
            print("Please enter a valid city name")
            exit()

    return weather


# get current hour and min
def get_curr_hour_min():
    hr, mins = datetime.now().hour, datetime.now().minute
    if mins < 10:
        mins = f"0{mins}"
    curr_time = f"{hr}:{mins}"
    time_of_day = determine_time_of_day(hr)
    return curr_time, time_of_day


# get weather details from weather object
def get_weather_details(weather):
    ref_time, time_of_day = get_curr_hour_min()
    weather_info_dict = {}
    # error handling
    try:
        weather_info_dict = {'status': weather.status, 'detailed_status': weather.detailed_status,
                             'sunrise_time': weather.sunrise_time(timeformat='iso'),
                             'ref_time': ref_time,
                             'sunset_time': weather.sunset_time(timeformat='iso'), 'humidity': weather.humidity,
                             'temperature': weather.temperature(unit='celsius'), 'time_of_day': time_of_day}
    except:
        print("Error occurred while fetching weather details")
        exit()

    weather_info_dict['humidity_level'] = determine_humidity(weather_info_dict['humidity'])
    weather_info_dict['temp_max'] = weather_info_dict['temperature']['temp_max']
    weather_info_dict['temp_min'] = weather_info_dict['temperature']['temp_min']
    weather_info_dict['temp_feels_like'] = weather_info_dict['temperature']['feels_like']

    return weather_info_dict


# get forecast details from forecast object
def get_forecast_details(forecast):
    forecast_info_dict = {}
    future_time_hour, jump_entries = jump_to_entry()
    for each_time_stamp in forecast.weathers:
        if jump_entries == 0:
            break
        jump_entries -= 1
    # print(each_time_stamp)
    forecast_info_dict = {'status': each_time_stamp.status, 'detailed_status': each_time_stamp.detailed_status,
                          'reftime': future_time_hour}
    return forecast_info_dict


# get rain, snow, fog forecast for a city
def get_rain_snow_fog_forecast(args):
    rain_snow_fog_dict = {}
    weather_manager = get_weather_obj(args.api_key)
    forecast = weather_manager.forecast_at_place(args.city, '3h')

    tomorrow = timestamps.tomorrow()
    rain_snow_fog_dict['rain'] = forecast.will_be_rainy_at(tomorrow)
    rain_snow_fog_dict['snow'] = forecast.will_have_snow()
    rain_snow_fog_dict['fog'] = forecast.will_have_fog()
    return rain_snow_fog_dict


# determine morning, afternoon, evening from reference time
def determine_time_of_day(reference_time):
    if 6 <= reference_time < 12:
        return "Morning"
    elif 12 <= reference_time < 18:
        return "Afternoon"
    elif 18 <= reference_time < 24:
        return "Evening"


# determine humidity low, medium or high
def determine_humidity(humidity):
    if humidity < 30:
        return "low"
    elif 30 <= humidity < 60:
        return "medium"
    else:
        return "high"


# convert all non string values to string
def convert_to_string(weather_info_dict):
    for key, value in weather_info_dict.items():
        if not isinstance(value, str):
            weather_info_dict[key] = str(value)
    return weather_info_dict


# remove all fields with None value
def remove_none_fields(weather_info_dict):
    # error handling
    if weather_info_dict == None:
        return {}
    old_weather_info_dict = weather_info_dict.copy()
    for key, value in old_weather_info_dict.items():
        if value == None or value == 'None':
            del weather_info_dict[key]
    return weather_info_dict


# remove empty fields from weather details
def remove_empty_fields(weather_info_dict):
    old_weather_info_dict = weather_info_dict.copy()
    for key, value in old_weather_info_dict.items():
        if value == '' or value == {} or value == []:
            del weather_info_dict[key]
    return weather_info_dict


# format the weather details
def format_weather_details(weather_info_dict):
    weather_info_dict = remove_none_fields(weather_info_dict)
    weather_info_dict = remove_empty_fields(weather_info_dict)
    weather_info_dict = convert_to_string(weather_info_dict)
    return weather_info_dict


# print the weather details beautifully
def print_weather_details(args, weather_info_dict, future_info_dict, rain_snow_fog_dict):
    print_stmt = ""
    ## present
    curr_time = weather_info_dict['ref_time']
    time_of_day = weather_info_dict['time_of_day']
    detailed_status = weather_info_dict['detailed_status']
    humidity = weather_info_dict['humidity']
    humidity_level = weather_info_dict['humidity_level']
    temp_max = weather_info_dict['temp_max']
    temp_min = weather_info_dict['temp_min']
    feels_like = weather_info_dict['temp_feels_like']

    print_stmt_curr = f"Good {time_of_day}!! It is {curr_time} hours in {args.city}, and we have {detailed_status} with {humidity}% {humidity_level} humidity. " \
                      f"The temperature ranges between {temp_min} and {temp_max} degrees Celsius but it may feel like {feels_like}" \
                      f" degrees Celsius."
    ## future
    fut_time = future_info_dict['reftime']
    fut_detailed_status = future_info_dict['detailed_status']
    fut_status = future_info_dict['status']
    print_stmt_future = f"At around {fut_time} hours, we might have {fut_detailed_status}."

    ## rain, snow, fog forecast
    print_stmt_rain = "Carry an umbrella as there might be some rain tomorrow." if rain_snow_fog_dict[
        'rain'] else "We are expecting clear skies tomorrow.Don't miss your shades!!"
    print_stmt_fog = "Also, it might be foggy the next few days." if rain_snow_fog_dict['fog'] else ""
    print_stmt = print_stmt_curr + "\n" + print_stmt_future + "\n" + print_stmt_rain + "\n" + print_stmt_fog
    print(print_stmt)


# main function
def main():
    # get command line args
    args = cmd_line_parser()

    ## Current
    # get weather for city
    weather = get_weather(args)
    # Error handling
    if weather is None:
        print("No weather details found for the city. Please check the city name and try again.")
        exit(0)

    # get weather details
    weather_info_dict = get_weather_details(weather)
    # format weather details
    weather_info_dict = format_weather_details(weather_info_dict)

    ## Future - 3 hours
    # get forecast for city
    forecast = get_weather(args, "3h")
    # get weather details
    forecast_info_dict = get_forecast_details(forecast)

    ## Future - rain, snow, fog
    rain_snow_fog_dict = get_rain_snow_fog_forecast(args)
    print_weather_details(args, weather_info_dict, forecast_info_dict, rain_snow_fog_dict)


if __name__ == "__main__":
    main()
