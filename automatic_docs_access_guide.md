# Panduan Akses Dokumentasi Otomatis

Dokumentasi otomatis dalam proyek `telegram-automation` dihasilkan oleh berbagai alat dan dapat diakses di lokasi yang berbeda. Penting untuk diingat bahwa untuk mengakses beberapa dokumentasi ini, aplikasi backend atau frontend mungkin perlu berjalan.

Berikut adalah cara Anda dapat melihat dokumentasi otomatis:

## 1. Dokumentasi API Interaktif (Swagger UI & Redoc)

Dokumentasi ini dihasilkan secara otomatis oleh FastAPI dan sangat berguna untuk memahami serta menguji *endpoint* API backend.

*   **Prasyarat**: Pastikan aplikasi backend sedang berjalan. Anda dapat menjalankannya dengan menavigasi ke direktori `telegram-automation/backend/` dan menjalankan `uvicorn app.main:app --reload` (setelah menginstal dependensi Python).

*   **Akses**: Setelah backend berjalan, buka browser Anda dan kunjungi URL berikut:
    *   **Swagger UI**: `http://127.0.0.1:8000/docs`
    *   **Redoc**: `http://127.0.0.1:8000/redoc`

    Di sini Anda akan menemukan daftar lengkap *endpoint* API, detail parameter, contoh respons, dan kemampuan untuk melakukan panggilan API langsung dari antarmuka browser.

## 2. Dokumentasi Kode Backend (Sphinx)

Dokumentasi ini dihasilkan oleh Sphinx dari *docstrings* kode Python backend. Ini memberikan detail mendalam tentang struktur internal, modul, kelas, dan fungsi.

*   **Prasyarat**: Dokumentasi Sphinx perlu di-*build* terlebih dahulu. Anda dapat melakukannya dengan menavigasi ke direktori `telegram-automation/backend/docs/` dan menjalankan perintah *build* Sphinx (misalnya, `make html` jika Anda memiliki `Makefile` yang dikonfigurasi, atau perintah Sphinx langsung).

*   **Akses**: Setelah berhasil di-*build*, dokumentasi akan tersedia dalam format HTML di direktori `telegram-automation/backend/docs/build/html/`. Anda dapat membuka file `index.html` di browser Anda:
    *   **Lokasi File**: `file:///home/ubuntu/telegram-automation/backend/docs/build/html/index.html` (Anda perlu mengganti `/home/ubuntu/` dengan path absolut repositori Anda di sistem lokal).

## 3. Dokumentasi Kode Frontend (JSDoc)

Dokumentasi ini dihasilkan oleh JSDoc dari komentar kode JavaScript/React di frontend. Ini berguna untuk memahami komponen, fungsi, dan struktur kode frontend.

*   **Prasyarat**: Dokumentasi JSDoc perlu di-*build* terlebih dahulu. Anda dapat melakukannya dengan menavigasi ke direktori `telegram-automation/frontend/` dan menjalankan perintah *build* JSDoc (periksa `package.json` di `frontend/` untuk skrip yang relevan, mungkin `npm run docs` atau `pnpm run docs`).

*   **Akses**: Setelah berhasil di-*build*, dokumentasi akan tersedia dalam format HTML di direktori `telegram-automation/frontend/docs/jsdoc/`. Anda dapat membuka file `index.html` di browser Anda:
    *   **Lokasi File**: `file:///home/ubuntu/telegram-automation/frontend/docs/jsdoc/index.html` (Anda perlu mengganti `/home/ubuntu/` dengan path absolut repositori Anda di sistem lokal).

Dengan mengikuti panduan ini, Anda dapat mengakses semua jenis dokumentasi otomatis yang tersedia dalam proyek `telegram-automation`.

