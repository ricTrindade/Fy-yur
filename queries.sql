CREATE DATABASE fyyur;

UPDATE "Artist"
SET seeking_description = 'YO, I am looking for a venue!!!'
WHERE seeking_venue = TRUE;

SELECT * FROM "Artist" ORDER BY id;
SELECT * FROM "Venue" ORDER BY id;
INSERT INTO "Venue" VALUES (
    4,
    'Dragao',
    'Porto',
    'Lisbon',
    '155 Helgrain ST',
    '12413415',
    'Link Here!',
    'Facebook Link here'
);

DELETE FROM "Venue" WHERE id = 4;


INSERT INTO "Artist" VALUES (
    4,
    'MrHamptons',
    'Sintra',
    'Lisbon',
    '123124531232',
    'Soulful Music',
    'linked',
    'Facebook'
);

INSERT INTO show VALUES (
    3,
    1,
    '2024-06-03 20:00:00'
);

SELECT * FROM show;

SELECT pg_get_serial_sequence('"Venue"', 'id');
SELECT setval('Artist_id_seq', (SELECT MAX(id) FROM "Artist"));

SELECT setval('"Venue_id_seq"', (SELECT MAX(id) FROM "Artist"));

DELETE FROM "Venue" WHERE id =6
;

CREATE DATABASE MigrateFyyurTest;
