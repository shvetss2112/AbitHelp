# AbitHelp

## Prerequisites

- Python 3.10 or higher
- PostgreSQL

## Setup Instructions

### 1. Clone the project

```bash
git clone https://github.com/NiksUsername/AbitHelp
cd AbitHelp
```

### 2. Create and edit `.env` file

```bash
cp .env.example .env
```

#### How to get the values:

1. **Email Configuration**:
    - `EMAIL_HOST`: The SMTP server for your email provider (e.g., `smtp.gmail.com` for Gmail).
    - `EMAIL_PORT`: Use `587` for most email providers.
    - `EMAIL_USE_TLS`: Set to `True` for secure email transmission.
    - `EMAIL_HOST_USER`: Your email address.
    - `EMAIL_HOST_PASSWORD`: The password for your email account.

2. **Google OAuth Configuration**:
    - `GOOGLE_CLIENT_ID` and `GOOGLE_SECRET`: 
        - Go to the [Google Cloud Console](https://console.cloud.google.com/).
        - Create a new project or select an existing one.
        - Navigate to **APIs & Services > Credentials**.
        - Click **Create Credentials** and select **OAuth Client ID**.
        - Configure the consent screen and set the redirect URI to your app's callback URL (e.g., `https://<site_url>/accounts/google/login/callback/`).
        - Copy the `Client ID` and `Client Secret` values.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```
