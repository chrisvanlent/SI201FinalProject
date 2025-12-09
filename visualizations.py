import sqlite3
import matplotlib.pyplot as plt

DB_NAME = "football_weather.db"   # make sure this matches the db filename

def get_connection():
    return sqlite3.connect(DB_NAME)

# 1) scatter: total points vs temp
def vis_points_vs_temp():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT w.temp_max,
               (g.home_points + g.away_points) AS total_points
        FROM games g
        JOIN weather w ON g.weather_id = w.weather_id
        WHERE g.home_points IS NOT NULL
          AND g.away_points IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()

    temps = [r[0] for r in rows]
    points = [r[1] for r in rows]

    plt.figure(figsize=(8, 6))
    plt.scatter(temps, points, alpha=0.7)
    plt.xlabel("Max Temperature (°C)")
    plt.ylabel("Total Points")
    plt.title("Total Points vs Max Temperature")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig("vis1_points_vs_temp.png")
    plt.close()

# 2) bar: avg points by rain bucket
def vis_points_by_rain_bucket():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            CASE
                WHEN w.precipitation = 0 THEN 'No rain'
                WHEN w.precipitation <= 5 THEN 'Light (0-5mm)'
                ELSE 'Heavy (>5mm)'
            END AS rain_bucket,
            AVG(g.home_points + g.away_points) AS avg_points
        FROM games g
        JOIN weather w ON g.weather_id = w.weather_id
        WHERE g.home_points IS NOT NULL
          AND g.away_points IS NOT NULL
        GROUP BY rain_bucket
        ORDER BY avg_points DESC
    """)
    rows = cur.fetchall()
    conn.close()

    buckets = [r[0] for r in rows]
    avgs = [r[1] for r in rows]

    plt.figure(figsize=(8, 6))
    bars = plt.bar(buckets, avgs)
    plt.xlabel("Rain Level")
    plt.ylabel("Average Total Points")
    plt.title("Average Total Points by Rain Level")

    for bar, val in zip(bars, avgs):
        plt.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.3,
                 f"{val:.1f}",
                 ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig("vis2_points_by_rain_bucket.png")
    plt.close()

# 3) bar: avg temp by city
def vis_avg_temp_by_city():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.city_name,
               AVG(w.temp_max) AS avg_temp
        FROM games g
        JOIN weather w ON g.weather_id = w.weather_id
        JOIN cities c ON g.city_id = c.city_id
        GROUP BY c.city_name
        ORDER BY avg_temp DESC
    """)
    rows = cur.fetchall()
    conn.close()

    cities = [r[0] for r in rows]
    temps = [r[1] for r in rows]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(cities, temps)
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("City")
    plt.ylabel("Average Max Temperature (°C)")
    plt.title("Average Game-Day Max Temperature by City")

    for bar, val in zip(bars, temps):
        plt.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.2,
                 f"{val:.1f}",
                 ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    plt.savefig("vis3_avg_temp_by_city.png")
    plt.close()

def main():
    vis_points_vs_temp()
    vis_points_by_rain_bucket()
    vis_avg_temp_by_city()

if __name__ == "__main__":
    main()