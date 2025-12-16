import requests
import sqlite3
import json
import pprint

#def drop_tables(cur,conn):
    # Followed commands from online
 #   commands = [
  #      "DROP TABLE IF EXISTS cities",
   #     "DROP TABLE IF EXISTS teams",
    #    "DROP TABLE IF EXISTS gamedates",
     #   "DROP TABLE IF EXISTS games",
      #  "DROP TABLE IF EXISTS weather",]
    
   # for command in commands:
    #    cur.execute(command)



# Creating My Tables
def create_tables(cur, conn):

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        city_id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_name TEXT NOT NULL UNIQUE,
        latitude REAL,
        longitude REAL,
        elevation INTEGER
    );""")
    
    
    
    cur.execute("""            
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY,
        team_name TEXT NOT NULL
    );""")

    cur.execute("""                
    CREATE TABLE IF NOT EXISTS gamedates (
        date_id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_date TEXT NOT NULL UNIQUE
    );""")  

    cur.execute("""   
    CREATE TABLE IF NOT EXISTS games (
        game_id INTEGER PRIMARY KEY,
        home_team_id INTEGER NOT NULL,
        away_team_id INTEGER NOT NULL,
        home_points INTEGER,
        away_points INTEGER,
        city_id INTEGER NOT NULL,
        date_id INTEGER NOT NULL,
        weather_id INTEGER NOT NULL,
                
    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    FOREIGN KEY (date_id) REFERENCES gamedates(date_id),
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (weather_id) REFERENCES weather(weather_id)
    );""")  
  
    cur.execute("""              
    CREATE TABLE IF NOT EXISTS weather (
        weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER NOT NULL,
        date_id INTEGER NOT NULL,
        temp_max FLOAT,
        temp_min FLOAT,
        precipitation FLOAT,
        windspeed_max FLOAT,

    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    FOREIGN KEY (date_id) REFERENCES gamedates(date_id)
);""")  
    
    conn.commit()  


def insert_into_table(data, data_name, id_name, table, cur, conn):
    # Inputs: data, data_name (str), id_name (str), table(str), cur and conn
    # Outputs: data_id (int)

    # Tries for find data in table
    command = "SELECT " + id_name + " FROM " + table + " WHERE " + data_name + " = ?;"
    cur.execute(command, (data,))
    row = cur.fetchone()
    
    # Returns id if data exists is table
    if row:
        id = row[0]

    # Adds data into table and returns id if data doesn't already exist in table
    else:
        command = "INSERT INTO " + table + " (" + data_name + ") VALUES (?);"
        cur.execute(command, (data,))
        id = cur.lastrowid

        conn.commit()

    return id


def insert_game_data(data, cur, conn):

    cur.execute(
        """
        SELECT EXISTS(
            SELECT 1 FROM games WHERE game_id = ?
        )
        """,
        (data["game_id"],)
    )

    result = cur.fetchone()[0]
    
    if result == 1:
        print("Game ID: " + str(data["game_id"]) + " already in table")
        return 0
    
    print("Game ID: " + str(data["game_id"]) + " added to table")

    home_team_id = insert_into_table(data["home_team_name"], "team_name", "team_id", "teams", cur, conn)
    away_team_id = insert_into_table(data["away_team_name"], "team_name", "team_id", "teams", cur, conn)
    date_id = insert_into_table(data["date"], "game_date", "date_id", "gamedates", cur, conn)
    city_id = insert_into_table(data["city"], "city_name", "city_name", "cities", cur, conn)

    cords = get_city_coords(data["city"])
    elevation = get_elevation(cords["longitude"], cords["latitude"])

    cur.execute("""
    UPDATE cities
    SET latitude = ?, longitude = ?, elevation = ?
    WHERE city_id = ?;
    """, (cords["latitude"], cords["longitude"], elevation, city_id))

    weather = get_past_weather(cords["latitude"], cords["longitude"], data["date"])

    cur.execute("""
    INSERT INTO weather (city_id, date_id, temp_max, temp_min, precipitation, windspeed_max)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (city_id, date_id, weather["temp_max"], weather["temp_min"], weather["precipitation"], weather["wind_max"]))

    weather_id = cur.lastrowid


    cur.execute("""
    INSERT INTO games (game_id, home_team_id, away_team_id, home_points, away_points, date_id, city_id, weather_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (data["game_id"], home_team_id, away_team_id, data["home_team_points"], data["away_team_points"], date_id, city_id, weather_id))

    conn.commit()

    return 1





def get_football_results():
    # Input: None
    # Output: List of Dictonaries, each dictionary is a game and contains home_team_name(str), away_team_name(str), home_team_points(int), away_team_points(int), date(str), city(str)

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
            "game_id": game["id"],
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
    # Input: City name (str)
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

def get_elevation(lon, lat):
    # Input: Latitude (float) and Longitude (float)
    # Output: elevation (float)

    link = "https://api.open-elevation.com/api/v1/lookup?locations=" + str(lat) + "," + str(lon)

    weather_data = requests.get(link)

    d = weather_data.json()["results"][0]

    return d["elevation"]





def main():

    db_path = "football_weather.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    #drop_tables(cur, conn)

    cords = get_city_coords("Ann Arbor")
    print(cords)
    aaElevation = get_elevation(cords["longitude"], cords["latitude"])
    print(aaElevation)

    create_tables(cur, conn)

    games = get_football_results()

    count = 0
    for i in range(len(games)):
        count += insert_game_data(games[i], cur, conn)
        print(count)
        if count >= 25:
            break
        
    insert_game_data(games[13], cur, conn)

if __name__ == "__main__":
    main()
