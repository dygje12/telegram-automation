# Dokumentasi API Backend

Dokumentasi ini menjelaskan endpoint API yang disediakan oleh backend FastAPI. API ini berfungsi sebagai jembatan antara antarmuka pengguna (frontend) dan logika bisnis inti, termasuk interaksi dengan Telegram melalui Telethon.

## 🌐 Base URL

`http://127.0.0.1:8000` (atau sesuai konfigurasi `HOST` dan `PORT` di `.env`)

## 🔑 Autentikasi

Semua endpoint yang memerlukan autentikasi menggunakan **Bearer Token** (JWT). Token ini diperoleh setelah proses login berhasil dan harus disertakan dalam header `Authorization` untuk setiap permintaan yang dilindungi.

Contoh Header:
`Authorization: Bearer <your_jwt_token>`

## 🚦 Health Check

### `GET /health`

Memeriksa status kesehatan aplikasi backend, termasuk koneksi database dan status scheduler.

**Responses:**
- `200 OK`: Aplikasi berjalan normal.
  ```json
  {
    "status": "ok",
    "database_connection": "ok",
    "scheduler_status": "running"
  }
  ```
- `500 Internal Server Error`: Jika ada masalah dengan database atau scheduler.

## 🔐 Autentikasi Pengguna

### `POST /auth/login`

Memulai proses login pengguna Telegram.

**Request Body:**
```json
{
  "api_id": "<your_api_id>",
  "api_hash": "<your_api_hash>",
  "phone_number": "<your_phone_number>"
}
```

**Responses:**
- `200 OK`: Kode verifikasi telah dikirim.
  ```json
  {
    "message": "Code sent to your Telegram app/SMS."
  }
  ```
- `400 Bad Request`: Invalid input atau nomor telepon tidak valid.
- `500 Internal Server Error`: Masalah dengan koneksi Telegram.

### `POST /auth/verify-code`

Memverifikasi kode yang diterima dari Telegram.

**Request Body:**
```json
{
  "phone_number": "<your_phone_number>",
  "code": "<verification_code>"
}
```

**Responses:**
- `200 OK`: Kode berhasil diverifikasi. Mengembalikan token JWT jika tidak ada 2FA, atau meminta 2FA.
  ```json
  {
    "access_token": "<jwt_token>",
    "token_type": "bearer",
    "message": "Login successful" (if no 2FA)
  }
  ```
  ```json
  {
    "message": "Two-factor authentication required."
  }
  ```
- `400 Bad Request`: Kode tidak valid.
- `401 Unauthorized`: Kode salah atau kadaluarsa.

### `POST /auth/verify-2fa`

Memverifikasi password Two-Factor Authentication.

**Request Body:**
```json
{
  "phone_number": "<your_phone_number>",
  "password": "<2fa_password>"
}
```

**Responses:**
- `200 OK`: 2FA berhasil diverifikasi. Mengembalikan token JWT.
  ```json
  {
    "access_token": "<jwt_token>",
    "token_type": "bearer",
    "message": "Login successful"
  }
  ```
- `401 Unauthorized`: Password 2FA salah.

### `POST /auth/logout`

Mengakhiri sesi pengguna.

**Responses:**
- `200 OK`: Logout berhasil.

## ✉️ Manajemen Pesan

### `GET /messages`

Mengambil daftar semua template pesan.

**Responses:**
- `200 OK`: Daftar pesan.
  ```json
  [
    {
      "id": 1,
      "title": "Pesan Selamat Datang",
      "content": "Halo {group_name}!",
      "status": "active",
      "created_at": "2025-01-01T10:00:00",
      "updated_at": "2025-01-01T10:00:00"
    }
  ]
  ```

### `POST /messages`

Membuat template pesan baru.

**Request Body:**
```json
{
  "title": "Pesan Promosi",
  "content": "Diskon {random_number}% untuk {group_name}!",
  "status": "active"
}
```

**Responses:**
- `201 Created`: Pesan berhasil dibuat.

### `GET /messages/{message_id}`

Mengambil detail template pesan berdasarkan ID.

**Responses:**
- `200 OK`: Detail pesan.
- `404 Not Found`: Pesan tidak ditemukan.

### `PUT /messages/{message_id}`

Memperbarui template pesan berdasarkan ID.

**Request Body:**
```json
{
  "title": "Pesan Promosi Terbaru",
  "content": "Diskon {random_number}% untuk {group_name}! Buruan!",
  "status": "active"
}
```

**Responses:**
- `200 OK`: Pesan berhasil diperbarui.
- `404 Not Found`: Pesan tidak ditemukan.

### `DELETE /messages/{message_id}`

Menghapus template pesan berdasarkan ID.

**Responses:**
- `204 No Content`: Pesan berhasil dihapus.
- `404 Not Found`: Pesan tidak ditemukan.

## 👥 Manajemen Grup

### `GET /groups`

Mengambil daftar semua grup target.

**Responses:**
- `200 OK`: Daftar grup.

### `POST /groups`

Menambahkan grup baru dan memvalidasinya.

**Request Body:**
```json
{
  "group_identifier": "@my_telegram_group" (bisa username, ID, atau invite link)
}
```

**Responses:**
- `201 Created`: Grup berhasil ditambahkan dan divalidasi.
- `400 Bad Request`: Identifier tidak valid atau grup tidak dapat diakses.

### `GET /groups/{group_id}`

Mengambil detail grup berdasarkan ID.

**Responses:**
- `200 OK`: Detail grup.
- `404 Not Found`: Grup tidak ditemukan.

### `PUT /groups/{group_id}`

Memperbarui informasi grup.

**Responses:**
- `200 OK`: Grup berhasil diperbarui.
- `404 Not Found`: Grup tidak ditemukan.

### `DELETE /groups/{group_id}`

Menghapus grup.

**Responses:**
- `204 No Content`: Grup berhasil dihapus.
- `404 Not Found`: Grup tidak ditemukan.

## 🚫 Manajemen Blacklist

### `GET /blacklist`

Mengambil daftar semua entri blacklist.

**Responses:**
- `200 OK`: Daftar blacklist.

### `POST /blacklist`

Menambahkan grup ke blacklist secara manual.

**Request Body:**
```json
{
  "group_id": "<telegram_group_id>",
  "blacklist_type": "temporary",
  "reason": "Spamming",
  "expires_at": "2025-08-01T12:00:00Z" (opsional untuk temporary)
}
```

**Responses:**
- `201 Created`: Entri blacklist berhasil dibuat.

### `DELETE /blacklist/{blacklist_id}`

Menghapus entri blacklist.

**Responses:**
- `204 No Content`: Entri blacklist berhasil dihapus.
- `404 Not Found`: Entri blacklist tidak ditemukan.

## ⚙️ Pengaturan Aplikasi

### `GET /settings`

Mengambil pengaturan aplikasi pengguna.

**Responses:**
- `200 OK`: Pengaturan aplikasi.

### `PUT /settings`

Memperbarui pengaturan aplikasi pengguna.

**Request Body:**
```json
{
  "min_interval": 30,
  "max_interval": 120,
  "min_delay": 5,
  "max_delay": 15
}
```

**Responses:**
- `200 OK`: Pengaturan berhasil diperbarui.

## 📈 Logs

### `GET /logs`

Mengambil riwayat pengiriman pesan.

**Query Parameters:**
- `start_date`: Filter log dari tanggal ini (YYYY-MM-DD)
- `end_date`: Filter log hingga tanggal ini (YYYY-MM-DD)
- `status`: Filter berdasarkan status (success, failed, blacklisted)
- `group_id`: Filter berdasarkan ID grup

**Responses:**
- `200 OK`: Daftar log pengiriman.

### `GET /logs/export`

Mengekspor log pengiriman dalam format JSON.

**Responses:**
- `200 OK`: File JSON berisi log.

## 📊 Dashboard Metrics

### `GET /dashboard/metrics`

Mengambil metrik dashboard real-time.

**Responses:**
- `200 OK`: Metrik dashboard.
  ```json
  {
    "scheduler_status": "running",
    "active_messages_count": 10,
    "available_groups_count": 50,
    "success_rate_24h": 95.5,
    "messages_sent_24h": 1000
  }
  ```

## 🔄 Scheduler Control

### `POST /scheduler/start`

Memulai scheduler pengiriman pesan.

**Responses:**
- `200 OK`: Scheduler berhasil dimulai.

### `POST /scheduler/stop`

Menghentikan scheduler pengiriman pesan.

**Responses:**
- `200 OK`: Scheduler berhasil dihentikan.



