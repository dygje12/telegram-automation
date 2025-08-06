# Panduan Penggunaan

Panduan lengkap untuk menggunakan aplikasi Telegram Automation setelah instalasi berhasil.

## 🚀 Memulai Aplikasi

### 1. Menjalankan Backend
```bash
cd backend
uvicorn app.main:app --reload
```
Backend akan berjalan di `http://127.0.0.1:8000`

### 2. Menjalankan Frontend
```bash
cd frontend
pnpm run dev
```
Frontend akan berjalan di `http://localhost:5173`

## 🔐 Proses Autentikasi

### Langkah 1: Login
1. Buka aplikasi di browser (`http://localhost:5173`)
2. Masukkan informasi berikut:
   - **API ID**: Dapatkan dari [my.telegram.org](https://my.telegram.org)
   - **API Hash**: Dapatkan dari [my.telegram.org](https://my.telegram.org)
   - **Phone Number**: Nomor telepon yang terdaftar di Telegram

### Langkah 2: Verifikasi Kode
1. Telegram akan mengirim kode verifikasi via SMS atau aplikasi
2. Masukkan kode 5 digit yang diterima
3. Klik "Verify Code"

### Langkah 3: Two-Factor Authentication (Opsional)
1. Jika akun Telegram menggunakan 2FA, masukkan password 2FA
2. Klik "Submit Password"

## 📊 Dashboard Utama

Setelah login berhasil, Anda akan melihat dashboard dengan informasi:

### Statistik Real-time
- **Scheduler Status**: Running/Stopped dengan toggle control
- **Active Messages**: Jumlah template pesan yang aktif
- **Available Groups**: Jumlah grup yang tersedia untuk pengiriman
- **Success Rate**: Persentase keberhasilan pengiriman 24 jam terakhir

### Quick Actions
- Start/Stop Scheduler
- Add New Message
- Add New Group
- View Recent Logs

## 📝 Manajemen Pesan

### Membuat Template Pesan
1. Klik "Messages" di sidebar
2. Klik "Add New Message"
3. Isi form:
   - **Title**: Nama template untuk identifikasi
   - **Content**: Isi pesan (mendukung variabel dinamis)
   - **Status**: Active/Inactive

### Variabel Dinamis
Gunakan variabel berikut dalam konten pesan:
- `{group_name}`: Nama grup target
- `{current_time}`: Waktu saat ini
- `{random_number}`: Angka random 1-1000

Contoh:
```
Halo {group_name}! 
Pesan otomatis pada {current_time}
ID: {random_number}
```

### Mengelola Template
- **Edit**: Klik ikon edit untuk mengubah template
- **Delete**: Klik ikon delete untuk menghapus
- **Toggle Status**: Aktifkan/nonaktifkan template

## 👥 Manajemen Grup

### Menambah Grup Target
1. Klik "Groups" di sidebar
2. Klik "Add New Group"
3. Masukkan salah satu:
   - **Group Username**: @namagrup (tanpa @)
   - **Group ID**: ID numerik grup
   - **Invite Link**: Link undangan grup

### Validasi Grup
Sistem akan otomatis memvalidasi:
- Apakah grup dapat diakses
- Status keanggotaan user
- Izin untuk mengirim pesan
- Deteksi slow mode

### Status Grup
- **✅ Active**: Grup siap menerima pesan
- **⚠️ Slow Mode**: Grup memiliki pembatasan waktu
- **❌ Blacklisted**: Grup di-blacklist sementara
- **🔒 No Access**: Tidak dapat mengakses grup

## 🚫 Sistem Blacklist

### Blacklist Otomatis
Grup akan otomatis masuk blacklist jika:
- Terdeteksi slow mode yang terlalu ketat
- Gagal mengirim pesan berulang kali
- Mendapat error "Too Many Requests"

### Manajemen Blacklist Manual
1. Klik "Blacklist" di sidebar
2. Untuk menambah manual:
   - Pilih grup dari dropdown
   - Pilih tipe blacklist (Temporary/Permanent)
   - Atur durasi (untuk temporary)
   - Tambahkan alasan

### Tipe Blacklist
- **Temporary**: Blacklist dengan durasi tertentu
- **Permanent**: Blacklist permanen hingga dihapus manual

## ⚙️ Pengaturan Scheduler

### Konfigurasi Interval
1. Klik "Settings" di sidebar
2. Atur parameter berikut:
   - **Min Interval**: Jeda minimum antar grup (detik)
   - **Max Interval**: Jeda maksimum antar grup (detik)
   - **Min Delay**: Jeda minimum antar pesan (detik)
   - **Max Delay**: Jeda maksimum antar pesan (detik)

### Rekomendasi Pengaturan
```
Min Interval: 30 detik
Max Interval: 120 detik
Min Delay: 5 detik
Max Delay: 15 detik
```

### Kontrol Scheduler
- **Start**: Mulai pengiriman otomatis
- **Stop**: Hentikan pengiriman
- **Status**: Monitor status real-time

## 📈 Monitoring dan Logs

### Dashboard Metrics
Monitor performa melalui:
- Grafik success rate harian
- Statistik pengiriman per jam
- Breakdown status pesan (success/failed/blacklisted)

### Log Pengiriman
1. Klik "Logs" di sidebar
2. Filter berdasarkan:
   - Tanggal
   - Status (All/Success/Failed/Blacklisted)
   - Grup tertentu

### Export Logs
- Klik "Export" untuk download logs dalam format JSON
- Berguna untuk analisis lebih lanjut

## 🔧 Troubleshooting

### Masalah Umum

#### Scheduler Tidak Berjalan
- Pastikan ada pesan aktif
- Pastikan ada grup yang tidak di-blacklist
- Cek log untuk error details

#### Pesan Tidak Terkirim
- Verifikasi grup masih dapat diakses
- Cek apakah grup di-blacklist
- Pastikan konten pesan valid

#### Login Gagal
- Verifikasi API ID dan API Hash
- Pastikan nomor telepon benar
- Cek koneksi internet

#### Kode Verifikasi Tidak Diterima
- Tunggu beberapa menit
- Restart aplikasi
- Coba login ulang

### Tips Optimasi

#### Menghindari Spam Detection
- Gunakan interval yang cukup panjang
- Variasikan konten pesan
- Jangan kirim ke terlalu banyak grup sekaligus

#### Meningkatkan Success Rate
- Validasi grup secara berkala
- Hapus grup yang tidak aktif
- Monitor blacklist dan bersihkan yang expired

## 🛡️ Best Practices

### Keamanan
- Jangan share API credentials
- Gunakan password 2FA yang kuat
- Logout setelah selesai menggunakan

### Penggunaan Bertanggung Jawab
- Patuhi Terms of Service Telegram
- Jangan spam atau kirim konten tidak pantas
- Hormati privasi dan aturan grup

### Maintenance
- Backup database secara berkala
- Monitor logs untuk error patterns
- Update aplikasi secara teratur

---

Untuk bantuan lebih lanjut, silakan buat issue di repository GitHub atau hubungi tim support.

