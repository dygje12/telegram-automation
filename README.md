# Telegram Automation - Fullstack Application

Aplikasi fullstack untuk otomasi pengiriman pesan Telegram menggunakan user account dengan fitur-fitur canggih seperti smart blacklist, scheduler otomatis, dan monitoring real-time.

## 🚀 Fitur Utama

### Backend (FastAPI + Telethon)
- **Authentication**: Login menggunakan API ID, API Hash, dan nomor telepon
- **Message Management**: Template pesan dengan variabel dinamis
- **Group Management**: Validasi dan manajemen grup target
- **Smart Blacklist**: Sistem blacklist otomatis dengan expiry time
- **Scheduler**: Pengiriman otomatis dengan interval random untuk menghindari spam detection
- **Monitoring**: Logging lengkap dan statistik real-time
- **Security**: Enkripsi data sensitif dan session management

### Frontend (React + Tailwind CSS)
- **Modern UI**: Interface yang clean dan responsive
- **Multi-step Auth**: Login → Code Verification → 2FA (jika diperlukan)
- **Dashboard**: Statistik real-time dan kontrol scheduler
- **Management**: CRUD untuk messages, groups, dan blacklist
- **Settings**: Konfigurasi interval dan parameter pengiriman

## 📋 Persyaratan

### Telegram API Credentials
1. Kunjungi [my.telegram.org](https://my.telegram.org)
2. Login dengan nomor telepon Anda
3. Buka "API development tools"
4. Buat aplikasi baru
5. Salin API ID dan API Hash

### System Requirements
- Python 3.8+
- Node.js 16+
- SQLite (included)

## 🛠️ Instalasi dan Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd telegram-automation
```

### 2. Setup Backend
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env file dengan konfigurasi Anda

# Jalankan aplikasi
python run.py
```

Backend akan berjalan di `http://localhost:8000`

### 3. Setup Frontend
```bash
cd frontend

# Install dependencies
pnpm install

# Jalankan development server
pnpm run dev
```

Frontend akan berjalan di `http://localhost:5173`

## 🔧 Konfigurasi

### Environment Variables (.env)
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
- **Min Interval**: 1 jam 10 menit (4200 detik)
- **Max Interval**: 1 jam 30 menit (5400 detik)
- **Min Delay**: 5 detik
- **Max Delay**: 10 detik
- **Blacklist Duration**: Dinamis (maksimal 60 menit untuk slow mode, 1 jam untuk flood wait, atau permanen tergantung jenis error)
## 📖 Cara Penggunaan

### 1. Login
1. Buka aplikasi di browser
2. Masukkan API ID, API Hash, dan nomor telepon
3. Masukkan kode verifikasi dari Telegram
4. Jika ada 2FA, masukkan password

### 2. Setup Messages
1. Buka tab "Messages"
2. Klik "Add Message"
3. Buat template pesan dengan variabel:
   - `{username}`: Username target
   - `{first_name}`: Nama depan
   - `{group_title}`: Nama grup

### 3. Setup Groups
1. Buka tab "Groups"
2. Tambahkan grup dengan username atau link
3. Sistem akan memvalidasi akses grup

### 4. Start Automation
1. Buka tab "Scheduler"
2. Klik "Start" untuk memulai pengiriman otomatis
3. Monitor progress di Dashboard

## 🔒 Keamanan

### Data Protection
- Semua data sensitif dienkripsi
- Session Telegram disimpan dengan aman
- Token akses memiliki expiry time

### Anti-Spam Measures
- Interval random antar pengiriman
- Deteksi slow mode otomatis
- Blacklist grup yang bermasalah
- Rate limiting pada API

### Privacy
- Tidak menyimpan isi pesan yang dikirim
- Log hanya menyimpan status pengiriman
- Data user terisolasi per akun

## 📊 Monitoring

### Dashboard Metrics
- Status scheduler (running/stopped)
- Jumlah pesan aktif
- Jumlah grup tersedia
- Success rate pengiriman
- Statistik 24 jam terakhir

### Logging
- Setiap pengiriman dicatat dengan timestamp
- Status: success, failed, blacklisted
- Error details untuk debugging
- Export logs dalam format JSON

## 🚨 Troubleshooting

### Common Issues

**1. Login Failed**
- Pastikan API credentials benar
- Cek koneksi internet
- Pastikan nomor telepon format internasional (+62xxx)

**2. Code Not Received**
- Tunggu beberapa detik
- Cek aplikasi Telegram di device lain
- Restart aplikasi jika perlu

**3. Slow Mode Detected**
- Grup akan otomatis masuk blacklist
- Tunggu 24 jam atau hapus manual dari blacklist
- Adjust interval settings untuk lebih konservatif

**4. Messages Not Sending**
- Cek apakah ada pesan aktif
- Pastikan ada grup yang tidak di-blacklist
- Periksa log untuk error details

### Debug Mode
```bash
# Backend debug
DEBUG=True python run.py

# Frontend debug
pnpm run dev
```

## 🔄 API Endpoints

### Authentication
- `POST /auth/login` - Login dengan credentials
- `POST /auth/verify-code` - Verifikasi kode
- `POST /auth/verify-2fa` - Verifikasi 2FA
- `GET /auth/status` - Status autentikasi

### Messages
- `GET /messages` - List semua pesan
- `POST /messages` - Buat pesan baru
- `PUT /messages/{id}` - Update pesan
- `DELETE /messages/{id}` - Hapus pesan

### Groups
- `GET /groups` - List semua grup
- `POST /groups` - Tambah grup
- `POST /groups/{id}/validate` - Validasi grup

### Scheduler
- `POST /scheduler/start` - Start scheduler
- `POST /scheduler/stop` - Stop scheduler
- `GET /scheduler/status` - Status scheduler
- `GET /scheduler/logs` - Logs pengiriman

## 📝 Database Schema

### Tables
- **users**: Data user dan session
- **messages**: Template pesan
- **groups**: Daftar grup target
- **blacklist**: Grup yang di-blacklist
- **logs**: History pengiriman
- **settings**: Konfigurasi user

## 🤝 Contributing

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Buat Pull Request

## 📄 License

MIT License - lihat file LICENSE untuk detail.

## ⚠️ Disclaimer

Aplikasi ini dibuat untuk tujuan edukasi dan otomasi personal. Pengguna bertanggung jawab untuk mematuhi Terms of Service Telegram dan tidak melakukan spam. Penggunaan yang tidak bertanggung jawab dapat menyebabkan akun Telegram dibanned.

## 📞 Support

Jika mengalami masalah atau butuh bantuan:
1. Cek dokumentasi troubleshooting
2. Periksa logs untuk error details
3. Buat issue di repository
4. Hubungi developer

---

**Dibuat dengan ❤️ menggunakan FastAPI, Telethon, React, dan Tailwind CSS**

