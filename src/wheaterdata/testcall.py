import requests as re
import datetime
import json


key = "e9605469cc89a06cc714efc3b55484da"
city_name = "Erlangen"
country_code = "DE"
start = 1747386702
end = 1747832367
cnt = 10

# request = f"https://history.openweathermap.org/data/2.5/history/city?q={city_name},{country_code}&type=hour&start={start}&end={end}&appid={key}"
# request = f"https://history.openweathermap.org/data/2.5/history/city?q={city_name},{country_code}&type=hour&start={start}&cnt={cnt}&appid={key}"

#Test da die ersten beiden Anfragen nicht funktioniert haben
erlangen_req = f"https://history.openweathermap.org/data/2.5/history/city?lat=49.58&lon=-11.02&appid={key}"


print (erlangen_req)
res = re.get(erlangen_req)

print(res.content)