from PIL import Image, ImageFont, ImageDraw
import os
import numpy as np
import time
from datetime import datetime
from dateutil import tz
from ast import literal_eval

class WeatherScreen:
    def __init__(self, config, modules):
        self.modules = modules
        self.font = ImageFont.truetype("fonts/tiny.otf", 5)

        self.canvas_width = 64
        self.canvas_height = 64
        self.icons = generateIconMap()

        self.text_color = literal_eval(config.get('Weather Screen', 'text_color', fallback="(255,255,255)"))
        self.low_color = (12, 138, 235)
        self.high_color = (235, 38, 12)

    def generate(self):
        
        frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))

        weather_module = self.modules['weather']
        one_call = weather_module.getWeather()

        if one_call is not None:
            forecast = one_call.forecast_daily[0]
            rain = round(forecast.precipitation_probability*100)
            temps = forecast.temperature('fahrenheit')
            min_temp = round(temps['min'])
            max_temp = round(temps['max'])
            curr_temp = round(one_call.current.temperature('fahrenheit')['temp'])
            humidity = round(one_call.current.humidity)
            sunrise_timestamp = one_call.forecast_daily[0].sunrise_time()
            sunset_timestamp = one_call.forecast_daily[0].sunset_time()
            dtsr = datetime.fromtimestamp(sunrise_timestamp, tz=tz.tzlocal())
            dtss = datetime.fromtimestamp(sunset_timestamp, tz=tz.tzlocal())
            weather_icon_name = one_call.current.weather_icon_name

            draw = ImageDraw.Draw(frame)
            draw.text((3,3), str(min_temp), self.low_color, font=self.font)
            draw.text((13,3), str(curr_temp), self.text_color, font=self.font)
            draw.text((23,3), str(max_temp), self.high_color, font=self.font)

            draw.text((3,10), 'RAIN', self.text_color, font=self.font)
            draw.text((21,10), str(rain) + '%', (82, 180, 255), font=self.font)

            draw.text((3,24), 'HUMIDITY', self.text_color, font=self.font)
            draw.text((37,24), str(humidity) + '%', (82, 180, 255), font=self.font)

            currentTime = datetime.now(tz=tz.tzlocal())
            if (currentTime.hour > dtsr.hour and currentTime.hour <= dtss.hour):
                draw.text((3,17), 'SET', self.text_color , font=self.font)
                hours = dtss.hour % 12
                if (hours == 0):
                    hours += 12 
                draw.text((17,17), str(hours) + ':' + convertToTwoDigits(dtss.minute), (0, 29, 217), font=self.font)
            else:
                draw.text((3,17), 'RISE', (self.text_color), font=self.font)
                hours = dtsr.hour % 12
                if (hours == 0):
                    hours += 12 
                draw.text((21,17), str(hours) + ':' + convertToTwoDigits(dtsr.minute), (245, 206, 66), font=self.font)

            if weather_icon_name in self.icons:
                frame.paste(self.icons[weather_icon_name], (40,1))

            # Dealing with time:
            timeString = currentTime.strftime("%I:%M:%S %p")
            dateString = currentTime.strftime("%a, %b %w")

            #to center text:
            wD, hD = self.font.getsize(dateString)
            wT, hT = self.font.getsize(timeString)

            draw.text(((64-wT)/2, 40), timeString, self.text_color, font=self.font)
            draw.text(((64 - wD) / 2, 47), dateString, (161, 255, 220), font=self.font)
        
        return frame

def generateIconMap():
    icon_map = dict()
    for _, _, files in os.walk("apps_v2/res/weather"):
        for file in files:
            if file.endswith('.png'):
                icon_map[file[:-4]] = Image.open('apps_v2/res/weather/' + file).convert("RGB")
    return icon_map

def convertToTwoDigits(num):
    if num < 10:
        return '0' + str(num)
    return str(num)