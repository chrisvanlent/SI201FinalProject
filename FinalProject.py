import requests
import sqlite3
import json






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
        team_name TEXT NOT NULL,
        city_id INTEGER NOT NULL,
        FOREIGN KEY (city_id) REFERENCES cities(city_id)
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
        neutral_site BOOLEAN DEFAULT 0,

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

    



def get_football_results(link):

    API_KEY = 'NvYq3srg3jWcngq2uVqbwXg4Kl3ESAEbOwsEzlXxh2V7uRf05RbrAt3qSQqIvkrM'

    headers = {
        "Authorization": "Bearer " + API_KEY
    }

    params = {
        "year": 2023,
        # "conference": "big ten",
        "seasonType": "postseason"
    }


    response = requests.get(link, headers=headers, params=params)

    print("Status:", response.status_code)
    for game in response.json():
        print(game["homeTeam"] + " vs " + game["awayTeam"])

    return response.json()





def get_past_weather(lat, lon, date_str):
    """
    Get daily weather summary for a specific date and location
    using Open-Meteo's free archive API (no key needed).

    Returns:
      {
        "date": "...",
        "temp_max": ...,
        "temp_min": ...,
        "precip_sum": ...,
        "wind_max": ...
      }
    """
    url = "https://archive-api.open-meteo.com/v1/archive"

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

    resp = requests.get(url, params=params)
    data = resp.json()

    if "daily" not in data or not data["daily"]["time"]:
        return None

    d = data["daily"]

    result = {
        "date": d["time"][0],
        "temp_max": d["temperature_2m_max"][0],
        "temp_min": d["temperature_2m_min"][0],
        "precip_sum": d["precipitation_sum"][0],
        "wind_max": d["windspeed_10m_max"][0]
    }

    return result




def get_city_coords(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name}

    r = requests.get(url, params=params).json()

    if "results" not in r or len(r["results"]) == 0:
        return None

    city = r["results"][0]

    return {
        "name": city["name"],
        "lat": city["latitude"],
        "lon": city["longitude"],
        "country": city.get("country")
    }




def main():

    # Ann Arbor, MI on 2024-11-20
    ann_arbor = get_past_weather(42.2808, -83.7430, "2024-11-20")
    print("Ann Arbor:", ann_arbor)


    coords = get_city_coords("Ann Arbor")
    print(coords)
    lat = coords['lat']
    long = coords['lon']


    data = get_info("https://api.collegefootballdata.com/games")
    
    print(len(data))
    

    db_path = "football_weather.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    create_tables(cur, conn)


if __name__ == "__main__":
    main()
