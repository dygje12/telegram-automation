# Panduan Instalasi

Dokumen ini akan memandu Anda melalui proses instalasi dan setup aplikasi Telegram Automation.

## 📋 Prasyarat

Sebelum memulai, pastikan Anda memiliki perangkat lunak berikut terinstal di sistem Anda:

- **Python 3.9+**: Untuk menjalankan backend FastAPI.
- **Node.js 18+**: Untuk menjalankan frontend React.
- **pnpm**: Manajer paket untuk Node.js (direkomendasikan).
- **Git**: Untuk mengkloning repositori.
- **Docker (Opsional)**: Untuk deployment yang lebih mudah.

## 🚀 Langkah-langkah Instalasi

### 1. Kloning Repositori

Buka terminal atau command prompt Anda dan jalankan perintah berikut untuk mengkloning repositori proyek:

```bash
git clone https://github.com/dygje12/telegram-automation.git
cd telegram-automation
```

### 2. Setup Backend

Navigasi ke direktori `backend` dan instal dependensi Python:

```bash
cd backend
pip install -r requirements.txt
```

#### Konfigurasi Environment

Buat file `.env` di direktori `backend` dengan menyalin `example.env` dan mengisi variabel yang diperlukan:

```bash
cp example.env .env
```

Edit file `.env` dan isi nilai-nilai berikut:

- `API_ID`: Dapatkan dari [my.telegram.org](https://my.telegram.org)
- `API_HASH`: Dapatkan dari [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN`: (Opsional) Jika Anda ingin menggunakan bot untuk fitur tertentu.
- `ENCRYPTION_KEY`: Kunci acak 32-byte untuk enkripsi data sensitif. Anda bisa membuatnya dengan:
  ```bash
  python -c "import os; print(os.urandom(32).hex())"
  ```
- `DATABASE_URL`: URL koneksi database SQLite (default: `sqlite:///./sql_app.db`)

#### Migrasi Database

Jalankan migrasi database untuk membuat tabel yang diperlukan:

```bash
alembic upgrade head
```

### 3. Setup Frontend

Navigasi ke direktori `frontend` dan instal dependensi Node.js menggunakan pnpm:

```bash
cd ../frontend
pnpm install
```

#### Konfigurasi Environment

Buat file `.env` di direktori `frontend` dengan menyalin `example.env` dan mengisi variabel yang diperlukan:

```bash
cp example.env .env
```

Edit file `.env` dan isi nilai-nilai berikut:

- `VITE_API_BASE_URL`: URL dasar API backend Anda (default: `http://127.0.0.1:8000`)

## ▶️ Menjalankan Aplikasi

Setelah semua dependensi terinstal dan konfigurasi selesai, Anda dapat menjalankan aplikasi:

### Menjalankan Backend

Dari direktori `backend`:

```bash
uvicorn app.main:app --reload
```

Backend akan berjalan di `http://127.0.0.1:8000`.

### Menjalankan Frontend

Dari direktori `frontend`:

```bash
pnpm run dev
```

Frontend akan berjalan di `http://localhost:5173`.

Sekarang Anda dapat mengakses aplikasi Telegram Automation melalui browser Anda di `http://localhost:5173`.

---

Jika Anda mengalami masalah selama instalasi, silakan merujuk ke bagian [Troubleshooting](usage.md#troubleshooting) atau buat issue di repositori GitHub.

