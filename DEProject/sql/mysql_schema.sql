CREATE DATABASE IF NOT EXISTS city_weather;

USE city_weather;

CREATE TABLE IF NOT EXISTS cities (
    city_id INT PRIMARY KEY AUTO_INCREMENT,
    city_name VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    temperature DECIMAL(10, 2) NOT NULL,
    humidity DECIMAL(5, 2) NOT NULL,
    weather_condition VARCHAR(255) NOT NULL,
    recorded_at VARCHAR(40) NOT NULL
);