# Google Cloud Translation API Setup Guide

## Why Service Account Authentication?

The Google Cloud Translation API v3 **does not support API key authentication**. It requires OAuth2 access tokens or service account credentials for security reasons.

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your **Project ID** (you'll need this)

### 2. Enable the Translation API

1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Cloud Translation API"
3. Click on it and press **Enable**

### 3. Create a Service Account

1. Go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Give it a name like "translation-service"
4. Click **Create and Continue**
5. Grant the role: **Cloud Translation API User**
6. Click **Continue** and **Done**

### 4. Generate Service Account Key

1. Click on your newly created service account
2. Go to **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Choose **JSON** format
5. Download the JSON file

### 5. Configure Your Application


1. Place the JSON file in a secure location
2. Add to your `.env` file:
```
GOOGLE_TRANSLATE_API_KEY = "/path/to/your/service-account.json"
GOOGLE_PROJECT_ID = "your-project-id"
```



## Security Best Practices

- **Never commit** service account files to version control
- **Use environment variables** or secure secret management
- **Restrict service account permissions** to only what's needed
- **Rotate keys regularly** for production environments


## Cost Considerations

- Google Cloud Translation API charges per character translated
- Check current pricing at [Google Cloud Pricing](https://cloud.google.com/translate/pricing)
- Consider using caching (built into our TranslationService) to reduce API calls 