CREATE DATABASE fyyur;

UPDATE "Artist"
SET image_link = 'https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80';

SELECT * FROM "Artist";
SELECT * FROM "Venue";
INSERT INTO "Venue" VALUES (
    3,
    'Dragao',
    'Porto',
    'Porto',
    '155 Helgrain ST',
    '12413415',
    'Link Here!',
    'Facebook Link here'
);


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