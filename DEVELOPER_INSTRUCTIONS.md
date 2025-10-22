# Developer Implementation Instructions

## 📋 Project Overview

This is a **Streamlit-based Landing Page Generator** that creates high-converting landing pages for 5 brands using Claude AI (Anthropic) and DALL-E (OpenAI). The system includes:

- 🎨 AI-generated HTML landing pages with inline CSS/JavaScript
- 🖼️ AI-generated hero images via DALL-E 3
- 📊 A/B testing (automatic variation generation)
- 🔗 Integrations: **n8n** (email automation), **GoHighLevel** (CRM), **Microsoft Clarity** (heatmaps)
- 📈 Analytics tracking via Airtable
- 🚀 One-click deployment to Netlify

**Current Status:** ✅ All code complete, integrations configured, real content added

---

## 🔑 Step 1: Verify API Keys in Streamlit Secrets

The following API keys should already be configured in **Streamlit Cloud Secrets** (per user's confirmation):

### Required API Keys:

```toml
# Streamlit Cloud Secrets (Settings > Secrets)
ANTHROPIC_API_KEY = "sk-ant-..."
OPENAI_API_KEY = "sk-..."
AIRTABLE_API_KEY = "key..."
NETLIFY_ACCESS_TOKEN = "nfp_..."
```

### How to Verify:

1. Go to https://share.streamlit.io
2. Navigate to your app: **landing-page-generator**
3. Click **Settings** → **Secrets**
4. Confirm all 4 keys are present
5. If any are missing, add them in the format above

### Where to Get Keys (if needed):

- **Anthropic API Key:** https://console.anthropic.com/settings/keys
- **OpenAI API Key:** https://platform.openai.com/api-keys
- **Airtable API Key:** https://airtable.com/create/tokens
- **Netlify Access Token:** https://app.netlify.com/user/applications/personal

---

## 🔗 Step 2: Configure Integration Webhooks (Per-Campaign Basis)

The following integrations are **configured in the code** but require **webhook URLs to be entered manually** when generating each landing page. This is by design - different campaigns may use different webhooks.

### A. n8n Email Automation Webhook

**What it does:** Sends lead data (quiz results, form submissions) to n8n for email automation

**Setup Instructions:**

1. **Create n8n Workflow:**
   - Log into your n8n instance (cloud or self-hosted)
   - Create a new workflow
   - Add a **Webhook** node as the trigger
   - Set method to `POST`
   - Copy the webhook URL (e.g., `https://your-n8n-instance.app.n8n.cloud/webhook/abc123`)

2. **Configure n8n Workflow to Receive:**
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com",
     "phone": "555-1234",
     "quiz_score": 14,
     "quiz_result": "strong",
     "lead_source": "Landing Page - Sherrod Sports Visas",
     "timestamp": "2025-10-22T12:00:00Z"
   }
   ```

3. **Add Email Node in n8n:**
   - After webhook, add **Send Email** node
   - Configure to send quiz results to the lead's email
   - Add notification email to admin (e.g., sherrod@sherrodsportsvisas.com)

4. **Test the Webhook:**
   - Use n8n's test feature to verify webhook receives data
   - Copy the final webhook URL

5. **Where to Input in Streamlit App:**
   - When generating a landing page, you'll see a field: **"n8n Webhook URL (optional)"**
   - Paste your webhook URL there
   - The generated landing page will POST to this URL on quiz completion

**Example n8n Workflow Structure:**
```
Webhook (Receive POST)
  → Email to Lead (Send quiz results)
  → Email to Admin (New lead notification)
  → [Optional] Add to Google Sheets
  → [Optional] Send Slack notification
```

---

### B. GoHighLevel CRM Integration Webhook

**What it does:** Syncs leads to GoHighLevel CRM automatically

**Setup Instructions:**

1. **Get GoHighLevel API Webhook:**
   - Log into GoHighLevel: https://app.gohighlevel.com
   - Go to **Settings** → **API & Integrations**
   - Create a new **Webhook** or **Custom Webhook**
   - OR use GoHighLevel's **Custom Values** API endpoint
   - Copy the webhook URL

2. **Alternative: Use GoHighLevel API Directly**
   - API endpoint: `https://rest.gohighlevel.com/v1/contacts/`
   - You'll need your GoHighLevel API Key
   - The landing page will POST contact data to this endpoint

3. **Data Sent to GoHighLevel:**
   ```json
   {
     "email": "john@example.com",
     "name": "John Doe",
     "phone": "555-1234",
     "source": "Landing Page - Sherrod Sports Visas",
     "customFields": {
       "quiz_score": 14,
       "quiz_result": "strong",
       "landing_page_campaign": "O1-Visa-Athletes-2025"
     }
   }
   ```

4. **Where to Input in Streamlit App:**
   - Field: **"GoHighLevel Webhook URL (optional)"**
   - Paste your webhook or API endpoint
   - The generated landing page will sync leads to GHL automatically

**GoHighLevel Integration Options:**
- Option 1: Use n8n as middleware (Webhook → n8n → GoHighLevel API)
- Option 2: Direct GoHighLevel webhook (if available in your plan)
- Option 3: Zapier/Make.com as middleware (not recommended, n8n preferred)

---

### C. Microsoft Clarity Heatmap Tracking

**What it does:** Tracks user clicks, scrolls, and sessions with heatmaps and session recordings

**Setup Instructions:**

1. **Create Clarity Project:**
   - Go to https://clarity.microsoft.com
   - Sign in with Microsoft account (free)
   - Click **New Project**
   - Enter project name: "Landing Page - [Brand Name]"
   - Copy the **Project ID** (e.g., `abc123xyz`)

2. **Where to Input in Streamlit App:**
   - Field: **"Microsoft Clarity Project ID (optional)"**
   - Paste your Project ID (NOT the full script, just the ID)
   - The app will auto-generate the tracking code

3. **View Heatmaps:**
   - After deployment, visit your Clarity dashboard
   - You'll see heatmaps, scroll maps, and session recordings within 24 hours

**Note:** Each brand/campaign can have its own Clarity project, or you can use one project for all.

---

## 🎯 Step 3: Generate Your First Landing Page

### Quick Start Guide:

1. **Access the App:**
   - Go to https://landing-page-generator.streamlit.app
   - OR run locally: `streamlit run streamlit_app.py`

2. **Step-by-Step Flow:**

   **Step 1: Choose Brand**
   - Select from 5 brands:
     - Sherrod Sports Visas
     - Innovative Global Talent Agency (IGTA)
     - Aventus Visa Agents
     - Camino Immigration
     - Innovative Automations

   **Step 2: Landing Page Philosophy**
   - Choose conversion strategy:
     - Assessment-Driven Funnel
     - Authority-First Approach
     - Urgency & Scarcity Focus
     - Social Proof Heavy
     - Problem-Solution Framework

   **Step 3: Design Style**
   - Choose aesthetic:
     - Professional & Corporate
     - Modern & Minimalist
     - Bold & Vibrant
     - Elegant & Sophisticated
     - Friendly & Approachable

   **Step 4: Campaign Details**
   - Enter campaign name (e.g., "O1-Visa-Athletes-Q4-2025")
   - Enter target audience (e.g., "Professional MMA fighters seeking O-1 visas")

   **Step 5: Media Options**
   - ✅ Generate hero image with DALL-E (recommended)
   - ✅ Enable A/B testing (generates 2 variations)

   **Step 6: Analytics & Tracking**
   - Enter Airtable Base ID (for analytics tracking)
   - Enter Airtable Table Name (e.g., "Landing Page Analytics")

   **Step 7: Integration Configuration (OPTIONAL)**
   - **n8n Webhook URL:** Paste your n8n webhook (leave blank to skip)
   - **GoHighLevel Webhook URL:** Paste your GHL webhook (leave blank to skip)
   - **Microsoft Clarity Project ID:** Paste your Clarity ID (leave blank to skip)
   - **Calendly URL:** Paste your Calendly booking link (optional)

   **Step 8: Generate & Deploy**
   - Click **Generate Landing Page**
   - Wait 60-90 seconds (AI generation + image creation)
   - Preview the page (Desktop/Mobile/Tablet views)
   - Download HTML file OR
   - Deploy to Netlify with custom subdomain

3. **What Gets Generated:**
   - ✅ Full HTML page with inline CSS and JavaScript
   - ✅ Responsive design (mobile-first)
   - ✅ Interactive eligibility quiz (if brand has quiz configured)
   - ✅ Real testimonials, case studies, achievements
   - ✅ Multi-step contact forms
   - ✅ Calendar integration (Calendly embed)
   - ✅ Heatmap tracking code (if Clarity ID provided)
   - ✅ Webhook integration code (if n8n/GHL URLs provided)
   - ✅ A/B testing variation (if enabled)

---

## 🧪 Step 4: Testing Checklist

### Pre-Deployment Testing:

1. **Generate a Test Page:**
   - Brand: Sherrod Sports Visas (has the most features)
   - Philosophy: Assessment-Driven Funnel
   - Style: Professional & Corporate
   - ✅ Enable DALL-E image
   - ✅ Enable A/B testing

2. **Download HTML and Test Locally:**
   - Download the generated HTML
   - Open in browser (Chrome, Firefox, Safari)
   - Test on mobile device (responsive design)

3. **Test Interactive Features:**
   - **Eligibility Quiz:**
     - Fill out all questions
     - Submit with email
     - Verify quiz results appear
     - Check if webhook fires (test with n8n webhook URL)

   - **Contact Forms:**
     - Submit multi-step form
     - Verify webhook receives data
     - Check email automation triggers (if n8n configured)

   - **Calendar Integration:**
     - Click "Schedule Consultation" button
     - Verify Calendly modal opens (if URL provided)

   - **Heatmap Tracking:**
     - Visit Clarity dashboard after 24 hours
     - Verify page views are tracked

4. **Test Netlify Deployment:**
   - Deploy with a test subdomain (e.g., `test-sherrod-o1visa`)
   - Verify live URL works
   - Test on mobile device
   - Check SSL certificate (should be automatic)

---

## 📊 Step 5: Analytics Setup (Airtable)

### Create Airtable Base for Analytics:

1. **Create New Base:**
   - Go to https://airtable.com
   - Create new base: "Landing Page Analytics"

2. **Create Table with These Fields:**
   ```
   - event_id (Single line text, Primary field)
   - event_type (Single select: page_view, quiz_started, quiz_completed, form_submitted, deployed_to_netlify)
   - campaign (Single line text)
   - brand (Single line text)
   - timestamp (Date with time)
   - user_data (Long text - JSON)
   - metadata (Long text - JSON)
   ```

3. **Get Airtable Credentials:**
   - Base ID: Found in URL (e.g., `appXXXXXXXXXXXXXX`)
   - Table Name: "Landing Page Analytics"
   - API Key: Already in Streamlit secrets

4. **Enter in App:**
   - Step 6 of landing page generator
   - Paste Base ID and Table Name
   - App will auto-track all events

---

## 🚀 Step 6: Deployment Options

### Option 1: Netlify (One-Click from App)

1. **Generate Landing Page** in Streamlit app
2. **Enter Subdomain** (e.g., `sherrod-o1-visa-2025`)
3. **Click "Deploy to Netlify"**
4. **Live URL:** `https://[subdomain].netlify.app`

**Pros:**
- Instant deployment
- Free SSL certificate
- Custom subdomains
- Great for testing

**Cons:**
- Limited to netlify.app subdomains (unless you configure custom domain in Netlify dashboard)

---

### Option 2: Custom Domain Deployment

1. **Download HTML** from Streamlit app
2. **Upload to your hosting:**
   - cPanel File Manager
   - FTP/SFTP
   - Vercel, Cloudflare Pages, GitHub Pages, etc.

3. **Point Custom Domain:**
   - Example: `o1-visa-athletes.sherrodsportsvisas.com`
   - Update DNS A record or CNAME

**Pros:**
- Full control
- Custom branding
- Can use on existing domains

**Cons:**
- Manual upload required
- May need to configure SSL separately

---

### Option 3: Embed in Existing Website

1. **Download HTML** from Streamlit app
2. **Extract key sections** (hero, quiz, testimonials, etc.)
3. **Copy CSS and JavaScript** to your existing site
4. **Integrate** into WordPress, Webflow, etc.

**Pros:**
- Matches existing brand design
- Can customize further

**Cons:**
- Requires web development skills
- More time-consuming

---

## 🛠️ Step 7: Advanced Configuration

### Customize Brand Content:

All brand data is stored in JSON files. You can edit these directly:

1. **`config/brands.json`** - Brand info, colors, CTAs, credentials
2. **`config/verified_content.json`** - Testimonials, services, FAQs, pricing, quiz questions
3. **`config/philosophies.json`** - Landing page conversion strategies
4. **`config/styles.json`** - Design aesthetic configurations

**Example: Add New Testimonial**

Edit `config/verified_content.json`:

```json
{
  "sherrod-sports-visas": {
    "testimonials": [
      {
        "quote": "Your new testimonial here",
        "author": "Client Name",
        "title": "Professional Title",
        "source_url": "https://www.sherrodsportsvisas.com/testimonials",
        "verified": true
      }
    ]
  }
}
```

Commit and push to GitHub - Streamlit will auto-redeploy.

---

### Add New Brand:

1. **Add to `config/brands.json`:**
   ```json
   "new-brand-id": {
     "name": "Brand Name",
     "logo": "https://logo-url.com/logo.png",
     "website": "https://www.brandwebsite.com",
     "colors": {
       "primary": "#003366",
       "secondary": "#0066CC",
       "accent": "#FF6B00"
     },
     "credentials": { ... },
     "trust_badges": [ ... ],
     "ctas": { ... }
   }
   ```

2. **Add to `config/verified_content.json`:**
   ```json
   "new-brand-id": {
     "testimonials": [ ... ],
     "services": [ ... ],
     "faqs": [ ... ]
   }
   ```

3. **Commit and Push** - Brand will appear in dropdown

---

## 🧩 Integration Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│          LANDING PAGE (Generated HTML)          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Quiz    │  │  Form    │  │ Calendar │     │
│  │  Widget  │  │  Submit  │  │  Embed   │     │
│  └────┬─────┘  └────┬─────┘  └──────────┘     │
└───────┼─────────────┼─────────────────────────┘
        │             │
        │             │
        ▼             ▼
┌─────────────────────────────────────────────────┐
│            n8n WORKFLOW (Email)                  │
│  1. Receive webhook POST                         │
│  2. Send quiz results email to lead             │
│  3. Send notification to admin                   │
│  4. [Optional] Add to Google Sheets             │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│         GoHighLevel CRM (Lead Sync)              │
│  - Auto-create contact                           │
│  - Tag with campaign name                        │
│  - Trigger automation workflows                  │
└──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│       Microsoft Clarity (Analytics)              │
│  - Heatmaps                                      │
│  - Session recordings                            │
│  - Click tracking                                │
└──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│         Airtable (Campaign Analytics)            │
│  - Page views                                    │
│  - Quiz completions                              │
│  - Form submissions                              │
│  - Conversion rates                              │
└──────────────────────────────────────────────────┘
```

---

## 📝 Step 8: Production Checklist

Before launching a real campaign:

- [ ] **API Keys Verified** in Streamlit secrets
- [ ] **n8n Workflow** created and tested
- [ ] **GoHighLevel** webhook configured
- [ ] **Microsoft Clarity** project created
- [ ] **Airtable Base** created with correct fields
- [ ] **Calendly Link** updated in brands.json (if using)
- [ ] **Test Landing Page** generated successfully
- [ ] **Quiz Functionality** tested end-to-end
- [ ] **Email Automation** triggered correctly
- [ ] **CRM Sync** working (lead appears in GHL)
- [ ] **Heatmap Tracking** code present in HTML
- [ ] **Mobile Responsive** design verified
- [ ] **A/B Testing** variations generated
- [ ] **Netlify Deployment** successful
- [ ] **Custom Domain** configured (if using)
- [ ] **Analytics Tracking** to Airtable working

---

## 🆘 Troubleshooting

### Issue: "API Key Not Found" Error

**Solution:**
- Verify API keys in Streamlit Cloud Secrets
- Restart the Streamlit app after adding secrets
- Check for typos in key names (case-sensitive)

---

### Issue: n8n Webhook Not Receiving Data

**Solution:**
1. Test webhook URL directly with curl:
   ```bash
   curl -X POST https://your-n8n-instance.app.n8n.cloud/webhook/abc123 \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```
2. Check n8n workflow is active (not paused)
3. Verify webhook URL is correctly pasted in app
4. Check browser console for JavaScript errors

---

### Issue: GoHighLevel Not Creating Contacts

**Solution:**
- Verify GHL API key has correct permissions
- Check GHL webhook URL is correct
- Test with GHL's API testing tool
- Consider using n8n as middleware for easier debugging

---

### Issue: Landing Page Not Responsive on Mobile

**Solution:**
- This should not happen (AI generates mobile-first design)
- If it occurs, check the generated HTML for viewport meta tag
- Report issue - may need to adjust Claude prompt

---

### Issue: DALL-E Image Generation Fails

**Solution:**
- Check OpenAI API key and billing status
- Verify you have credits in OpenAI account
- Try generating without image first (uncheck DALL-E option)
- Check if content policy violation (adjust campaign description)

---

### Issue: Netlify Deployment Says "Subdomain Already Exists"

**Solution:**
- Choose a different subdomain name
- Add timestamp or campaign identifier
- Example: `sherrod-o1-visa-2025-q4` instead of `sherrod-o1-visa`

---

## 📞 Support & Resources

### Documentation Files:
- `README.md` - Setup and overview
- `TESTING_REPORT.md` - Comprehensive test results
- `WORLD_CLASS_LANDING_PAGES.md` - Conversion optimization guide
- `DEPLOYMENT.md` - Deployment instructions
- `WHATS_NEW.md` - Changelog

### External Resources:
- **Streamlit Docs:** https://docs.streamlit.io
- **Anthropic API Docs:** https://docs.anthropic.com
- **OpenAI API Docs:** https://platform.openai.com/docs
- **n8n Documentation:** https://docs.n8n.io
- **GoHighLevel API:** https://highlevel.stoplight.io
- **Microsoft Clarity:** https://docs.microsoft.com/en-us/clarity
- **Netlify Docs:** https://docs.netlify.com
- **Airtable API:** https://airtable.com/developers/web/api

### GitHub Repository:
```
https://github.com/IGTA-Tech/landing-page-generator
```

---

## 🎯 Quick Start Summary

**For the impatient developer:**

1. ✅ API keys already in Streamlit secrets (per your confirmation)
2. 🔗 Create n8n workflow → Get webhook URL
3. 🔗 Get GoHighLevel webhook URL
4. 📊 Create Microsoft Clarity project → Get Project ID
5. 📈 Create Airtable base → Get Base ID
6. 🎨 Open https://landing-page-generator.streamlit.app
7. 🚀 Generate landing page with Sherrod Sports Visas
8. 🧪 Test quiz, forms, and integrations
9. 🌐 Deploy to Netlify or download HTML
10. ✅ Verify analytics in Airtable and Clarity

**Time to First Landing Page:** 15-30 minutes

---

## 🏁 Next Steps After First Deployment

Once your first landing page is live:

1. **Monitor Performance:**
   - Check Airtable for analytics
   - Review Clarity heatmaps after 24 hours
   - Monitor leads in GoHighLevel
   - Check n8n workflow executions

2. **A/B Testing:**
   - Deploy both variations A and B
   - Split traffic 50/50
   - Compare conversion rates in Airtable
   - Keep winner, iterate on loser

3. **Iterate & Optimize:**
   - Update testimonials in verified_content.json
   - Adjust quiz questions based on results
   - Modify CTAs in brands.json
   - Regenerate with different philosophy/style

4. **Scale:**
   - Generate pages for other brands
   - Create multiple campaigns per brand
   - Test different philosophies and styles
   - Build conversion optimization playbook

---

**Good luck! You have everything you need to start generating high-converting landing pages. 🚀**

**Questions?** Review the documentation files or check the GitHub repository for updates.

---

**Generated:** 2025-10-22
**Version:** 2.0 (GoHighLevel + n8n Integration)
**Status:** ✅ Production Ready
