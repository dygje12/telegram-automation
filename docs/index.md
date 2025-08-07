# Telegram Automation Documentation

Selamat datang di dokumentasi Telegram Automation! Aplikasi fullstack untuk otomasi pengiriman pesan Telegram menggunakan user account dengan fitur-fitur canggih seperti smart blacklist, scheduler otomatis, dan monitoring real-time.

## 📚 Dokumentasi

*   [Installation](installation.md) - Panduan instalasi dan setup
*   [Usage](usage.md) - Panduan penggunaan aplikasi
*   [Backend API Docs](backend_api_docs.md) - Dokumentasi API backend yang detail
*   [Backend Code Docs (Sphinx)](backend_sphinx_html/) - Dokumentasi kode backend dengan Sphinx

## 🚀 Fitur Utama

### Backend (FastAPI + Telethon)
- **Authentication**: Login menggunakan API ID, API Hash, dan nomor telepon dengan verifikasi OTP dan 2FA
- **Message Management**: Template pesan dengan variabel dinamis untuk personalisasi
- **Group Management**: Validasi dan manajemen grup target dengan deteksi otomatis
- **Smart Blacklist**: Sistem blacklist otomatis dengan expiry time untuk menghindari grup bermasalah
- **Scheduler**: Pengiriman otomatis dengan interval random untuk menghindari spam detection
- **Monitoring**: Logging lengkap dan statistik real-time untuk tracking performa
- **Security**: Enkripsi data sensitif dan session management yang aman

### Frontend (React + Tailwind CSS)
- **Modern UI**: Interface yang clean dan responsive dengan komponen UI modern
- **Multi-step Auth**: Proses login bertahap (Login → Code Verification → 2FA)
- **Dashboard**: Statistik real-time dan kontrol scheduler dengan visualisasi data
- **Management**: CRUD lengkap untuk messages, groups, dan blacklist
- **Settings**: Konfigurasi interval dan parameter pengiriman yang fleksibel

## 📋 Arsitektur Aplikasi

Aplikasi ini terdiri dari dua komponen utama:

1. **Backend (FastAPI)**: API server yang menangani logika bisnis, database, dan integrasi Telegram
2. **Frontend (React)**: Antarmuka pengguna untuk mengelola aplikasi dengan pengalaman yang intuitif

## 🔒 Keamanan dan Privasi

### Data Protection
- Semua data sensitif dienkripsi menggunakan `ENCRYPTION_KEY` yang aman
- Session Telegram disimpan dengan enkripsi dan isolasi per pengguna
- Token akses memiliki expiry time untuk keamanan tambahan

### Anti-Spam Measures
- Interval random antar pengiriman untuk menghindari deteksi spam Telegram
- Deteksi slow mode otomatis dan penanganan blacklist cerdas
- Blacklist grup yang bermasarkan secara otomatis dengan durasi yang dapat dikonfigurasi
- Rate limiting pada API untuk mencegah abuse

### Privacy
- Tidak menyimpan isi pesan yang dikirim untuk menjaga privasi
- Log hanya menyimpan status pengiriman dan metadata
- Data user terisolasi per akun dengan enkripsi end-to-end

## 📊 Monitoring dan Troubleshooting

### Dashboard Metrics
- Status scheduler (running/stopped) dengan indikator real-time
- Jumlah pesan aktif dan template yang tersedia
- Jumlah grup tersedia dan status validasi
- Success rate pengiriman dengan grafik performa
- Statistik 24 jam terakhir dengan breakdown detail

### Logging dan Debugging
- Setiap pengiriman dicatat dengan timestamp dan detail lengkap
- Status kategorisasi: success, failed, blacklisted, pending
- Error details untuk debugging dan troubleshooting
- Export logs dalam format JSON untuk analisis lebih lanjut

### Common Issues dan Solusi
- **Login Failed**: Verifikasi API credentials dan koneksi internet
- **Code Not Received**: Tunggu beberapa detik atau restart aplikasi
- **Slow Mode Detected**: Grup otomatis masuk blacklist, sesuaikan interval
- **Messages Not Sending**: Periksa pesan aktif dan grup yang tidak di-blacklist

## 📝 Database Schema

Proyek ini menggunakan SQLite sebagai database default dengan skema yang teroptimasi:

- **users**: Data pengguna dan sesi Telegram dengan enkripsi
- **messages**: Template pesan dengan variabel dinamis
- **groups**: Daftar grup Telegram target dengan metadata
- **blacklist**: Grup yang di-blacklist dengan expiry time
- **logs**: Riwayat pengiriman dengan status dan timestamp
- **settings**: Konfigurasi aplikasi yang dapat diubah pengguna

## 🤝 Contributing

Kontribusi sangat dihargai! Untuk berkontribusi:

1. Fork repository ini
2. Buat branch fitur baru (`git checkout -b feature/nama-fitur`)
3. Lakukan perubahan dan commit (`git commit -m "Tambahkan fitur baru"`)
4. Push ke branch (`git push origin feature/nama-fitur`)
5. Buat Pull Request dengan deskripsi yang jelas

## 📄 License

Proyek ini dilisensikan di bawah MIT License. Lihat file `LICENSE` untuk detail lebih lanjut.

## ⚠️ Disclaimer

Aplikasi ini dibuat untuk tujuan edukasi dan otomasi personal. Pengguna bertanggung jawab penuh untuk:
- Mematuhi Terms of Service Telegram
- Tidak melakukan spam atau aktivitas yang melanggar aturan
- Menggunakan aplikasi secara bertanggung jawab

Penggunaan yang tidak bertanggung jawab dapat menyebabkan akun Telegram diblokir atau dibanned.

## 📞 Support

Jika Anda mengalami masalah atau membutuhkan bantuan:

1. Cek dokumentasi troubleshooting di atas
2. Periksa log aplikasi untuk detail error
3. Buat issue baru di repository GitHub dengan detail lengkap
4. Sertakan log error dan langkah reproduksi

---

**Dibuat dengan ❤️ menggunakan FastAPI, Telethon, React, dan Tailwind CSS**

