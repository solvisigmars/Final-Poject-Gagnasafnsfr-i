-- Task C3: Reconstruct the database
-- Nýtt og endurbætt skema fyrir OrkuflaediIsland
-- Passar við ER diagram (Orku Eining supertype með discriminator D)
-- ================================================

CREATE SCHEMA raforka;


-- ================================================
-- 1. ORKU_EINING (Supertype)
--    Sameiginlegir dálkar Millistöðvar og Virkjunar.
--    Discriminator dálkur 'tegund' svarar til D í ER diagrami.
-- ================================================
CREATE TABLE raforka.orku_eining (
    id      SERIAL           PRIMARY KEY,
    heiti   TEXT             NOT NULL UNIQUE,
    eigandi TEXT,
    stofnad DATE,                        -- var: ar/manudir/dagur_uppsett (3 dálkar → 1)
    x_hnit  DOUBLE PRECISION,
    y_hnit  DOUBLE PRECISION,
    tegund  TEXT             NOT NULL    -- discriminator: 'millistod' eða 'virkjun'
                CHECK (tegund IN ('millistod', 'virkjun'))
);


-- ================================================
-- 2. MILLISTODVAR (Subtype af orku_eining)
--    Deilir ID með orku_eining (joined table inheritance).
--    Bætir við tegund_stod sem er sérstakt fyrir millistöðvar.
-- ================================================
CREATE TABLE raforka.millistodvar (
    id          INTEGER PRIMARY KEY REFERENCES raforka.orku_eining(id) ON DELETE CASCADE,
    tegund_stod TEXT            -- t.d. 'Aðveitustöð'
);


-- ================================================
-- 3. MILLISTOD_TENGINGAR (Transmission lines milli millistöðva)
--    Vantar algerlega í gamla skema.
--    Geymir fjarlægð (reiknað úr hnitunum) og hámarksafköst.
--    Nauðsynlegt fyrir Task F (Substation Flow Estimation).
-- ================================================
CREATE TABLE raforka.millistod_tengingar (
    id               SERIAL  PRIMARY KEY,
    fra_millistod_id INTEGER NOT NULL REFERENCES raforka.millistodvar(id),
    til_millistod_id INTEGER NOT NULL REFERENCES raforka.millistodvar(id),
    fjarlægd_km      NUMERIC,           -- reiknað úr x_hnit/y_hnit á orku_eining
    max_capacity_mw  NUMERIC,           -- hámarksafköst línunnar (uppfært í Task F)
    CHECK (fra_millistod_id <> til_millistod_id)
);


-- ================================================
-- 4. VIRKJANIR (Subtype af orku_eining)
--    Deilir ID með orku_eining (joined table inheritance).
--    tengd_millistod_id kemur í stað lausu textarinnar tengd_stod.
-- ================================================
CREATE TABLE raforka.virkjanir (
    id                 INTEGER PRIMARY KEY REFERENCES raforka.orku_eining(id) ON DELETE CASCADE,
    tegund_stod        TEXT,                              -- t.d. 'Vindmylla', 'Vatnsafl'
    tengd_millistod_id INTEGER REFERENCES raforka.millistodvar(id)
                       -- FK í stað laus texti (tengd_stod) í gamla skema
);


-- ================================================
-- 5. VIDSKIPTAVINIR (Customers / End users)
--    Kemur í stað notendur_skraning.
--    'heiti' = viðskiptavina-nafnið (var eigandi í gamla skema)
--    'lysing' = tegund viðskiptavinar (var heiti í gamla skema)
-- ================================================
CREATE TABLE raforka.vidskiptavinir (
    id        SERIAL PRIMARY KEY,
    heiti     TEXT   NOT NULL UNIQUE,   -- t.d. 'Laxey ehf' (var eigandi í gamla skema)
    lysing    TEXT,                     -- t.d. 'FishFactory' (var heiti í gamla skema)
    kennitala TEXT   UNIQUE,
    stofnad   DATE,                     -- var: ar_stofnad (integer) í gamla skema
    x_hnit    DOUBLE PRECISION,
    y_hnit    DOUBLE PRECISION
);


-- ================================================
-- 6. MAELINGAR (Measurements)
--    Kemur í stað orku_maelingar.
--    Öll textaviðföng eru nú foreign keys.
--    timi er TIMESTAMPTZ (var timestamp without time zone).
--    gildi_kwh er NUMERIC með CHECK >= 0.
-- ================================================
CREATE TABLE raforka.maelingar (
    id                 SERIAL      PRIMARY KEY,
    virkjun_id         INTEGER     NOT NULL REFERENCES raforka.virkjanir(id),
    tegund_maelingar   TEXT        NOT NULL
                           CHECK (tegund_maelingar IN ('Framleiðsla', 'Innmötun', 'Úttekt')),
    sendandi_maelingar TEXT,       -- eigandi virkjunar (Framleiðsla) eða millistöð (Innmötun/Úttekt)
    timi               TIMESTAMPTZ NOT NULL,
    gildi_kwh          NUMERIC     NOT NULL CHECK (gildi_kwh >= 0),
    vidskiptavinur_id  INTEGER     REFERENCES raforka.vidskiptavinir(id)
                       -- NULL fyrir Framleiðsla og Innmötun, NOT NULL fyrir Úttekt
);


-- ================================================
-- Task D1: Indexing strategy
-- Allar þrjár fyrirspurnirnar fara gegnum tímasvið og virkjun.
-- ================================================

-- Tíma-index: allar þrjár fyrirspurnir nota from_date/to_date
CREATE INDEX idx_maelingar_timi
    ON raforka.maelingar(timi);

-- Samsett index fyrir algengustu mynstur: virkjun + tími + tegund
-- Stydur fyrirspurn 1 (energy flow) og 3 (loss ratio) beint
CREATE INDEX idx_maelingar_virkjun_timi_tegund
    ON raforka.maelingar(virkjun_id, timi, tegund_maelingar);

-- Index fyrir viðskiptavin: fyrirspurn 2 (customer usage) notar þetta
CREATE INDEX idx_maelingar_vidskiptavinur_timi
    ON raforka.maelingar(vidskiptavinur_id, timi);
