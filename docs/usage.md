# Panduan Penggunaan

Panduan ini akan menjelaskan cara menggunakan aplikasi Telegram Automation untuk mengirim pesan otomatis ke grup-grup Telegram.

## Login ke Aplikasi

1. Buka browser dan akses alamat frontend aplikasi Anda (biasanya `http://localhost:5173` jika dijalankan secara lokal).
2. Masukkan API ID, API Hash, dan nomor telepon Telegram Anda.
3. Masukkan kode verifikasi yang Anda terima dari Telegram.
4. Jika Anda mengaktifkan Two-Factor Authentication (2FA), masukkan password 2FA Anda.
5. Klik tombol "Login" untuk masuk ke dashboard.

## Mengelola Pesan

### Membuat Pesan Baru

1. Navigasi ke halaman "Messages" di dashboard.
2. Klik tombol "Add New Message" atau yang serupa.
3. Masukkan konten pesan yang ingin Anda kirim. Anda dapat menggunakan variabel dinamis jika didukung.
4. Klik "Save" untuk menyimpan pesan.

### Mengedit Pesan

1. Di halaman "Messages", cari pesan yang ingin diubah dan klik tombol "Edit" atau ikon pensil.
2. Ubah konten pesan sesuai kebutuhan Anda.
3. Klik "Save" untuk menyimpan perubahan.

### Menghapus Pesan

1. Di halaman "Messages", cari pesan yang ingin dihapus dan klik tombol "Delete" atau ikon tempat sampah.
2. Konfirmasi penghapusan jika diminta.

## Mengelola Grup

### Menambah Grup Baru

1. Navigasi ke halaman "Groups" di dashboard.
2. Klik tombol "Add New Group" atau yang serupa.
3. Masukkan informasi grup, seperti username grup atau tautan undangan. Sistem akan memvalidasi akses grup secara otomatis.
4. Klik "Save" untuk menyimpan grup.

### Mengedit Grup

1. Di halaman "Groups", cari grup yang ingin diubah dan klik tombol "Edit" atau ikon pensil.
2. Ubah informasi grup sesuai kebutuhan Anda.
3. Klik "Save" untuk menyimpan perubahan.

### Menghapus Grup

1. Di halaman "Groups", cari grup yang ingin dihapus dan klik tombol "Delete" atau ikon tempat sampah.
2. Konfirmasi penghapusan jika diminta.

## Penjadwalan Pesan

### Memulai Otomasi

1. Navigasi ke halaman "Scheduler" di dashboard.
2. Pastikan Anda telah menyiapkan pesan dan grup target.
3. Klik tombol "Start" untuk memulai proses pengiriman pesan otomatis.
4. Anda dapat memantau progress pengiriman di Dashboard.

### Menghentikan Otomasi

1. Di halaman "Scheduler", klik tombol "Stop" untuk menghentikan proses pengiriman pesan otomatis.

## Mengelola Blacklist

### Menambah Grup ke Blacklist

1. Navigasi ke halaman "Blacklist" di dashboard.
2. Klik tombol "Add to Blacklist" atau yang serupa.
3. Pilih grup yang ingin ditambahkan ke blacklist. Grup yang ada di blacklist tidak akan menerima pesan otomatis meskipun termasuk dalam jadwal pengiriman.
4. Klik "Save" untuk menyimpan.

### Menghapus Grup dari Blacklist

1. Di halaman "Blacklist", cari grup yang ingin dihapus dari blacklist dan klik tombol "Delete" atau ikon tempat sampah.
2. Konfirmasi penghapusan jika diminta.

## Tips Penggunaan

- Pastikan untuk menguji pesan Anda terlebih dahulu sebelum menjadwalkan pengiriman massal.
- Gunakan fitur blacklist untuk mengecualikan grup-grup tertentu dari pengiriman otomatis.
- Periksa log aktivitas secara berkala untuk memastikan pesan terkirim dengan baik dan untuk troubleshooting.
- Sesuaikan pengaturan interval pengiriman di bagian "Settings" untuk menghindari deteksi spam oleh Telegram.



