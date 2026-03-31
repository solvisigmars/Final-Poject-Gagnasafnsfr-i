-- Task D

CREATE INDEX idx_maelingar_virkjun_timi
ON raforka.maelingar (virkjun_id, timi);

CREATE INDEX idx_maelingar_virkjun_tegund_timi
ON raforka.maelingar (virkjun_id, tegund_maelingar, timi);

CREATE INDEX idx_maelingar_vidskiptavinur_timi
ON raforka.maelingar (vidskiptavinur_id, timi);

CREATE INDEX idx_maelingar_tegund_timi
ON raforka.maelingar (tegund_maelingar, timi);