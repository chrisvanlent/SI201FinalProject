import requests
import sqlite3
import json
import pprint





# Creating My Tables
def create_tables(cur, conn):

# Followed commands from online
    commands = [
        "DROP TABLE IF EXISTS cities",
        "DROP TABLE IF EXISTS teams",
        "DROP TABLE IF EXISTS gamedates",
        "DROP TABLE IF EXISTS games",
        "DROP TABLE IF EXISTS weather",]
    
    for command in commands:
        cur.execute(command)


    cur.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        city_id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_name TEXT NOT NULL UNIQUE,
        latitude REAL,
        longitude REAL
    );""")
    
    
    
    cur.execute("""            
    CREATE TABLE teams (
        team_id INTEGER PRIMARY KEY,
        team_name TEXT NOT NULL
    );""")

    cur.execute("""                
    CREATE TABLE gamedates (
        date_id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_date TEXT NOT NULL UNIQUE
    );""")  

    cur.execute("""   
    CREATE TABLE games (
        game_id INTEGER PRIMARY KEY,
        date_id INTEGER NOT NULL,
        home_team_id INTEGER NOT NULL,
        away_team_id INTEGER NOT NULL,
        home_points INTEGER,
        away_points INTEGER,
        city_id INTEGER NOT NULL,
                
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
    FOREIGN KEY (date_id) REFERENCES gamedates(date_id),
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
    );""")  
  
    cur.execute("""              
    CREATE TABLE weather (
        weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER UNIQUE NOT NULL,
        temp_max FLOAT,
        temp_min FLOAT,
        precipitation FLOAT,
        windspeed_max FLOAT,
        latitude FLOAT,
        longitude FLOAT,

    FOREIGN KEY (game_id) REFERENCES games(game_id)
);""")  
    
    conn.commit()  

    


def insert_team_data(data):

    # pprint.pprint(data)
    pass





def get_football_results():
    # Input: None
    # Output: List of Dictonaries, each dictionary is a game and contains home_team_name(string), away_team_name(string), home_team_points(int), away_team_points(int), date(string), city(string)

    API_KEY = 'NvYq3srg3jWcngq2uVqbwXg4Kl3ESAEbOwsEzlXxh2V7uRf05RbrAt3qSQqIvkrM'
    link = "https://api.collegefootballdata.com"
    list = []

    headers = {
        "Authorization": "Bearer " + API_KEY
    }

    params = {
        "year": 2023,
        "week": 2,
        "seasonType": "regular"
    }

    # game_data conatins all info except city, venue_data conatins cities for each statiom 
    game_data = requests.get(link + "/games", headers=headers, params=params)
    venue_data = requests.get(link + "/venues", headers=headers)

    for game in game_data.json():
        inner = {
            "home_team_name": game["homeTeam"],
            "away_team_name": game["awayTeam"],
            "home_team_points": game["homePoints"],
            "away_team_points": game["awayPoints"],
            "date": game["startDate"][:10]
            }

        # taking stadiom from game_data and cross referancing with venue_data to find city
        for venue in venue_data.json():
            if venue["name"] == game["venue"]:
                inner["city"] = venue["city"]
                break
            
        list.append(inner)

    return list


def get_city_coords(city_name):
    # Input: City name (string)
    # Output: Dictionary containing Latitude (float) and Longitude (float)

    link = "https://geocoding-api.open-meteo.com/v1"

    params = {
        "name": city_name
        }

    city_data = requests.get(link + "/search", params=params).json()

    city = city_data["results"][0]

    return {"latitude": city["latitude"], "longitude": city["longitude"]}



def get_past_weather(lat, lon, date_str):
    # Input: Latitude (float) Longitude (float) and date (str)
    # Output: Dictionary containing temp_max (float) temp_min (float) precipitation (float) and wind_max (float)

    link = "https://archive-api.open-meteo.com/v1"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date_str,
        "end_date": date_str,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "windspeed_10m_max"
        ),
        "timezone": "America/Detroit"
    }

    weather_data = requests.get(link + "/archive", params=params)

    d = weather_data.json()["daily"]

    # All units are metric; Celcius, mm, km/h
    result = {
        "temp_max": d["temperature_2m_max"][0],
        "temp_min": d["temperature_2m_min"][0],
        "precipitation": d["precipitation_sum"][0],
        "wind_max": d["windspeed_10m_max"][0]
    }

    return result





def main():

    db_path = "football_weather.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    create_tables(cur, conn)

    games = get_football_results()
    print(games[0]["city"])

    coords = get_city_coords(games[0]["city"])
    print(coords)

    weather = get_past_weather(coords["latitude"], coords["longitude"], games[0]["date"])
    print(weather)


    insert_team_data(games)


if __name__ == "__main__":
    main()
