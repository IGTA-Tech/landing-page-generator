# Landing Page Generator

A production-ready Streamlit app that generates branded landing pages with AI-powered content and design using Claude and DALL-E.

## Features

- **7-Step Conversational Flow**: Intuitive wizard-style interface
- **5 Pre-Configured Brands**: Ready to use with logos, colors, and CTAs
- **4 Marketing Philosophies**: Assessment funnel, traditional, story-driven, social proof
- **5 Design Styles**: Professional, modern, bold, warm, premium
- **AI-Powered Generation**:
  - HTML generation with Claude Sonnet 4
  - Hero image generation with DALL-E 3
- **One-Click Deployment**: Deploy directly to Netlify
- **Airtable Integration**: Save campaigns for tracking
- **Mobile Responsive**: All generated pages are mobile-first
- **Live Preview**: See your landing page before deploying

## Quick Start

### Prerequisites

- Python 3.8+
- API Keys:
  - [Anthropic API Key](https://console.anthropic.com/) (for Claude)
  - [OpenAI API Key](https://platform.openai.com/) (for DALL-E)
  - [Netlify Token](https://app.netlify.com/user/applications) (optional, for deployment)
  - [Airtable API Key](https://airtable.com/account) (optional, for logging)

### Local Installation

1. **Clone or download this repository**

```bash
cd landing-page-generator
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set environment variables**

Create a `.env` file or export environment variables:

```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export NETLIFY_TOKEN="your-netlify-token"  # Optional
export AIRTABLE_API_KEY="your-airtable-key"  # Optional
export AIRTABLE_BASE_ID="your-base-id"  # Optional
```

Or on Windows:
```cmd
set ANTHROPIC_API_KEY=your-anthropic-key
set OPENAI_API_KEY=your-openai-key
```

4. **Run the app**

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
landing-page-generator/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit theme configuration
├── config/
│   ├── brands.json          # 5 brand configurations
│   └── philosophy.json      # Marketing philosophy templates
└── README.md
```

## Configuration

### Brands

Edit `config/brands.json` to customize or add brands. Each brand includes:
- Name and logo URL
- Primary, secondary, and accent colors
- Pre-configured CTAs (top, middle, bottom)

### Philosophies

Edit `config/philosophy.json` to customize marketing approaches:
- **Assessment-Driven Funnel**: Lead gen through quiz (20-40% conversion)
- **Traditional Funnel**: Standard top/middle/bottom (2-10% conversion)
- **Story-Driven**: Narrative approach (5-15% conversion)
- **Social Proof Heavy**: Testimonials-focused (10-25% conversion)

## Deploy to Streamlit Cloud

1. **Push to GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/landing-page-generator.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**

- Go to [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Connect your GitHub repository
- Select `app.py` as the main file
- Add your secrets in the "Advanced settings":

```toml
ANTHROPIC_API_KEY = "your-key"
OPENAI_API_KEY = "your-key"
NETLIFY_TOKEN = "your-token"
AIRTABLE_API_KEY = "your-key"
AIRTABLE_BASE_ID = "your-base"
```

3. **Deploy!**

Your app will be live at `https://your-app-name.streamlit.app`

## Usage Guide

### Step 1: Define Your Intent
Describe what you want to create in natural language.

**Examples:**
- "Landing page for free O-1 visa webinar to capture athlete emails"
- "Conversion page for automation service targeting small businesses"

### Step 2: Select Your Brand
Choose from 5 pre-configured brands with distinct visual identities.

### Step 3: Choose Philosophy
Select your marketing approach:
- Assessment funnel (recommended for lead gen)
- Traditional funnel
- Story-driven
- Social proof heavy

### Step 4: Pick Your Style
Choose a design aesthetic:
- Professional & Corporate
- Modern & Minimal
- Bold & Energetic
- Warm & Trustworthy
- Premium & Luxurious

### Step 5: Configure CTAs
Set your primary call-to-action button text and URL. Optionally add a secondary CTA.

### Step 6: Media Options
Choose whether to generate a hero image with DALL-E 3.

### Step 7: Generate & Deploy
- Preview your landing page
- Download HTML
- Deploy to Netlify
- Save to Airtable

## API Keys Setup

### Anthropic (Claude)
1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new key
5. Copy and save securely

### OpenAI (DALL-E)
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign in or create account
3. Navigate to API Keys
4. Create new secret key
5. Copy and save securely

### Netlify (Optional)
1. Go to [app.netlify.com](https://app.netlify.com/)
2. Sign in
3. Go to User Settings → Applications
4. Create new access token
5. Copy and save securely

### Airtable (Optional)
1. Go to [airtable.com/account](https://airtable.com/account)
2. Generate a personal access token
3. Create a base called "Landing Pages"
4. Add fields: Campaign, Brand, Philosophy, Style, Created, HTML, URL
5. Copy base ID from URL (starts with "app")

## Troubleshooting

### "API key not set" error
Make sure environment variables are set correctly. Restart the Streamlit app after setting them.

### Image generation fails
Check that your OpenAI API key is valid and has credits. Image generation is optional.

### Netlify deployment fails
Verify your Netlify token has proper permissions. Try deploying manually first to test.

### Page not loading in preview
Try refreshing the page or downloading the HTML and opening it locally.

## Customization

### Add New Brands
Edit `config/brands.json` following the existing structure:

```json
{
  "your-brand-id": {
    "name": "Your Brand Name",
    "logo": "https://your-logo-url.com/logo.png",
    "website": "https://yourbrand.com",
    "colors": {
      "primary": "#000000",
      "secondary": "#333333",
      "accent": "#FF0000"
    },
    "ctas": {
      "top": {"text": "CTA Text", "url": "https://url"},
      "middle": {"text": "CTA Text", "url": "https://url"},
      "bottom": {"text": "CTA Text", "url": "https://url"}
    }
  }
}
```

### Modify Styles
Styles are processed by Claude. You can add new styles in Step 4 by editing `app.py` line ~415.

### Change Theme
Edit `.streamlit/config.toml` to change the app's appearance.

## Tech Stack

- **Frontend**: Streamlit
- **AI Models**:
  - Claude Sonnet 4 (HTML generation)
  - DALL-E 3 (Image generation)
- **Deployment**: Netlify, Streamlit Cloud
- **Data Storage**: Airtable

## License

MIT License - feel free to use and modify for your needs.

## Support

For issues or questions:
1. Check this README
2. Review environment variables
3. Check API key validity
4. Verify config files are valid JSON

## Roadmap

- [ ] Video generation with Sora
- [ ] A/B testing variants
- [ ] Custom fonts upload
- [ ] SEO optimization
- [ ] Analytics integration
- [ ] Multi-language support
- [ ] Custom CSS editor
- [ ] Template library

---

Built with ❤️ using Claude Code
