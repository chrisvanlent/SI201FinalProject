SELECT
    c.city_name,
    COUNT(*) AS num_games,
    ROUND(AVG(w.temp_max), 1) AS avg_temp_max,
    ROUND(AVG(g.home_points + g.away_points), 1) AS avg_total_points
FROM games AS g
JOIN cities AS c
    ON g.city_id = c.city_id
JOIN weather AS w
    ON g.weather_id = w.weather_id
GROUP BY c.city_id, c.city_name
ORDER BY num_games DESC;

SELECT
    CASE 
        WHEN w.precipitation > 0 THEN 'Wet (rain/snow)'
        ELSE 'Dry'
    END AS weather_type,
    COUNT(*) AS num_games,
    ROUND(AVG(g.home_points + g.away_points), 1) AS avg_total_points
FROM games AS g
JOIN weather AS w
    ON g.weather_id = w.weather_id
GROUP BY weather_type;

SELECT
    CASE
        WHEN c.latitude >= 40 THEN 'Northern cities (lat ≥ 40)'
        ELSE 'Southern cities (lat < 40)'
    END AS region,
    COUNT(*) AS num_games,
    ROUND(AVG(g.home_points), 1) AS avg_home_points,
    ROUND(AVG(g.away_points), 1) AS avg_away_points,
    ROUND(AVG(g.home_points - g.away_points), 1) AS avg_home_margin
FROM games AS g
JOIN cities AS c
    ON g.city_id = c.city_id
GROUP BY region
ORDER BY region;