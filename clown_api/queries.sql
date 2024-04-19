SELECT * FROM clown;

SELECT c.clown_id, c.clown_name, s.speciality_name, AVG(r.rating) as Average_rating
FROM clown as c
JOIN speciality as s USING(speciality_id)
LEFT JOIN review as r USING(clown_id)
GROUP BY c.clown_id, c.clown_name, s.speciality_name
ORDER BY AVG(r.rating) DESC;

-- clown_name, speciality_name

-- AVG(r.rating) as Average_rating