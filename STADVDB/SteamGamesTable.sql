DROP DATABASE IF EXISTS steamGames;
CREATE DATABASE steamGames;

USE steamGames;

CREATE TABLE steamGames (
    appid INT PRIMARY KEY,
    name TEXT,
    price DECIMAL(10, 2),
    releasedate_cleaned DATE
);

SELECT * FROM steamGames;
