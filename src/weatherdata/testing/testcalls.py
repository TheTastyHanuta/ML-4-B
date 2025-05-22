import requests as re
import json
import pandas


key = "1961fb1384d6bcc3fb39acdf228beb96"
city_name = "Nuremberg"
country_code = "DE"
start = 1716383627
end = 1747832367
cnt = 1


# request = f"https://history.openweathermap.org/data/2.5/history/city?q={city_name},{country_code}&type=hour&start={start}&end={end}&appid={key}"
request = f"https://history.openweathermap.org/data/2.5/history/city?q={city_name},{country_code}&type=hour&start={start}&cnt={cnt}&appid={key}"

#Test da die ersten beiden Anfragen nicht funktioniert haben
# erlangen_req = f"https://history.openweathermap.org/data/2.5/history/city?lat=49.58&lon=-11.02&appid={key}"


print (request)
res = re.get(request)

with open("./Data.json", "w") as write:
    write.write(str(json.loads(res.content)))
    print(res.content)