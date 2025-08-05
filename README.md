# Telegram Automation - Fullstack Application

Aplikasi fullstack untuk otomasi pengiriman pesan Telegram menggunakan user account dengan fitur-fitur canggih seperti smart blacklist, scheduler otomatis, dan monitoring real-time.

## 🚀 Fitur Utama

### Backend (FastAPI + Telethon)
- **Authentication**: Login menggunakan API ID, API Hash, dan nomor telepon (dikonfirmasi oleh `auth.py` router)
- **Message Management**: Template pesan dengan variabel dinamis (dikonfirmasi oleh `messages.py` router)
- **Group Management**: Validasi dan manajemen grup target (dikonfirmasi oleh `groups.py` router)
- **Smart Blacklist**: Sistem blacklist otomatis dengan expiry time (dikonfirmasi oleh `blacklist.py` router)
- **Scheduler**: Pengiriman otomatis dengan interval random untuk menghindari spam detection (dikonfirmasi oleh `scheduler.py` router dan `scheduler_service.py`)
- **Monitoring**: Logging lengkap dan statistik real-time (dikonfirmasi oleh `main.py` health check dan info endpoint)
- **Security**: Enkripsi data sensitif dan session management (dikonfirmasi oleh `utils/encryption.py` dan `auth.py`)

### Frontend (React + Tailwind CSS)
- **Modern UI**: Interface yang clean dan responsive (dikonfirmasi oleh `package.json` dependencies seperti `@radix-ui`, `tailwindcss`)
- **Multi-step Auth**: Login → Code Verification → 2FA (jika diperlukan) (dikonfirmasi oleh `auth.py` router)
- **Dashboard**: Statistik real-time dan kontrol scheduler (dikonfirmasi oleh `main.py` info endpoint dan `scheduler.py` router)
- **Management**: CRUD untuk messages, groups, dan blacklist (dikonfirmasi oleh `messages.py`, `groups.py`, `blacklist.py` routers)
- **Settings**: Konfigurasi interval dan parameter pengiriman (dikonfirmasi oleh `settings.py` router)

## 📋 Persyaratan

### Telegram API Credentials
1. Kunjungi [my.telegram.org](https://my.telegram.org)
2. Login dengan nomor telepon Anda
3. Buka "API development tools"
4. Buat aplikasi baru
5. Salin API ID dan API Hash

### System Requirements
- Python 3.8+ (dikonfirmasi oleh `requirements.txt`)
- Node.js 16+ (dikonfirmasi oleh `package.json`)
- SQLite (included) (dikonfirmasi oleh `database.py`)

## 🛠️ Instalasi dan Setup

### 1. Clone Repository
```bash
git clone https://github.com/dygje12/telegram-automation
cd telegram-automation
```

### 2. Setup Backend
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env file dengan konfigurasi Anda (lihat bagian Konfigurasi)

# Jalankan aplikasi
python run.py
```

Backend akan berjalan di `http://localhost:8000` (dikonfirmasi oleh `main.py`)

### 3. Setup Frontend
```bash
cd frontend

# Install dependencies
pnpm install

# Jalankan development server
pnpm run dev
```

Frontend akan berjalan di `http://localhost:5173` (dikonfirmasi oleh `vite.config.js` default)

## 🔧 Konfigurasi

### Environment Variables (.env)
File `.env` harus dibuat di direktori `backend` dengan variabel-variabel berikut:
```env
# Database
DATABASE_URL=sqlite:///./telegram_automation.db

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### Default Settings
Pengaturan default untuk interval dan delay pengiriman, serta durasi blacklist, dapat ditemukan di kode sumber (`settings.py` dan `scheduler_service.py`).
- **Min Interval**: 1 jam 10 menit (4200 detik)
- **Max Interval**: 1 jam 30 menit (5400 detik)
- **Min Delay**: 5 detik
- **Max Delay**: 10 detik
- **Blacklist Duration**: Dinamis (maksimal 60 menit untuk slow mode, 1 jam untuk flood wait, atau permanen tergantung jenis error)

## 📖 Cara Penggunaan

### 1. Login
1. Buka aplikasi di browser (biasanya `http://localhost:5173`)
2. Masukkan API ID, API Hash, dan nomor telepon
3. Masukkan kode verifikasi dari Telegram
4. Jika ada 2FA, masukkan password

### 2. Setup Messages
1. Buka tab "Messages"
2. Klik "Add Message"
3. Buat template pesan sesuai kebutuhan Anda

### 3. Setup Groups
1. Buka tab "Groups"
2. Tambahkan grup dengan username atau link
3. Sistem akan memvalidasi akses grup secara otomatis.

### 4. Start Automation
1. Buka tab "Scheduler"
2. Klik "Start" untuk memulai pengiriman otomatis.
3. Monitor progress di Dashboard.

## 🔒 Keamanan

### Data Protection
- Semua data sensitif dienkripsi menggunakan `ENCRYPTION_KEY`.
- Session Telegram disimpan dengan aman.
- Token akses memiliki expiry time.

### Anti-Spam Measures
- Interval random antar pengiriman untuk menghindari deteksi spam.
- Deteksi slow mode otomatis dan penanganan blacklist.
- Blacklist grup yang bermasalah secara otomatis.
- Rate limiting pada API (implied oleh penggunaan FastAPI).

### Privacy
- Tidak menyimpan isi pesan yang dikirim.
- Log hanya menyimpan status pengiriman.
- Data user terisolasi per akun.

## 📊 Monitoring

### Dashboard Metrics
- Status scheduler (running/stopped)
- Jumlah pesan aktif
- Jumlah grup tersedia
- Success rate pengiriman
- Statistik 24 jam terakhir

### Logging
- Setiap pengiriman dicatat dengan timestamp.
- Status: success, failed, blacklisted.
- Error details untuk debugging.
- Export logs dalam format JSON (fitur yang mungkin perlu dikembangkan lebih lanjut atau dijelaskan jika ada).

## 🚨 Troubleshooting

### Common Issues

**1. Login Failed**
- Pastikan API credentials benar.
- Cek koneksi internet.
- Pastikan nomor telepon dalam format internasional (misalnya, `+62812...`).

**2. Code Not Received**
- Tunggu beberapa detik.
- Cek aplikasi Telegram di perangkat lain.
- Restart aplikasi jika perlu.

**3. Slow Mode Detected**
- Grup akan otomatis masuk blacklist.
- Tunggu 24 jam atau hapus manual dari blacklist.
- Sesuaikan pengaturan interval untuk lebih konservatif.

**4. Messages Not Sending**
- Cek apakah ada pesan aktif.
- Pastikan ada grup yang tidak di-blacklist.
- Periksa log untuk detail error.

### Debug Mode
Untuk mengaktifkan mode debug:
```bash
# Backend debug
DEBUG=True python run.py

# Frontend debug
pnpm run dev
```

## 🔄 API Endpoints

Berikut adalah daftar endpoint API utama yang disediakan oleh backend:

### Authentication
- `POST /auth/login` - Login dengan credentials (API ID, API Hash, nomor telepon)
- `POST /auth/verify-code` - Verifikasi kode OTP yang diterima dari Telegram
- `POST /auth/verify-2fa` - Verifikasi Two-Factor Authentication (2FA) jika diaktifkan
- `GET /auth/status` - Mendapatkan status autentikasi pengguna saat ini

### Messages
- `GET /messages` - Mendapatkan daftar semua template pesan
- `POST /messages` - Membuat template pesan baru
- `PUT /messages/{id}` - Memperbarui template pesan berdasarkan ID
- `DELETE /messages/{id}` - Menghapus template pesan berdasarkan ID

### Groups
- `GET /groups` - Mendapatkan daftar semua grup target
- `POST /groups` - Menambahkan grup baru
- `POST /groups/{id}/validate` - Memvalidasi akses ke grup tertentu berdasarkan ID

### Scheduler
- `POST /scheduler/start` - Memulai proses pengiriman pesan otomatis
- `POST /scheduler/stop` - Menghentikan proses pengiriman pesan otomatis
- `GET /scheduler/status` - Mendapatkan status scheduler saat ini (running/stopped)
- `GET /scheduler/logs` - Mendapatkan log riwayat pengiriman pesan

### Settings
- `GET /settings` - Mendapatkan pengaturan aplikasi saat ini
- `PUT /settings` - Memperbarui pengaturan aplikasi

## 📝 Database Schema

Proyek ini menggunakan SQLite sebagai database default. Berikut adalah tabel-tabel utama yang digunakan:

- **users**: Menyimpan data pengguna dan sesi Telegram.
- **messages**: Menyimpan template pesan yang dibuat pengguna.
- **groups**: Menyimpan daftar grup Telegram yang menjadi target pengiriman.
- **blacklist**: Menyimpan daftar grup yang di-blacklist sementara atau permanen.
- **logs**: Menyimpan riwayat dan status setiap pengiriman pesan.
- **settings**: Menyimpan konfigurasi aplikasi yang dapat diubah oleh pengguna.

## 🤝 Contributing

Kontribusi sangat dihargai! Ikuti langkah-langkah berikut untuk berkontribusi:

1. Fork repository ini.
2. Buat branch fitur baru (`git checkout -b feature/nama-fitur`).
3. Lakukan perubahan Anda dan commit (`git commit -m 'Tambahkan fitur baru'`).
4. Push ke branch Anda (`git push origin feature/nama-fitur`).
5. Buat Pull Request.

## 📄 License

Proyek ini dilisensikan di bawah MIT License. Lihat file `LICENSE` untuk detail lebih lanjut.

## ⚠️ Disclaimer

Aplikasi ini dibuat untuk tujuan edukasi dan otomasi personal. Pengguna bertanggung jawab penuh untuk mematuhi Terms of Service Telegram dan tidak melakukan spam. Penggunaan yang tidak bertanggung jawab dapat menyebabkan akun Telegram diblokir atau dibanned.

## 📞 Support

Jika Anda mengalami masalah atau membutuhkan bantuan, silakan:
1. Cek dokumentasi troubleshooting di atas.
2. Periksa log aplikasi untuk detail error.
3. Buat issue baru di repository GitHub.
4. Hubungi developer (jika ada informasi kontak yang disediakan).

---

**Dibuat dengan ❤️ menggunakan FastAPI, Telethon, React, dan Tailwind CSS**



