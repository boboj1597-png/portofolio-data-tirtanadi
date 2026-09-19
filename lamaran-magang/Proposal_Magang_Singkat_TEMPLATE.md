# PROPOSAL MAGANG SINGKAT — TEMPLATE 1-2 HALAMAN

> Salin menjadi `Proposal_Magang_Singkat_FINAL.md`, isi semua `[Isi ...]`, ekspor ke PDF untuk kampus & perusahaan.
> Seluruh angka operasional di bawah adalah HASIL SIMULASI SINTETIS portofolio, bukan data resmi Perumda Tirtanadi.

---

## 1. Identitas
- Nama / NIM : Kalek / [Isi NIM]
- Kampus     : Universitas Insan Cita Indonesia (UICI) — Informatika (PJJ), Semester 6
- Periode    : [Isi Periode — contoh: 1 Oktober – 31 Desember 2026]
- Penempatan : Kantor Pusat (TI/Admin Data) dan/atau IPA Sunggal (Admin Operasional & Lab)
- Pembimbing : [Isi Dosen Pembimbing] | Mentor Lapangan: [Isi Jika Sudah Ada]

## 2. Latar Belakang
Operasional IPA membutuhkan rekap harian debit, NTU, pH, sisa klor, dan PAC dari banyak formulir Excel yang belum seragam. Keterlambatan rekap menyulitkan deteksi kebocoran internal dan audit boros kimia. Portofolio saya mensimulasikan solusi atas 3 masalah tersebut memakai SQL + Python.

## 3. Tujuan
1. Mendukung rekonsiliasi neraca air harian dan flag anomali loss >5% di luar jadwal backwash
2. Mendukung audit mingguan efisiensi PAC per kategori NTU dan per shift
3. Membantu automasi rekap logbook Excel → database terpusat agar siap dilaporkan ke Divisi Pengolahan

## 4. Ruang Lingkup (Sesuai Portofolio)
1. `generate_analysis.py` + `analisis_sql_sunggal.sql` — rekap shift, agregasi NTU, deteksi kritis
2. `generate_dashboard_chart.py` — dashboard tren NTU, aktual vs ideal PAC, loss %, biaya per shift
3. Pipeline ETL — cleaning tanggal/teks, imputasi kosong, validasi integritas

## 5. Rencana Kerja Mingguan (Contoh 12 Minggu)
- Minggu 1-2  : Orientasi, SOP, alur logbook IPA Sunggal / alur admin Kantor Pusat
- Minggu 3-4  : Inventarisasi format Excel, desain skema SQLite/MySQL
- Minggu 5-8  : Bangun query rekap + skrip cleaning, uji pada data dummy lalu data riil (sesuai izin)
- Minggu 9-10 : Dashboard mingguan untuk pembimbing lapangan
- Minggu 11-12: Dokumentasi SOP, serah terima kode, laporan akhir

## 6. Output
- Skrip SQL + Python terdokumentasi
- Skema database + SOP rekap
- Dashboard mingguan
- Laporan akhir magang UICI

## 7. Etika Data
Seluruh data simulasi di repo ini adalah sintetis. Selama magang saya bersedia menandatangani pakta kerahasiaan data dan hanya memakai data riil sesuai izin tertulis.
