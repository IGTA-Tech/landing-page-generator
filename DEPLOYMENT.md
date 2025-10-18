# Deployment Guide

## Important: Platform Choice

This **Streamlit application** should be deployed to **Streamlit Cloud** (not Netlify).

The app itself *generates* landing pages that can then be deployed to Netlify using the built-in "Deploy to Netlify" feature.

---

## Option 1: Deploy to Streamlit Cloud (Recommended)

### Step 1: Go to Streamlit Cloud
Visit: https://share.streamlit.io

### Step 2: Sign in with GitHub
Use the same GitHub account that has the repository.

### Step 3: Create New App
1. Click "New app"
2. Select repository: `IGTA-Tech/landing-page-generator`
3. Branch: `main`
4. Main file path: `app.py`
5. Click "Advanced settings"

### Step 4: Add Secrets
In the "Secrets" section, add:

```toml
ANTHROPIC_API_KEY = "your-anthropic-key-here"
OPENAI_API_KEY = "your-openai-key-here"

# Optional - for Netlify deployment feature
NETLIFY_TOKEN = "your-netlify-token-here"

# Optional - for Airtable logging
AIRTABLE_API_KEY = "your-airtable-key-here"
AIRTABLE_BASE_ID = "your-base-id-here"
```

### Step 5: Deploy
Click "Deploy!"

Your app will be live at: `https://your-app-name.streamlit.app`

---

## Option 2: Deploy to Other Platforms

### Render.com
1. Create new "Web Service"
2. Connect GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Add environment variables

### Railway.app
1. Create new project from GitHub
2. Add environment variables
3. No build configuration needed
4. Railway auto-detects Streamlit

### Hugging Face Spaces
1. Create new Space (Streamlit)
2. Upload files or connect GitHub
3. Add secrets in Settings
4. Auto-deploys

---

## Using the Netlify Feature

Once your Streamlit app is deployed, users can:

1. Generate a landing page in the app
2. Click "Deploy to Netlify" in Step 7
3. Enter a subdomain name
4. Landing page deploys to `https://subdomain.netlify.app`

**Note:** Users need to set the `NETLIFY_TOKEN` environment variable in your Streamlit Cloud secrets for this feature to work.

---

## Getting a Netlify Token

For the "Deploy to Netlify" feature to work:

1. Go to https://app.netlify.com/user/applications
2. Click "New access token"
3. Give it a name (e.g., "Landing Page Generator")
4. Click "Generate token"
5. Copy the token
6. Add to Streamlit Cloud secrets as `NETLIFY_TOKEN`

---

## Monitoring Your App

### Streamlit Cloud Dashboard
- View logs
- Check resource usage
- Manage secrets
- Restart app

### GitHub Integration
- Every push to `main` branch auto-deploys
- Pull requests can be previewed
- Rollback to previous commits

---

## Troubleshooting

### App won't start
- Check logs in Streamlit Cloud dashboard
- Verify all required secrets are set
- Ensure requirements.txt is up to date

### API errors
- Verify API keys are correct
- Check API key has sufficient credits
- Test keys locally first

### Deployment feature not working
- Verify NETLIFY_TOKEN is set
- Check Netlify token has proper permissions
- Test token at https://api.netlify.com/api/v1/user

---

## Cost Considerations

### Streamlit Cloud
- **Free tier**: 1 app, unlimited viewers
- **Plus**: $20/month for 3 apps
- **Pro**: Custom pricing

### API Usage
- **Claude API**: Pay per token
- **OpenAI DALL-E 3**: ~$0.04 per image
- **Netlify**: Free tier covers most use cases

---

Your app is ready to deploy!
