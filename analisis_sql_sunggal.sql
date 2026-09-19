-- ==============================================================================
-- ANALISIS DATA OPERASIONAL IPA SUNGGAL - PERUMDA TIRTANADI
-- ==============================================================================

-- 1. Rekonsiliasi Neraca Air Global (Evaluasi total volume & persentase plant loss 30 hari)
SELECT 
    COUNT(*) as total_jam_evaluasi,
    ROUND(SUM(inflow_m3), 0) as total_air_baku_m3,
    ROUND(SUM(outflow_m3), 0) as total_air_terolah_m3,
    ROUND(SUM(water_loss_m3), 0) as total_air_hilang_m3,
    ROUND((SUM(water_loss_m3) / SUM(inflow_m3)) * 100, 2) as persentase_loss_keseluruhan
FROM operasional_sunggal;

-- 2. Deteksi Dini Kebocoran Kritis (Plant loss > 5.0% di luar siklus rutin backwash saringan)
SELECT 
    timestamp,
    shift,
    inflow_m3,
    outflow_m3,
    water_loss_m3,
    ROUND(loss_percentage, 2) as loss_pct,
    status_neraca_air
FROM operasional_sunggal
WHERE is_backwash = 0 AND loss_percentage > 5.0
ORDER BY loss_percentage DESC;

-- 3. Audit Overdosing Koagulan (PAC) Berdasarkan Kategori Kekeruhan Sungai Belawan
SELECT 
    turbidity_category,
    COUNT(*) as frekuensi_jam,
    ROUND(AVG(turbidity_ntu), 1) as rata_rata_ntu,
    ROUND(SUM(pac_used_kg), 1) as total_pac_aktual_kg,
    ROUND(SUM(pac_ideal_kg), 1) as total_pac_ideal_kg,
    ROUND(SUM(pac_waste_kg), 1) as total_overdosing_kg,
    ROUND(SUM(waste_cost_idr), 0) as total_biaya_pemborosan_rp
FROM operasional_sunggal
GROUP BY turbidity_category
ORDER BY total_biaya_pemborosan_rp DESC;

-- 4. Audit Deviasi Shift Kerja dengan Total Pemborosan di Atas Rata-rata Shift
SELECT 
    shift,
    ROUND(AVG(pac_used_kg - pac_ideal_kg), 2) as avg_selisih_kg_per_jam,
    ROUND(SUM(waste_cost_idr), 0) as total_pemborosan_rp
FROM operasional_sunggal
WHERE pac_used_kg > pac_ideal_kg
GROUP BY shift
HAVING SUM(waste_cost_idr) > (
    SELECT AVG(total_waste) FROM (
        SELECT SUM(waste_cost_idr) as total_waste 
        FROM operasional_sunggal 
        GROUP BY shift
    ) AS subquery
);
