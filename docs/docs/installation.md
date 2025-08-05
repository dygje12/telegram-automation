# Panduan Instalasi

Panduan ini akan memandu Anda melalui proses instalasi dan setup proyek Telegram Automation.

## Persyaratan Sistem

Pastikan sistem Anda memenuhi persyaratan berikut:

*   **Python 3.9+**
*   **Node.js 18+**
*   **pnpm** (direkomendasikan) atau **npm** atau **yarn**
*   **Git**

## Langkah-langkah Instalasi

1.  **Clone Repositori**

    Buka terminal atau command prompt Anda dan jalankan perintah berikut untuk mengkloning repositori proyek:

    ```bash
    git clone https://github.com/dygje12/telegram-automation.git
    cd telegram-automation
    ```

2.  **Setup Backend (FastAPI)**

    Navigasi ke direktori backend dan instal dependensi Python:

    ```bash
    cd backend
    pip install -r requirements.txt
    ```

    Buat file `.env` di direktori `backend` dan tambahkan konfigurasi yang diperlukan (lihat `backend/.env.example` untuk contoh):

    ```dotenv
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

    Jalankan migrasi database (jika ada):

    ```bash
    # Jika menggunakan Alembic untuk migrasi database
    # alembic upgrade head
    ```

    Jalankan aplikasi backend:

    ```bash
    uvicorn app.main:app --reload
    ```

    Backend akan berjalan di `http://127.0.0.1:8000` secara default.

3.  **Setup Frontend (React)**

    Buka terminal baru, navigasi ke direktori frontend dan instal dependensi Node.js:

    ```bash
    cd ../frontend
    pnpm install
    # atau
    # npm install
    # atau
    # yarn install
    ```

    Buat file `.env` di direktori `frontend` dan tambahkan konfigurasi yang diperlukan (lihat `frontend/.env.example` jika ada):

    ```dotenv
    VITE_API_BASE_URL=http://127.0.0.1:8000
    ```

    Jalankan aplikasi frontend:

    ```bash
    pnpm run dev
    # atau
    # npm run dev
    # atau
    # yarn dev
    ```

    Frontend akan berjalan di `http://localhost:5173` secara default (sesuai `vite.config.js`).

Setelah semua langkah ini selesai, aplikasi Telegram Automation seharusnya sudah berjalan dan dapat diakses melalui browser Anda.


