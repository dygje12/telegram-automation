# Backend API Documentation

Dokumentasi ini menjelaskan API endpoints yang tersedia di backend Telegram Automation.

## Akses Dokumentasi API

Backend Telegram Automation menggunakan FastAPI yang secara otomatis menghasilkan dokumentasi API interaktif. Anda dapat mengakses dokumentasi ini melalui:

### Swagger UI
Akses: `http://127.0.0.1:8000/docs`

Swagger UI menyediakan antarmuka interaktif untuk menjelajahi dan menguji API endpoints. Anda dapat:
- Melihat semua endpoint yang tersedia
- Melihat parameter yang diperlukan untuk setiap endpoint
- Menguji endpoint langsung dari browser
- Melihat contoh response

### Redoc
Akses: `http://127.0.0.1:8000/redoc`

Redoc menyediakan dokumentasi API yang lebih bersih dan mudah dibaca dengan:
- Tampilan yang lebih terstruktur
- Navigasi yang mudah
- Dokumentasi yang detail untuk setiap endpoint

## Dokumentasi Kode Backend (Sphinx)

Untuk dokumentasi kode backend yang lebih detail, termasuk docstrings dan struktur internal, Anda dapat mengakses dokumentasi Sphinx yang telah dibuat:

Lokasi: `backend/docs/build/html/index.html`

Dokumentasi Sphinx ini mencakup:
- Dokumentasi untuk semua modul Python
- Docstrings dari fungsi dan kelas
- Struktur arsitektur backend
- Detail implementasi services dan utilities

## Endpoint Utama

Berikut adalah ringkasan endpoint utama yang tersedia:

### Authentication
- `POST /auth/login` - Login pengguna
- `POST /auth/register` - Registrasi pengguna baru

### Messages
- `GET /messages/` - Mendapatkan daftar pesan
- `POST /messages/` - Membuat pesan baru
- `PUT /messages/{id}` - Mengupdate pesan
- `DELETE /messages/{id}` - Menghapus pesan

### Groups
- `GET /groups/` - Mendapatkan daftar grup
- `POST /groups/` - Menambah grup baru
- `PUT /groups/{id}` - Mengupdate grup
- `DELETE /groups/{id}` - Menghapus grup

### Scheduler
- `GET /scheduler/` - Mendapatkan daftar jadwal
- `POST /scheduler/` - Membuat jadwal baru
- `PUT /scheduler/{id}` - Mengupdate jadwal
- `DELETE /scheduler/{id}` - Menghapus jadwal

### Blacklist
- `GET /blacklist/` - Mendapatkan daftar blacklist
- `POST /blacklist/` - Menambah ke blacklist
- `DELETE /blacklist/{id}` - Menghapus dari blacklist

Untuk detail lengkap tentang parameter, response, dan contoh penggunaan, silakan akses dokumentasi Swagger UI atau Redoc yang disebutkan di atas.

