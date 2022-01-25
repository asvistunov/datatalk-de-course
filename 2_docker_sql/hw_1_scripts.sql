SELECT count("index") FROM yellow_taxi_data ytd 
WHERE tpep_pickup_datetime::date = '2021-01-15'



SELECT tpep_pickup_datetime::date, max(tip_amount) FROM yellow_taxi_data ytd 
WHERE EXTRACT(MONTH FROM tpep_pickup_datetime) = 1
	AND EXTRACT(YEAR FROM tpep_pickup_datetime) = 2021
GROUP BY tpep_pickup_datetime::date
ORDER BY max DESC 


SELECT "Zone", count(*) FROM yellow_taxi_data yd
JOIN zones_data zd ON zd."LocationID" = yd."DOLocationID"
WHERE tpep_pickup_datetime::date = '2021-01-14'
	AND "PULocationID" = 43
GROUP BY "Zone"
ORDER BY count DESC 

SELECT 
pairs."PUZone", 
pairs."DOZone", 
avg(pairs.total_amount) AS avg_price
FROM (
	SELECT 
	tpep_pickup_datetime, 
	tpep_dropoff_datetime, 
	trip_distance, 
	total_amount,
	"PULocationID", 
	zd2."Zone" AS "PUZone", 
	"DOLocationID",
	zd."Zone" AS "DOZone"
	FROM yellow_taxi_data yd
	JOIN zones_data zd ON zd."LocationID" = yd."DOLocationID"
	JOIN zones_data zd2 ON zd2."LocationID" = yd."PULocationID"
	WHERE EXTRACT(MONTH FROM tpep_pickup_datetime) = 1
		AND EXTRACT(YEAR FROM tpep_pickup_datetime) = 2021
) pairs 
GROUP BY pairs."PUZone", pairs."DOZone"
ORDER BY avg_price DESC 