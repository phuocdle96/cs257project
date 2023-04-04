-- Create company_type table to store types of companies involved in movie production and distribution(r1)

CREATE TABLE company_type (
    id INT PRIMARY KEY,
    kind VARCHAR(50)
);

-- Create info_type table to store various types of information related to movies(r2)
CREATE TABLE info_type (
    id INT PRIMARY KEY,
    info VARCHAR(50)
);


-- Create movie_companies table to store relationships between movies and the companies involved(r3)

CREATE TABLE movie_companies (
    id INT PRIMARY KEY,
    company_type_id INT,
    movie_id INT,
    note VARCHAR(100),
    FOREIGN KEY (company_type_id) REFERENCES company_type(id),
    FOREIGN KEY (movie_id) REFERENCES title(id)
);

-- Create movie_info_idx table to store relationships between movies and their information(r4)
CREATE TABLE movie_info_idx (
    id INT PRIMARY KEY,
    movie_id INT,
    info_type_id INT,
    FOREIGN KEY (movie_id) REFERENCES title(id),
    FOREIGN KEY (info_type_id) REFERENCES info_type(id)
);


-- Create title table to store movie titles and their production years(r5)
CREATE TABLE title (
    id INT PRIMARY KEY,
    title VARCHAR(100),
    production_year INT
);


-- Create cinema table to store screening schedules for movies(r6)
CREATE TABLE cinema (
    id INT PRIMARY KEY,
    title_id INT,
    screening_time TIMESTAMP,
    theater_number INT,
    FOREIGN KEY (title_id) REFERENCES title(id)
);




-- Insert company types
INSERT INTO company_type (id, kind) VALUES
(1, 'production companies'),
(2, 'distribution companies'),
(3, 'studios');

INSERT INTO info_type (id, info) VALUES
(1, 'top 250 rank'),
(2, 'box office'),
(3, 'awards');

INSERT INTO movie_companies (id, company_type_id, movie_id, note) VALUES
(1, 1, 1, '(co-production)'),
(2, 1, 2, '(presents)'),
(3, 2, 3, '(distribution)'),
(4, 2, 4, '(distribution)'),
(5, 3, 5, '(studio)'),
(6, 3, 6, '(studio)'),
(7, 1, 7, '(co-production)'),
(8, 2, 8, '(distribution)'),
(9, 2, 9, '(distribution)'),
(10, 3, 10, '(studio)');

INSERT INTO movie_info_idx (id, movie_id, info_type_id) VALUES
(1, 1, 1),
(2, 1, 2),
(3, 2, 1),
(4, 2, 3),
(5, 3, 1),
(6, 4, 2),
(7, 5, 1),
(8, 6, 1),
(9, 7, 1),
(10, 8, 2);

INSERT INTO title (id, title, production_year) VALUES
(1, 'The Godfather', 1972),
(2, 'The Godfather: Part II', 1974),
(3, 'Star Wars', 1977),
(4, 'Jaws', 1975),
(5, 'E.T. the Extra-Terrestrial', 1982),
(6, 'Jurassic Park', 1993),
(7, 'Pulp Fiction', 1994),
(8, 'Forrest Gump', 1994),
(9, 'The Lion King', 1994),
(10, 'Titanic', 1997);

INSERT INTO cinema (id, title_id, screening_time, theater_number) VALUES
(1, 1, '2023-04-01 10:00:00', 1),
(2, 1, '2023-04-02 13:30:00', 2),
(3, 2, '2023-04-02 16:00:00', 3),
(4, 3, '2023-04-03 18:00:00', 4),
(5, 3, '2023-04-04 20:30:00', 1),
(6, 4, '2023-04-04 12:00:00', 2),
(7, 5, '2023-04-05 14:00:00', 3),
(8, 6, '2023-04-05 16:30:00', 4),
(9, 7, '2023-04-06 19:00:00', 1),
(10, 8, '2023-04-07 21:00:00', 2);
--      ------------------------------------

SELECT MIN(mc.note) AS production_note,
       MIN(t.title) AS movie_title,
       MIN(t.production_year) AS movie_year,
       MIN(c.screening_time) AS screening_time,
       MIN(c.theater_number) AS theater_number
FROM company_type AS ct
JOIN movie_companies AS mc ON ct.id = mc.company_type_id
JOIN title AS t ON t.id = mc.movie_id
JOIN movie_info_idx AS mi_idx ON t.id = mi_idx.movie_id
JOIN info_type AS it ON it.id = mi_idx.info_type_id
JOIN cinema AS c ON c.title_id = t.id
WHERE ct.kind = 'production companies'
  AND it.info = 'top 250 rank'
  AND mc.note NOT LIKE '%(as Metro-Goldwyn-Mayer Pictures)%'
  AND (mc.note LIKE '%(co-production)%' OR mc.note LIKE '%(presents)%')
  AND c.screening_time BETWEEN '2023-04-01 00:00:00' AND '2023-04-07 23:59:59'
GROUP BY t.id, c.theater_number;
