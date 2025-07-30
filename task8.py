import os
import json
from pprint import pprint

import requests
from dotenv import load_dotenv
from geopy import distance
import folium


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def new_structure(apikey, coffee):
    coords = fetch_coordinates(apikey, address = input("Где вы находитесь?"))
    print("Ваши координаты:", coords)
    your_longitude = coords[0]
    your_latitude = coords[1]
    new_coffee = []

    for coffee_shop in coffee:
        title = coffee_shop["Name"]
        longitude = coffee_shop["geoData"]["coordinates"][0]
        latitude = coffee_shop["geoData"]["coordinates"][1]
        dist = distance.distance((latitude, longitude), (your_latitude, your_longitude)).km
        new_coffee.append({
            "title": title,
            "distance": dist,
            "longitude": longitude,
            "latitude": latitude
        })

    five_closest_coffee(new_coffee=new_coffee, your_longitude=your_longitude, your_latitude=your_latitude)


def five_closest_coffee(new_coffee, your_longitude, your_latitude):
    def get_min_distance(coffee_shop):
        return coffee_shop['distance']

    sorted_coffee = sorted(new_coffee, key=get_min_distance)
    closest_five = sorted_coffee[:5]
    create_map(your_longitude=your_longitude, your_latitude=your_latitude, closest_five=closest_five)


def create_map(your_longitude, your_latitude, closest_five):
    m = folium.Map([your_latitude, your_longitude], zoom_start=15)

    for i in range(5):
        folium.Marker(
            location=[closest_five[i]['latitude'], closest_five[i]['longitude']],
            popup=closest_five[i]['title'],
            icon=folium.Icon(color='red')
        ).add_to(m)

    m.save("coffee_map.html")


def main():
    with open("coffee.json", "r") as my_file:
        coffee_json = my_file.read()
    coffee = json.loads(coffee_json)
    load_dotenv()
    apikey = os.getenv("APIKEY")
    new_structure(apikey=apikey, coffee=coffee)


if __name__ == "__main__":
    main()