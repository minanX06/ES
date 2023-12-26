from urllib.parse import urlencode, quote_plus
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from PIL import Image

url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst'
serviceKey = 'serviceKey'

now = datetime.now()
today = datetime.today().strftime("%Y%m%d")
y = date.today() - timedelta(days=1)
yesterday = y.strftime("%Y%m%d")
if now.minute < 45:
    if now.hour==0:
        base_time = "2330"
        base_date = yesterday
    else:
        pre_hour = now.hour-1
        if pre_hour < 10:
            base_time = "0" + str(pre_hour) + "30"
        else:
            base_time = str(pre_hour) + "30"
        base_date = today
else:
    if now.hour < 10:
        base_time = "0" + str(now.hour) + "30"
    else:
        base_time = str(now.hour) + "30"
    base_date = today

nx = 63
ny = 102

queryParams = '?' + urlencode({ quote_plus('serviceKey') : serviceKey, quote_plus('base_date') : base_date,
                                quote_plus('base_time') : base_time, quote_plus('nx') : nx, quote_plus('ny') : ny,
                                quote_plus('dataType') : 'xml', quote_plus('numOfRows') : '60'})

dic = {}
now_code = int(str(now.hour) + str(now.minute))

response = requests.get(url + queryParams)
soup = BeautifulSoup(response.content, 'xml')

time_Min = 10000
sky_situation = str()
fcst_time = int()

for item in soup.find_all('item'):
    if str(item.category.string) =='SKY':
        time_lag = abs(int(str(item.fcstTime.string))-now_code)
        if time_lag < time_Min:
            time_Min = time_lag
            fcst_time = int(str(item.fcstTime.string))
            sky_situation = int(str(item.fcstValue.string))

for item in soup.find_all('item'):
    if int(str(item.fcstTime.string)) == fcst_time:
        if str(item.category.string) =='PTY':
            is_rain = int(str(item.fcstValue.string))
        if str(item.category.string) =='VEC':
            wind_deg = int(str(item.fcstValue.string))
        if str(item.category.string) =='WSD':
            wind_speed = int(str(item.fcstValue.string))

#--------------------------------------------------#

bg = Image.open('Img/white.png')

if sky_situation == 1:
    cloud = Image.open('Img/clear.png')
elif sky_situation == 3:
    cloud = Image.open('Img/cloudy.png')
elif sky_situation == 4:
    cloud = Image.open('Img/gray.png')

if wind_speed < 14:
    wind_speed = Image.open('Img/slow.png')
elif wind_speed >= 14 and wind_speed < 21:
    wind_speed = Image.open('Img/medium.png')
elif wind_speed >= 21:
    wind_speed = Image.open('Img/fast.png')

wind_speed = wind_speed.rotate(wind_deg)

if is_rain == 1 or is_rain == 5:
    weather = Image.open('Img/rain.png')
elif is_rain == 2 or is_rain == 6:
    weather = Image.open('Img/rain+snow.png')
elif is_rain == 3 or is_rain == 7:
    weather = Image.open('Img/snow.png')

combined = Image.alpha_composite(bg.convert('RGBA'), wind_speed.convert('RGBA'))
combined = Image.alpha_composite(combined.convert('RGBA'), cloud.convert('RGBA'))

if is_rain != 0:
    combined = Image.alpha_composite(combined.convert('RGBA'), weather.convert('RGBA'))

combined.show()