import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
import sqlite3

CSV_FILE_1 = "avg_temp_and_pts_by_city.csv"
CSV_FILE_2 = "finalproject_home_vs_away_by_lat.csv"
CSV_FILE_3 = "finalproject_wet_vs_dry.csv"

def vis_avg_metrics_by_city():
    try:
        df = pd.read_csv(CSV_FILE_1)
    except FileNotFoundError:
        print(f"Error: {CSV_FILE_1} not found. Please ensure the file is in the same directory.")
        return

    cities = df['city_name'].tolist()
    avg_temps = df['avg_temp_max'].tolist()
    avg_points = df['avg_total_points'].tolist() 

    x = np.arange(len(cities))  
    width = 0.35 

    fig, ax1 = plt.subplots(figsize=(12, 6))

    rects1 = ax1.bar(x - width/2, avg_temps, width, label='Avg Max Temp (°C)', color='skyblue')
    ax1.set_xlabel("City")
    ax1.set_ylabel("Average Max Temperature (°C)", color='skyblue')
    ax1.tick_params(axis='y', labelcolor='skyblue')
    ax1.set_xticks(x)
    ax1.set_xticklabels(cities, rotation=45, ha="right")
    ax1.grid(axis='y', linestyle='--', alpha=0.3)

    ax2 = ax1.twinx()  
    rects2 = ax2.bar(x + width/2, avg_points, width, label='Avg Total Points', color='coral')
    ax2.set_ylabel("Average Total Points", color='coral')
    ax2.tick_params(axis='y', labelcolor='coral')
    
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')

    plt.title("Average Max Temperature and Average Total Points by City")
    fig.tight_layout()
    plt.savefig("vis1_avg_metrics_by_city.png")
    plt.close()

def vis_avg_points_by_latitude_bucket():
    try:
        df = pd.read_csv(CSV_FILE_2)
    except FileNotFoundError:
        print(f"Error: {CSV_FILE_2} not found. Please ensure the file is in the same directory.")
        return

    df = df.sort_values(by='region', ascending=False) 

    buckets = df['region'].tolist()
    home_points = df['avg_home_points'].tolist()
    away_points = df['avg_away_points'].tolist()

    x = np.arange(len(buckets))
    width = 0.35

    plt.figure(figsize=(8, 6))
    rects1 = plt.bar(x - width/2, home_points, width, label='Average Home Points', color='darkblue')
    rects2 = plt.bar(x + width/2, away_points, width, label='Average Away Points', color='orange')

    plt.ylabel("Average Points")
    plt.title("Average Home vs. Away Points by Latitude")
    plt.xticks(x, buckets)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    def autolabel(rects, points):
        for rect, point in zip(rects, points):
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2., height + 0.5,
                     f'{point:.1f}',
                     ha='center', va='bottom', fontsize=9)

    autolabel(rects1, home_points)
    autolabel(rects2, away_points)

    plt.tight_layout()
    plt.savefig("vis2_points_by_latitude_bucket.png")
    plt.close()

def vis_avg_points_by_weather_type():
    try:
        df = pd.read_csv(CSV_FILE_3)
    except FileNotFoundError:
        print(f"Error: {CSV_FILE_3} not found. Please ensure the file is in the same directory.")
        return
    
    df['sort_order'] = df['weather_type'].apply(lambda x: 0 if x == 'Dry' else 1)
    df = df.sort_values(by='sort_order')

    types = df['weather_type'].tolist()
    avgs = df['avg_total_points'].tolist()

    plt.figure(figsize=(7, 6))
    bars = plt.bar(types, avgs, color=['darkgreen', 'gray'])
    plt.xlabel("Weather Type (Precipitation)")
    plt.ylabel("Average Total Points")
    plt.title("Average Total Points by Weather Type (Dry vs. Wet)")
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    for bar, val in zip(bars, avgs):
        plt.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.3,
                 f"{val:.1f}",
                 ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig("vis3_points_by_weather_type.png")
    plt.close()

def vis_visitor_points_vs_elevation(cur, conn):
   cur.execute("""
       SELECT c.elevation,
              g.away_points,
              g.home_points
       FROM games g
       JOIN cities c ON g.city_id = c.city_id
       WHERE g.away_points IS NOT NULL
         AND g.home_points IS NOT NULL
         AND c.elevation IS NOT NULL
         AND c.elevation > 0
   """)


   rows = cur.fetchall()


   elevations = np.array([r[0] for r in rows])
   away_points = np.array([r[1] for r in rows])
   home_points = np.array([r[2] for r in rows])


   # Green if away team wins, red if they lose
   colors = np.where(away_points > home_points, "green", "red")


   plt.figure(figsize=(8, 6))


   # Scatter plot with win/loss coloring
   plt.scatter(elevations, away_points, c=colors, alpha=0.7)


   # Line of best fit
   m, b = np.polyfit(elevations, away_points, 1)
   x_vals = np.linspace(elevations.min(), elevations.max(), 100)
   y_vals = m * x_vals + b
   plt.plot(x_vals, y_vals, linestyle="--", label="Best Fit Line")


   # Log scale for elevation
   plt.xscale("log")


   plt.xlabel("City Elevation (meters, log scale)")
   plt.ylabel("Visitor Points")
   plt.title("Visitor Points vs City Elevation (Log Scale)")
   plt.grid(True, which="both", linestyle="--", alpha=0.3)
   plt.tight_layout()
   plt.savefig("vis_visitor_points_vs_elevation_log.png")
   plt.close()

   conn.close()

def main():
    db_path = "football_weather.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    vis_avg_metrics_by_city()
    vis_avg_points_by_latitude_bucket()
    vis_avg_points_by_weather_type()
    vis_visitor_points_vs_elevation(cur, conn)

if __name__ == "__main__":
    main()