BEGIN;

TRUNCATE TABLE
    raforka.maelingar,
    raforka.millistod_tengingar,
    raforka.virkjanir,
    raforka.millistodvar,
    raforka.vidskiptavinir,
    raforka.orku_eining
CASCADE;


INSERT INTO raforka.orku_eining (
    heiti,
    eigandi,
    stofnad,
    x_hnit,
    y_hnit,
    tegund
)
SELECT
    l.heiti,
    l.eigandi,
    MAKE_DATE(l.ar_uppsett, l.manudir_uppsett, l.dagur_uppsett) AS stofnad,
    l."X_HNIT",
    l."Y_HNIT",
    CASE
        WHEN l.tegund = 'stod' THEN 'millistod'
        WHEN l.tegund = 'virkjun' THEN 'virkjun'
    END AS tegund
FROM raforka_legacy.orku_einingar l;


INSERT INTO raforka.millistodvar (
    id,
    tegund_stod
)
SELECT
    oe.id,
    l.tegund_stod
FROM raforka_legacy.orku_einingar l
JOIN raforka.orku_eining oe
    ON oe.heiti = l.heiti
WHERE l.tegund = 'stod';


INSERT INTO raforka.virkjanir (
    id,
    tegund_stod,
    tengd_millistod_id
)
SELECT
    oe.id,
    l.tegund_stod,
    ms.id
FROM raforka_legacy.orku_einingar l
JOIN raforka.orku_eining oe
    ON oe.heiti = l.heiti
LEFT JOIN raforka.orku_eining oe_ms
    ON oe_ms.heiti = l.tengd_stod
LEFT JOIN raforka.millistodvar ms
    ON ms.id = oe_ms.id
WHERE l.tegund = 'virkjun';




INSERT INTO raforka.vidskiptavinir (
    heiti,
    lysing,
    kennitala,
    stofnad,
    x_hnit,
    y_hnit
)
SELECT
    n.heiti,
    n.eigandi AS lysing,
    n.kennitala,
    MAKE_DATE(n.ar_stofnad, 1, 1) AS stofnad,
    n."X_HNIT",
    n."Y_HNIT"
FROM raforka_legacy.notendur_skraning n;




INSERT INTO raforka.millistod_tengingar (
    fra_millistod_id,
    til_millistod_id,
    fjarlægd_km,
    max_capacity_mw
)
SELECT
    ms_from.id,
    ms_to.id,
    NULL AS fjarlægd_km,
    NULL AS max_capacity_mw
FROM raforka_legacy.orku_einingar l
JOIN raforka.orku_eining oe_from
    ON oe_from.heiti = l.heiti
JOIN raforka.millistodvar ms_from
    ON ms_from.id = oe_from.id
JOIN raforka.orku_eining oe_to
    ON oe_to.heiti = l.tengd_stod
JOIN raforka.millistodvar ms_to
    ON ms_to.id = oe_to.id
WHERE l.tegund = 'stod'
  AND l.tengd_stod IS NOT NULL;


INSERT INTO raforka.maelingar (
    virkjun_id,
    tegund_maelingar,
    sendandi_maelingar,
    timi,
    gildi_kwh,
    vidskiptavinur_id
)
SELECT
    v.id,
    m.tegund_maelingar,
    m.sendandi_maelingar,
    m.timi,
    m.gildi_kwh,
    c.id
FROM raforka_legacy.orku_maelingar m
JOIN raforka.orku_eining oe
    ON oe.heiti = m.eining_heiti
JOIN raforka.virkjanir v
    ON v.id = oe.id
LEFT JOIN raforka.vidskiptavinir c
    ON c.lysing = m.notandi_heiti;

COMMIT;