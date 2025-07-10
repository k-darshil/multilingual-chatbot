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

Choose one of these methods:

#### Method 1: JSON Content in secrets.toml (Recommended for Streamlit)

1. Open the downloaded JSON file
2. Copy the entire JSON content
3. Add to your `.streamlit/secrets.toml`:

```toml
[secrets]
GOOGLE_TRANSLATE_API_KEY = '{"type": "service_account", "project_id": "your-project-id", "private_key_id": "...", "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n", "client_email": "...", "client_id": "...", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token"}'
GOOGLE_PROJECT_ID = "your-project-id"
```

#### Method 2: JSON File Path

1. Place the JSON file in a secure location
2. Add to your `.streamlit/secrets.toml`:

```toml
[secrets]
GOOGLE_TRANSLATE_API_KEY = "/path/to/your/service-account.json"
GOOGLE_PROJECT_ID = "your-project-id"
```

#### Method 3: Application Default Credentials

1. Install Google Cloud CLI: `pip install google-cloud-cli`
2. Run: `gcloud auth application-default login`
3. Add to your `.streamlit/secrets.toml`:

```toml
[secrets]
GOOGLE_PROJECT_ID = "your-project-id"
```

## Security Best Practices

- **Never commit** service account files to version control
- **Use environment variables** or secure secret management
- **Restrict service account permissions** to only what's needed
- **Rotate keys regularly** for production environments

## Testing Your Setup

Run the example script to verify everything works:

```bash
python example_translation_usage.py
```

## Common Issues

### Error: "API keys are not supported by this API"
- **Solution**: Use service account authentication instead of API keys

### Error: "The caller does not have permission"
- **Solution**: Ensure your service account has the "Cloud Translation API User" role

### Error: "Project not found"
- **Solution**: Double-check your GOOGLE_PROJECT_ID matches your actual project ID

### Error: "Invalid JSON"
- **Solution**: Ensure JSON is properly escaped in TOML format (use single quotes)

## Cost Considerations

- Google Cloud Translation API charges per character translated
- Check current pricing at [Google Cloud Pricing](https://cloud.google.com/translate/pricing)
- Consider using caching (built into our TranslationService) to reduce API calls 