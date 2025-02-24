CREATE DATABASE fyyur;

UPDATE "Venue"
SET facebook_link = 'https://www.facebook.com/ParkSquareLiveMusicAndCoffee'
;

SELECT * FROM "Artist";
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
    2,
    1,
    '2025-06-03 20:00:00'
);

SELECT * FROM show;