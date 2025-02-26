 -- VENUE
 SELECT * FROM "Venue";
 INSERT INTO "Venue" VALUES (
    2,
    'Hey Jazzy BO',
    '{"JAZZ"}',
    'London',
    'AL',
    '27 Cavatina Point',
    '3211434',
    'NOE',
    TRUE,
    'Come funk our place',
    'https://www.obonparis.com/uploads/Paris%20Jazz%20Bar%20or%20Club/39094-le-baiser-sale-club-de-jazz-bois.jpg',
    'LINK'
 );

 -- ARTIST
 SELECT * FROM "Artist";

 INSERT INTO "Artist" VALUES (
    1,
    'Master Flunk Flex',
    'London',
    'AL',
    '3211434',
    '{"JAZZ"}',
    'NOE',
    TRUE,
    'I am searching yall!',
    'https://offloadmedia.feverup.com/secretldn.com/wp-content/uploads/2022/08/25135727/g22ad29d151b025c9725957ea57e9e81b2175909b39d37eb33e18bbf20b15ce6cf043d87ef02511a557028470b8525fbdc68e7af809667f258ed4bfe5e193840e_1280-1024x682.jpg',
    'LINK'
 );

 -- SHOWS
 SELECT setval(pg_get_serial_sequence('"Show"', 'id'), COALESCE(MAX(id), 1), true) FROM "Show";

 SELECT * FROM "Show";
 INSERT INTO "Show" VALUES (

    2,
    1,
    2,
    '2023-05-26 11:48:04'
 )