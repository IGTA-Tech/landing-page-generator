# Quick Start Guide - Landing Page Generator

## Get Running in 3 Minutes

### Step 1: Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

### Step 2: Set Your API Keys (1 minute)

**Option A - Environment Variables:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
```

**Option B - Create .env file:**
```bash
cp .env.example .env
# Then edit .env with your keys
```

### Step 3: Run the App (30 seconds)

```bash
streamlit run streamlit_app.py
```

The app opens at `http://localhost:8501`

---

## Where to Get API Keys

### Anthropic (Required)
1. Go to: https://console.anthropic.com/
2. Sign in → API Keys → Create Key
3. Copy the key (starts with `sk-ant-`)

### OpenAI (Required for images)
1. Go to: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy the key (starts with `sk-`)

### Netlify (Optional - for deployment)
1. Go to: https://app.netlify.com/user/applications
2. Create new access token
3. Copy the token

### Airtable (Optional - for logging)
1. Go to: https://airtable.com/account
2. Generate personal access token
3. Create a base named "Landing Pages"
4. Copy base ID from URL

---

## First Test

1. Run the app
2. Step 1: Enter "Landing page for visa consultation service"
3. Step 2: Select any brand
4. Step 3: Choose "Assessment-Driven Funnel"
5. Step 4: Pick "Professional & Corporate"
6. Step 5: Keep default CTAs
7. Step 6: Enable image generation
8. Step 7: Generate and preview!

---

## Troubleshooting

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**"API key not set" error:**
```bash
echo $ANTHROPIC_API_KEY  # Should show your key
```

**Need help?**
Check README.md for detailed documentation.

---

Ready to build landing pages!
