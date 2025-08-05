# Panduan Instalasi

Panduan ini akan memandu Anda melalui proses instalasi dan setup proyek Telegram Automation.

## Persyaratan Sistem

Pastikan sistem Anda memenuhi persyaratan berikut:

*   **Python 3.9+**
*   **Node.js 18+**
*   **npm** atau **yarn**
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

    Buat file `.env` di direktori `backend` dan tambahkan konfigurasi yang diperlukan (contoh):

    ```
    DATABASE_URL="sqlite:///./sql_app.db"
    SECRET_KEY="your-super-secret-key"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

    Jalankan migrasi database:

    ```bash
    alembic upgrade head
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
    npm install
    # atau
    # yarn install
    ```

    Buat file `.env` di direktori `frontend` dan tambahkan konfigurasi yang diperlukan (contoh):

    ```
    REACT_APP_API_URL=http://127.0.0.1:8000
    ```

    Jalankan aplikasi frontend:

    ```bash
    npm start
    # atau
    # yarn start
    ```

    Frontend akan berjalan di `http://localhost:3000` secara default.

Setelah semua langkah ini selesai, aplikasi Telegram Automation seharusnya sudah berjalan dan dapat diakses melalui browser Anda.

