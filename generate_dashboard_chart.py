import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axs = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Dashboard Analisis Operasional IPA Sunggal - Perumda Tirtanadi (Simulasi 30 Hari)', fontsize=16, fontweight='bold', y=0.98)

df = pd.read_csv("dataset_ipa_sunggal_simulasi.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

axs[0, 0].plot(df['timestamp'], df['turbidity_ntu'], color='#e67e22', label='Kekeruhan Air Baku (NTU)', alpha=0.7, linewidth=1.2)
axs[0, 0].set_title('1. Fluktuasi Kekeruhan Sungai Belawan (NTU)', fontsize=12, fontweight='bold')
axs[0, 0].set_ylabel('Turbidity (NTU)')
axs[0, 0].axhline(y=150, color='red', linestyle='--', alpha=0.6, label='Batas Siaga (150 NTU)')
axs[0, 0].legend(loc='upper right', frameon=True)
axs[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

axs[0, 1].plot(df['timestamp'], df['pac_used_kg'], color='#e74c3c', label='PAC Aktual di Lapangan (kg/jam)', linewidth=1.2)
axs[0, 1].plot(df['timestamp'], df['pac_ideal_kg'], color='#27ae60', linestyle='--', label='Dosis Ideal Lab (kg/jam)', linewidth=1.2)
axs[0, 1].fill_between(df['timestamp'], df['pac_used_kg'], df['pac_ideal_kg'], where=(df['pac_used_kg'] > df['pac_ideal_kg']),
                       color='#f1948a', alpha=0.5, label='Area Pemborosan (Overdosing)')
axs[0, 1].set_title('2. Optimasi Dosis Koagulan PAC: Aktual vs Standar Jar Test', fontsize=12, fontweight='bold')
axs[0, 1].set_ylabel('Konsumsi PAC (kg/jam)')
axs[0, 1].legend(loc='upper right', frameon=True)
axs[0, 1].xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

colors = {'Normal': '#3498db', 'Normal (Proses Backwash)': '#95a5a6', 
          'WARNING: Kehilangan Air Tinggi': '#f39c12', 'CRITICAL: Indikasi Kebocoran / Overflow': '#c0392b'}
for status, col in colors.items():
    subset = df[df['status_neraca_air'] == status]
    axs[1, 0].scatter(subset['timestamp'], subset['loss_percentage'], label=status, color=col, s=15, alpha=0.8)

axs[1, 0].axhline(y=4.5, color='darkred', linestyle=':', label='Batas Toleransi Normal (4.5%)')
axs[1, 0].set_title('3. Monitoring Neraca Air & Deteksi Kehilangan Air (Plant Loss %)', fontsize=12, fontweight='bold')
axs[1, 0].set_ylabel('Loss (%)')
axs[1, 0].legend(loc='upper right', frameon=True, fontsize=8)
axs[1, 0].xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

shift_waste = df.groupby('shift')['waste_cost_idr'].sum() / 1_000_000
shift_names = shift_waste.index.tolist()
shift_values = shift_waste.values.tolist()

bars = axs[1, 1].bar(shift_names, shift_values, color=['#2980b9', '#e67e22', '#8e44ad'], width=0.5)
axs[1, 1].set_title('4. Estimasi Biaya Pemborosan Koagulan per Shift (Juta Rp / Bulan)', fontsize=12, fontweight='bold')
axs[1, 1].set_ylabel('Total Pemborosan (Juta Rupiah)')
for bar in bars:
    yval = bar.get_height()
    axs[1, 1].text(bar.get_x() + bar.get_width()/2.0, yval + 0.8, f"Rp {yval:.1f} Jt", ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig("dashboard_ipa_sunggal.png", dpi=200)
print("Dashboard visualisasi berhasil diekspor ke dashboard_ipa_sunggal.png")

