"""
Pipeline Simulasi & Analisis Data Operasional IPA Sunggal - Perumda Tirtanadi
Rekonsiliasi neraca air, deteksi anomali plant loss, dan audit biaya koagulan (PAC).
"""



import pandas as pd
import numpy as np
import datetime
import sqlite3

np.random.seed(42)

def generate_ipa_sunggal_dataset(days=30):
    date_range = pd.date_range(start="2026-08-01 00:00:00", periods=days * 24, freq="h")
    n = len(date_range)

    shifts = []
    for dt in date_range:
        hour = dt.hour
        if 8 <= hour < 16:
            shifts.append("Shift 1 (Pagi)")
        elif 16 <= hour < 24:
            shifts.append("Shift 2 (Sore)")
        else:
            shifts.append("Shift 3 (Malam)")

    # Kapasitas debit air baku IPA Sunggal (~2.400 L/detik ≈ 8.700 m³/jam)
    base_inflow = 8700 + np.random.normal(0, 150, n)
    
    # Fluktuasi kekeruhan (NTU) Sungai Belawan dengan lonjakan saat hujan di hulu
    base_ntu = np.random.gamma(shape=3.0, scale=20.0, size=n) + 25
    for i, dt in enumerate(date_range):
        if dt.day in [8, 15, 24] and 14 <= dt.hour <= 22:
            base_ntu[i] += np.random.uniform(180, 320)
    
    ph_values = 7.2 + np.random.normal(0, 0.2, n)

    # Siklus rutin pencucian saringan pasir cepat
    is_backwash = [1 if dt.hour in [1, 13] else 0 for dt in date_range]

    # Batas kehilangan air wajar
    normal_loss_pct = np.random.uniform(0.025, 0.038, n)
    outflow = base_inflow * (1 - normal_loss_pct)
    for i in range(n):
        if is_backwash[i] == 1:
            outflow[i] -= 380
            
    # Simulasi anomali kebocoran pipa
    for i, dt in enumerate(date_range):
        if dt.day == 19 and 4 <= dt.hour <= 10:
            outflow[i] -= 650

    # Standar dosis ideal Jar Test laboratorium: ppm = gram PAC/m³ air baku
    ideal_ppm = 12.0 + (0.16 * base_ntu)
    operator_bias = np.random.normal(1.08, 0.08, n)
    actual_ppm = ideal_ppm * operator_bias
    
    for i, dt in enumerate(date_range):
        if 11 <= dt.day <= 13:
            actual_ppm[i] *= 1.32

    # Konversi konsentrasi ppm ke total massa bahan kimia (kg/jam)
    pac_actual_kg = (actual_ppm * base_inflow) / 1000.0
    pac_ideal_kg = (ideal_ppm * base_inflow) / 1000.0

    df = pd.DataFrame({
        'timestamp': date_range,
        'shift': shifts,
        'inflow_m3': np.round(base_inflow, 2),
        'outflow_m3': np.round(outflow, 2),
        'is_backwash': is_backwash,
        'turbidity_ntu': np.round(base_ntu, 1),
        'ph_air_baku': np.round(ph_values, 2),
        'pac_used_kg': np.round(pac_actual_kg, 2),
        'pac_ideal_kg': np.round(pac_ideal_kg, 2)
    })
    return df

df_raw = generate_ipa_sunggal_dataset(days=30)

df_raw['water_loss_m3'] = df_raw['inflow_m3'] - df_raw['outflow_m3']
df_raw['loss_percentage'] = (df_raw['water_loss_m3'] / df_raw['inflow_m3']) * 100

def flag_water_anomaly(row):
    if row['is_backwash'] == 1:
        return 'Normal (Proses Backwash)'
    elif row['loss_percentage'] > 5.0:
        return 'CRITICAL: Indikasi Kebocoran / Overflow'
    elif row['loss_percentage'] > 4.2:
        return 'WARNING: Kehilangan Air Tinggi'
    else:
        return 'Normal'

df_raw['status_neraca_air'] = df_raw.apply(flag_water_anomaly, axis=1)

# Estimasi harga pengadaan bahan kimia koagulan PAC industri per kg
HARGA_PAC_PER_KG = 6500.0

df_raw['pac_waste_kg'] = np.maximum(0, df_raw['pac_used_kg'] - df_raw['pac_ideal_kg'])
df_raw['waste_cost_idr'] = df_raw['pac_waste_kg'] * HARGA_PAC_PER_KG

bins = [0, 50, 150, 300, 1000]
labels = ['Rendah (<50 NTU)', 'Sedang (50-150 NTU)', 'Tinggi (150-300 NTU)', 'Ekstrem (>300 NTU)']
df_raw['turbidity_category'] = pd.cut(df_raw['turbidity_ntu'], bins=bins, labels=labels)

df_raw.to_csv("dataset_ipa_sunggal_simulasi.csv", index=False)

conn = sqlite3.connect("tirtanadi_sunggal.db")
df_raw.to_sql("operasional_sunggal", conn, if_exists="replace", index=False)

query_rekap = """
SELECT 
    shift,
    COUNT(*) as total_jam_operasi,
    ROUND(AVG(inflow_m3), 1) as avg_inflow_m3_jam,
    ROUND(AVG(turbidity_ntu), 1) as avg_turbidity_ntu,
    ROUND(SUM(pac_used_kg), 1) as total_pac_aktual_kg,
    ROUND(SUM(pac_ideal_kg), 1) as total_pac_ideal_kg,
    ROUND(SUM(pac_waste_kg), 1) as total_pemborosan_kg,
    ROUND(SUM(waste_cost_idr), 0) as estimasi_pemborosan_rupiah
FROM operasional_sunggal
GROUP BY shift
ORDER BY estimasi_pemborosan_rupiah DESC;
"""
df_rekap_shift = pd.read_sql_query(query_rekap, conn)
conn.close()

total_inflow = df_raw['inflow_m3'].sum()
total_outflow = df_raw['outflow_m3'].sum()
total_air_hilang = df_raw['water_loss_m3'].sum()
total_loss_pct = (total_air_hilang / total_inflow) * 100
total_waste_pac_cost = df_raw['waste_cost_idr'].sum()
critical_events = df_raw[df_raw['status_neraca_air'] == 'CRITICAL: Indikasi Kebocoran / Overflow']

print("=== RINGKASAN HASIL PIPELINE IPA SUNGGAL ===")
print(f"Total Air Masuk (Inflow)     : {total_inflow:,.0f} m3")
print(f"Total Air Terdistribusi      : {total_outflow:,.0f} m3")
print(f"Total Air Hilang (Loss)      : {total_air_hilang:,.0f} m3 ({total_loss_pct:.2f}%)")
print(f"Insiden Kehilangan Kritis    : {len(critical_events)} jam operasional")
print(f"Estimasi Pemborosan Bahan PAC: Rp {total_waste_pac_cost:,.0f} / bulan")
print("\nRekapitulasi per Shift:")
print(df_rekap_shift.to_string(index=False))
