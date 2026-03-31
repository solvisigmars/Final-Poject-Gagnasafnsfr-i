-- Task C3


CREATE SCHEMA raforka;

CREATE TABLE raforka.orku_eining (
    id      SERIAL           PRIMARY KEY,
    heiti   TEXT             NOT NULL UNIQUE,
    eigandi TEXT,
    stofnad DATE,                        -- var: ar/manudir/dagur_uppsett (3 dálkar → 1)
    x_hnit  DOUBLE PRECISION,
    y_hnit  DOUBLE PRECISION,
    tegund  TEXT             NOT NULL    -- þarf að vera: 'millistod' eða 'virkjun'
                CHECK (tegund IN ('millistod', 'virkjun'))
);


CREATE TABLE raforka.millistodvar (
    id          INTEGER PRIMARY KEY REFERENCES raforka.orku_eining(id) ON DELETE CASCADE,
    tegund_stod TEXT            
);


CREATE TABLE raforka.millistod_tengingar (
    id               SERIAL  PRIMARY KEY,
    fra_millistod_id INTEGER NOT NULL REFERENCES raforka.millistodvar(id),
    til_millistod_id INTEGER NOT NULL REFERENCES raforka.millistodvar(id),
    fjarlægd_km      NUMERIC,           -- reiknað úr x_hnit/y_hnit á orku_eining
    max_capacity_mw  NUMERIC,           -- hámarksafköst línunnar (uppfært í Task F)
    CHECK (fra_millistod_id <> til_millistod_id)
);


CREATE TABLE raforka.virkjanir (
    id                 INTEGER PRIMARY KEY REFERENCES raforka.orku_eining(id) ON DELETE CASCADE,
    tegund_stod        TEXT,                              -- t.d. 'Vindmylla', 'Vatnsafl'
    tengd_millistod_id INTEGER REFERENCES raforka.millistodvar(id)
                       -- FK í stað laus texti (tengd_stod) í gamla skema
);


CREATE TABLE raforka.vidskiptavinir (
    id        SERIAL PRIMARY KEY,
    heiti     TEXT   NOT NULL UNIQUE,   
    lysing    TEXT,                     
    kennitala TEXT   UNIQUE,
    stofnad   DATE,                     
    x_hnit    DOUBLE PRECISION,
    y_hnit    DOUBLE PRECISION
);



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

