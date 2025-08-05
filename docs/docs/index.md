# Telegram Automation Documentation

Selamat datang di dokumentasi Telegram Automation! Aplikasi ini memungkinkan Anda untuk mengirim pesan otomatis ke grup-grup Telegram dengan penjadwalan yang fleksibel.

## Fitur Utama

- **Manajemen Pesan**: Buat dan kelola template pesan yang akan dikirim
- **Manajemen Grup**: Kelola daftar grup Telegram target
- **Penjadwalan**: Atur jadwal pengiriman pesan secara otomatis
- **Blacklist**: Kelola daftar grup yang dikecualikan dari pengiriman
- **Autentikasi**: Sistem login yang aman untuk mengakses aplikasi

## Arsitektur Aplikasi

Aplikasi ini terdiri dari dua komponen utama:

1. **Backend (FastAPI)**: API server yang menangani logika bisnis dan database
2. **Frontend (React)**: Antarmuka pengguna untuk mengelola aplikasi

## Dokumentasi

- [Installation](installation.md) - Panduan instalasi dan setup
- [Usage](usage.md) - Panduan penggunaan aplikasi
- [Backend API Docs](backend_api_docs.md) - Dokumentasi API backend yang detail


## Keamanan

Aplikasi ini dirancang dengan mempertimbangkan keamanan data dan langkah-langkah anti-spam. Informasi lebih lanjut mengenai fitur keamanan dan privasi dapat ditemukan di sini.

## Monitoring

Pantau status scheduler, metrik dashboard, dan log pengiriman pesan. Detail mengenai monitoring dan troubleshooting dapat ditemukan di sini.

## Skema Database

Proyek ini menggunakan SQLite sebagai database default. Detail mengenai skema database dapat ditemukan di sini.

## Troubleshooting

Jika Anda mengalami masalah atau membutuhkan bantuan, silakan lihat di sini atau buat issue baru di repositori GitHub.






Aplikasi ini dirancang dengan mempertimbangkan keamanan data dan langkah-langkah anti-spam. Fitur keamanan utama meliputi enkripsi `api_id`, `api_hash`, dan `phone_number` pengguna. Untuk meningkatkan keamanan, disarankan untuk mengimplementasikan:

*   **Rate Limiting**: Menerapkan pembatasan laju pada endpoint API untuk mencegah penyalahgunaan dan serangan brute-force.
*   **Validasi Input**: Memastikan validasi input yang ketat pada semua endpoint API untuk mencegah serangan injeksi (misalnya, SQL injection, XSS).
*   **Two-Factor Authentication (2FA)**: Jika aplikasi ini akan digunakan oleh banyak pengguna, pertimbangkan untuk menambahkan 2FA untuk lapisan keamanan tambahan pada proses login.

Pengguna bertanggung jawab penuh untuk mematuhi Ketentuan Layanan Telegram dan tidak melakukan spam. Penggunaan yang tidak bertanggung jawab dapat menyebabkan akun Telegram diblokir atau dibanned.




Pantau status scheduler, metrik dashboard, dan log pengiriman pesan. Untuk monitoring yang efektif, disarankan untuk:

*   **Dashboard Visualisasi**: Mengembangkan dashboard yang komprehensif di frontend untuk memvisualisasikan status pengiriman pesan, aktivitas scheduler, dan statistik blacklist. Ini dapat mencakup grafik dan tabel yang menunjukkan tren dan anomali.
*   **Log Real-time**: Mengimplementasikan pembaruan log secara real-time (misalnya, menggunakan WebSockets atau Server-Sent Events) untuk memantau kemajuan pengiriman pesan dan mengidentifikasi masalah dengan cepat.
*   **Peringatan Otomatis**: Menyiapkan sistem peringatan untuk notifikasi otomatis jika ada kegagalan pengiriman pesan atau masalah scheduler.

Untuk troubleshooting, log aplikasi dan status kesehatan API (`/health` endpoint) dapat memberikan informasi penting.




Proyek ini menggunakan SQLite sebagai database default. Skema database didefinisikan dalam `backend/app/models.py` dan mencakup tabel-tabel berikut:

*   **users**: Menyimpan informasi pengguna, termasuk `api_id`, `api_hash`, `phone_number`, dan `session_data` (semuanya dienkripsi).
*   **messages**: Menyimpan template pesan yang akan dikirim, termasuk `title` dan `content`.
*   **groups**: Menyimpan daftar grup Telegram target, termasuk `group_id`, `group_name`, `username`, dan `invite_link`.
*   **blacklist**: Menyimpan daftar grup yang dikecualikan dari pengiriman pesan, dengan `group_id`, `blacklist_type`, `reason`, dan `expires_at`.
*   **logs**: Mencatat riwayat pengiriman pesan, termasuk `group_id`, `message_id`, `status` (success/failed/blacklisted), dan `error_message`.
*   **settings**: Menyimpan pengaturan aplikasi per pengguna, seperti `min_interval`, `max_interval`, `min_delay`, dan `max_delay` untuk pengiriman pesan.

Semua tabel memiliki kolom `created_at` dan `updated_at` untuk melacak waktu pembuatan dan pembaruan data.




Jika Anda mengalami masalah atau membutuhkan bantuan, silakan:

*   **Periksa Log Aplikasi**: Log aplikasi (yang dapat diakses melalui konsol backend) akan memberikan informasi detail tentang kesalahan atau peringatan yang terjadi.
*   **Gunakan Endpoint Kesehatan API**: Akses endpoint `/health` (misalnya, `http://127.0.0.1:8000/health`) untuk memeriksa status koneksi database dan scheduler.
*   **Buat Issue Baru**: Jika masalah berlanjut, buat issue baru di repositori GitHub proyek dengan menyertakan detail masalah, langkah-langkah untuk mereproduksi, dan log yang relevan.

