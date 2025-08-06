# Backend API Documentation

Dokumentasi ini menjelaskan API endpoints yang tersedia di backend Telegram Automation, serta cara mengakses dokumentasi API interaktif dan dokumentasi kode internal.

## Akses Dokumentasi API Interaktif

Backend Telegram Automation dibangun menggunakan FastAPI, yang secara otomatis menghasilkan dokumentasi API interaktif. Anda dapat mengakses dokumentasi ini melalui:

### Swagger UI
Akses: `http://127.0.0.1:8000/docs`

Swagger UI menyediakan antarmuka interaktif yang memungkinkan Anda untuk:
- Melihat semua endpoint yang tersedia.
- Memahami parameter yang diperlukan untuk setiap endpoint.
- Menguji endpoint secara langsung dari browser Anda.
- Melihat contoh respons (response) dari setiap endpoint.

### Redoc
Akses: `http://127.0.0.1:8000/redoc`

Redoc menyediakan tampilan dokumentasi API yang lebih bersih, terstruktur, dan mudah dibaca, dengan fitur-fitur seperti:
- Tampilan yang ringkas dan navigasi yang intuitif.
- Dokumentasi yang detail untuk setiap endpoint.

## Dokumentasi Kode Backend (Sphinx)

Untuk dokumentasi kode backend yang lebih mendalam, termasuk docstrings, struktur internal modul, layanan, dan utilitas, Anda dapat merujuk pada dokumentasi Sphinx yang dihasilkan dari kode sumber. Dokumentasi ini sangat berguna bagi pengembang yang ingin memahami detail implementasi internal.

Lokasi: `backend/docs/build/html/index.html` (setelah Anda membangun dokumentasi Sphinx).

Dokumentasi Sphinx ini mencakup:
- Dokumentasi untuk semua modul Python.
- Docstrings dari fungsi dan kelas.
- Struktur arsitektur backend.
- Detail implementasi services dan utilities.

## Endpoint Utama

Berikut adalah daftar ringkasan endpoint API utama yang disediakan oleh backend. Untuk detail lengkap mengenai parameter, tipe data, dan contoh respons, silakan gunakan Swagger UI atau Redoc.

### Authentication
- `POST /auth/login`: Melakukan login pengguna dengan kredensial.
- `POST /auth/verify-code`: Memverifikasi kode OTP yang diterima dari Telegram.
- `POST /auth/verify-2fa`: Memverifikasi Two-Factor Authentication (2FA) jika diaktifkan.
- `GET /auth/status`: Mendapatkan status autentikasi pengguna saat ini.

### Messages
- `GET /messages`: Mendapatkan daftar semua template pesan yang tersedia.
- `POST /messages`: Membuat template pesan baru.
- `PUT /messages/{id}`: Memperbarui template pesan berdasarkan ID.
- `DELETE /messages/{id}`: Menghapus template pesan berdasarkan ID.

### Groups
- `GET /groups`: Mendapatkan daftar semua grup target.
- `POST /groups`: Menambahkan grup baru.
- `POST /groups/{id}/validate`: Memvalidasi akses ke grup tertentu berdasarkan ID.

### Scheduler
- `POST /scheduler/start`: Memulai proses pengiriman pesan otomatis.
- `POST /scheduler/stop`: Menghentikan proses pengiriman pesan otomatis.
- `GET /scheduler/status`: Mendapatkan status scheduler saat ini (running/stopped).
- `GET /scheduler/logs`: Mendapatkan log riwayat pengiriman pesan.

### Settings
- `GET /settings`: Mendapatkan pengaturan aplikasi saat ini.
- `PUT /settings`: Memperbarui pengaturan aplikasi.

### Blacklist
- `GET /blacklist`: Mendapatkan daftar grup yang masuk daftar hitam (blacklist).
- `POST /blacklist`: Menambahkan grup ke daftar hitam.
- `DELETE /blacklist/{id}`: Menghapus grup dari daftar hitam berdasarkan ID.



