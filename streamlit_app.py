import streamlit as st
from anthropic import Anthropic
import openai
import requests
import json
from datetime import datetime
import os
import zipfile
import io
import base64

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Landing Page Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'intent' not in st.session_state:
    st.session_state.intent = None
if 'intent_raw' not in st.session_state:
    st.session_state.intent_raw = None
if 'brand' not in st.session_state:
    st.session_state.brand = None
if 'brand_data' not in st.session_state:
    st.session_state.brand_data = None
if 'philosophy' not in st.session_state:
    st.session_state.philosophy = None
if 'style' not in st.session_state:
    st.session_state.style = None
if 'cta' not in st.session_state:
    st.session_state.cta = None
if 'media' not in st.session_state:
    st.session_state.media = None
if 'html' not in st.session_state:
    st.session_state.html = None
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'deployed_url' not in st.session_state:
    st.session_state.deployed_url = None
if 'preview_mode' not in st.session_state:
    st.session_state.preview_mode = 'desktop'
if 'show_html_editor' not in st.session_state:
    st.session_state.show_html_editor = False
if 'copy_preview' not in st.session_state:
    st.session_state.copy_preview = None
if 'copy_approved' not in st.session_state:
    st.session_state.copy_approved = False
if 'custom_colors' not in st.session_state:
    st.session_state.custom_colors = None
if 'style_selected' not in st.session_state:
    st.session_state.style_selected = False
if 'ab_testing' not in st.session_state:
    st.session_state.ab_testing = False
if 'variation_b' not in st.session_state:
    st.session_state.variation_b = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data
def load_brands():
    """Load brand configurations from JSON"""
    try:
        with open('config/brands.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("brands.json not found. Please ensure config/brands.json exists.")
        return {}

@st.cache_data
def load_philosophy():
    """Load philosophy configurations from JSON"""
    try:
        with open('config/philosophy.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("philosophy.json not found. Please ensure config/philosophy.json exists.")
        return {}

@st.cache_data
def load_verified_content():
    """Load verified content from crawled websites"""
    try:
        with open('config/verified_content.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning("verified_content.json not found. Testimonials will be disabled.")
        return {}

def get_secret(key):
    """Get secret from Streamlit secrets or environment variable"""
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variable (for local development)
        return os.getenv(key)

def is_valid_url(url):
    """Validate URL format"""
    import re
    if not url:
        return False
    # Check for http:// or https://
    pattern = re.compile(r'^https?://.+')
    return bool(pattern.match(url))

def get_contrast_text_color(hex_color):
    """Return black or white text color based on background luminance"""
    try:
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        # Convert to RGB
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        # Calculate relative luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        # Return black for light backgrounds, white for dark
        return '#000000' if luminance > 0.5 else '#FFFFFF'
    except:
        return '#FFFFFF'  # Default to white if error

def check_color_accessibility(bg_color, text_color='#FFFFFF'):
    """Check WCAG contrast ratio between background and text colors"""
    try:
        def get_luminance(hex_color):
            hex_color = hex_color.lstrip('#')
            r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
            # Convert to linear RGB
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        l1 = get_luminance(bg_color)
        l2 = get_luminance(text_color)

        # Calculate contrast ratio
        lighter = max(l1, l2)
        darker = min(l1, l2)
        ratio = (lighter + 0.05) / (darker + 0.05)

        # WCAG AA requires 4.5:1 for normal text, 3:1 for large text
        if ratio >= 4.5:
            return "✅ Excellent", ratio
        elif ratio >= 3.0:
            return "⚠️ Good for large text only", ratio
        else:
            return "❌ Poor contrast", ratio
    except:
        return "❓ Unable to check", 1.0

def parse_intent(user_input):
    """Parse user intent using Claude API"""
    try:
        api_key = get_secret('ANTHROPIC_API_KEY')
        if not api_key:
            st.error("ANTHROPIC_API_KEY not set in secrets or environment")
            return "Unable to parse intent - API key missing"

        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""Parse this landing page request and extract key information.

Request: {user_input}

Provide a structured analysis covering:
- Campaign type (e.g., lead generation, product launch, event registration)
- Target audience
- Primary objective
- Suggested approach

Keep it concise and actionable."""
            }]
        )
        return response.content[0].text
    except Exception as e:
        st.error(f"Error parsing intent: {str(e)}")
        return f"Error: {str(e)}"

def generate_copy_preview(brand, philosophy, style, cta, intent):
    """Generate copy/content preview before HTML generation"""
    try:
        api_key = get_secret('ANTHROPIC_API_KEY')
        if not api_key:
            st.error("ANTHROPIC_API_KEY not set in secrets or environment")
            return None

        client = Anthropic(api_key=api_key)

        # Load philosophy details
        phil_data = load_philosophy()
        phil_info = phil_data.get(philosophy, {})

        prompt = f"""Generate a detailed content outline for a landing page. DO NOT write HTML - just the copy and content structure.

BRAND INFORMATION:
- Brand Name: {brand['name']}
- Primary Color: {brand['colors']['primary']}
- Website: {brand['website']}

PHILOSOPHY: {philosophy}
{json.dumps(phil_info, indent=2)}

DESIGN STYLE: {style}

CALL-TO-ACTION:
- Primary: {cta['primary']['text']} → {cta['primary']['url']}
{'- Secondary: ' + cta.get('secondary', {}).get('text', '') + ' → ' + cta.get('secondary', {}).get('url', '') if 'secondary' in cta else ''}

USER GOAL/INTENT:
{intent}

Please provide:
1. **Page Title** - The main headline (H1)
2. **Subheadline** - Supporting text under the headline
3. **Section Breakdown** - List each section with:
   - Section title
   - Key message/copy
   - Purpose
4. **Key Benefits** - 3-5 bullet points
5. **Meta Description** - For SEO (150-160 characters)
6. **Meta Title** - For browser tab (50-60 characters)

Format as clear, structured text that I can review and approve before HTML generation."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
    except Exception as e:
        st.error(f"Error generating copy preview: {str(e)}")
        return None

def generate_landing_page(brand, philosophy, style, cta, intent, copy_preview=None, feedback=None, hero_image_url=None, brand_id=None):
    """Generate landing page HTML using Claude API"""
    try:
        api_key = get_secret('ANTHROPIC_API_KEY')
        if not api_key:
            st.error("ANTHROPIC_API_KEY not set in secrets or environment")
            return "<html><body><h1>Error: API key missing</h1></body></html>"

        client = Anthropic(api_key=api_key)

        # Load philosophy details
        phil_data = load_philosophy()
        phil_info = phil_data.get(philosophy, {})

        # Load verified content for this brand
        verified_content = load_verified_content()
        brand_content = verified_content.get(brand_id, {}) if brand_id else {}

        # Build copy guidance section
        copy_guidance = ""
        if copy_preview:
            copy_guidance = f"""
APPROVED COPY OUTLINE:
{copy_preview}

Use this approved copy as the foundation for your HTML content.
"""

        if feedback:
            copy_guidance += f"""
USER FEEDBACK/ADJUSTMENTS:
{feedback}

Please incorporate this feedback into the final HTML.
"""

        # Add hero image if generated
        hero_image_instruction = ""
        if hero_image_url:
            hero_image_instruction = f"""
HERO IMAGE (REQUIRED):
- Use this AI-generated image as the main hero image: {hero_image_url}
- Place it prominently in the hero section
- Use proper <img> tag with alt text describing the image
- Make it responsive and visually impactful
"""

        # Add verified content instructions
        verified_content_instruction = """
⚠️ CRITICAL TESTIMONIAL POLICY:
"""

        # Check if testimonials are available
        has_testimonials = brand_content.get('testimonials') and len(brand_content.get('testimonials', [])) > 0
        allow_ai_testimonials = brand_content.get('allow_ai_testimonials', False)

        if has_testimonials:
            testimonials_json = json.dumps(brand_content['testimonials'], indent=2)
            verified_content_instruction += f"""
VERIFIED TESTIMONIALS (Use ONLY these):
{testimonials_json}

- You MUST use ONLY these verified testimonials
- DO NOT modify or paraphrase these testimonials
- Include attribution exactly as provided
- You may use fewer testimonials, but NEVER create fake ones
"""
        else:
            verified_content_instruction += """
NO VERIFIED TESTIMONIALS AVAILABLE.

⛔ DO NOT CREATE, FABRICATE, OR MAKE UP ANY TESTIMONIALS
⛔ DO NOT include a testimonials section if no verified testimonials exist
⛔ DO NOT use placeholder testimonials
⛔ DO NOT paraphrase or invent customer quotes

If you want social proof, use:
- Trust badges
- Certifications
- Years of experience
- General statistics (if verified achievements are provided)
"""

        # Add verified achievements if available
        if brand_content.get('achievements'):
            achievements_json = json.dumps(brand_content['achievements'], indent=2)
            verified_content_instruction += f"""

VERIFIED ACHIEVEMENTS (Use these for social proof):
{achievements_json}
"""

        # Add verified services if available
        if brand_content.get('services'):
            services_json = json.dumps(brand_content['services'][:5], indent=2)  # Limit to 5
            verified_content_instruction += f"""

VERIFIED SERVICES (Reference these):
{services_json}
"""

        # Add founder info if available
        founder_info = ""
        if 'founder' in brand:
            founder_info = f"\n- Founder: {brand['founder']}"
        if 'tagline' in brand:
            founder_info += f"\n- Tagline: {brand['tagline']} (use this in appropriate places like footer or about section)"

        # Add credentials if available
        credentials_info = ""
        if 'credentials' in brand:
            credentials_json = json.dumps(brand['credentials'], indent=2)
            credentials_info = f"""

CREDENTIALS & QUALIFICATIONS (Display prominently for trust):
{credentials_json}

- Include success rate, years of experience, total clients/approvals prominently
- For attorneys: Display bar number, certifications, specializations
- Build credibility through specific numbers and verifiable credentials
"""

        # Add trust badges
        trust_badges_info = ""
        if 'trust_badges' in brand:
            trust_badges_json = json.dumps(brand['trust_badges'], indent=2)
            trust_badges_info = f"""

TRUST BADGES (Display near hero section):
{trust_badges_json}

- Create a visually appealing trust badge section near the top of the page
- Use icons and clear text
- Make badges stand out with brand colors
"""

        # Add FAQs from verified content
        faq_info = ""
        if brand_content.get('faqs'):
            faqs_json = json.dumps(brand_content['faqs'], indent=2)
            faq_info = f"""

FAQ SECTION (REQUIRED - Address objections):
{faqs_json}

- Create an FAQ section before the final CTA
- Use accordion/collapsible design for clean presentation
- These FAQs address real customer objections - include all of them
"""

        # Add press mentions if available
        press_mentions_info = ""
        if brand_content.get('press_mentions') and len(brand_content['press_mentions']) > 0:
            press_json = json.dumps(brand_content['press_mentions'], indent=2)
            press_mentions_info = f"""

PRESS MENTIONS (As Seen In section):
{press_json}

- Create an "As Seen In" or "Featured In" section
- Display outlet names prominently
- Link to articles if URLs provided
"""

        # Add eligibility quiz if available
        eligibility_quiz_info = ""
        if brand_content.get('eligibility_quiz', {}).get('enabled'):
            quiz_data = json.dumps(brand_content['eligibility_quiz'], indent=2)
            eligibility_quiz_info = f"""

⚠️ REQUIRED: INTERACTIVE ELIGIBILITY QUIZ (High-Converting Lead Generator)
{quiz_data}

- Create a full-page or modal eligibility quiz with JavaScript
- Multi-step progress indicator (Question X of Y)
- Each question on its own screen/step
- Previous/Next navigation buttons
- Email capture before showing results
- Calculate score based on answers (stronger answers = higher scores)
- Show personalized results based on score thresholds
- Include CTA to book consultation in results
- Mobile-friendly design with smooth transitions
- This typically converts at 20-40% - make it prominent!

Scoring guide:
- International competition: 5 points
- Extensive media: 4 points
- Major awards: 5 points
- Professional goals: 3 points
"""

        # Add video testimonials if available
        video_testimonials_info = ""
        if brand_content.get('video_testimonials') and len(brand_content['video_testimonials']) > 0:
            video_json = json.dumps(brand_content['video_testimonials'], indent=2)
            video_testimonials_info = f"""

VIDEO TESTIMONIALS (3x More Trust Than Text):
{video_json}

- Embed YouTube/Vimeo videos using provided URLs
- Display video thumbnail with play button overlay
- Show author name and title below video
- Include short quote preview as caption
- Make videos responsive (16:9 aspect ratio)
- Add "Watch [Client Name]'s Story" headline
- Video testimonials are MUCH more powerful than text - feature them prominently
"""

        # Add live chat widget
        live_chat_info = ""
        if brand.get('live_chat', {}).get('enabled'):
            chat_data = json.dumps(brand['live_chat'], indent=2)
            live_chat_info = f"""

LIVE CHAT WIDGET (Increases Conversions by 38%):
{chat_data}

- Add a chat widget button fixed to bottom-right corner
- Show availability status: "{brand['live_chat'].get('availability_text', 'Chat with us')}"
- Use brand colors for chat button
- Bubble icon with notification dot
- On click: open chat interface (simulate - can say "Chat opens in Intercom")
- Display offline message when outside business hours
- Make it unobtrusive but always visible
"""

        # Add multi-step form
        multi_step_form_info = ""
        if brand.get('lead_form', {}).get('type') == 'multi-step':
            form_data = json.dumps(brand['lead_form'], indent=2)
            multi_step_form_info = f"""

MULTI-STEP LEAD FORM (Higher Completion Rates):
{form_data}

- Create a multi-step form with progress indicator
- Show one step at a time with smooth transitions
- Progress bar showing "Step X of Y"
- Back/Next buttons for navigation
- Validate each step before proceeding
- Final step includes submit button
- Use brand colors for progress indicators
- Make it mobile-responsive
- Multi-step forms have 30-50% higher completion rates than single-page forms
"""

        # Add calendar integration
        calendar_integration_info = ""
        if brand.get('calendar_integration', {}).get('enabled'):
            cal_data = json.dumps(brand['calendar_integration'], indent=2)
            calendar_integration_info = f"""

CALENDAR INTEGRATION (Instant Booking):
{cal_data}

- Embed Calendly/Cal.com booking widget
- Inline embed OR modal popup button
- Button text: "{brand['calendar_integration'].get('button_text', 'Schedule Consultation')}"
- Modal title: "{brand['calendar_integration'].get('modal_title', 'Book Your Consultation')}"
- URL: {brand['calendar_integration'].get('url')}
- Use brand colors for calendar button
- Make it prominent - calendar booking converts at 15-30%
- Place calendar CTA after quiz results or in hero section
"""

        # Add email automation
        email_automation_info = ""
        if brand.get('email_automation', {}).get('enabled'):
            email_data = json.dumps(brand['email_automation'], indent=2)
            email_automation_info = f"""

EMAIL AUTOMATION (Zapier/Webhook Integration):
{email_data}

- Add hidden form fields for webhook submission
- On quiz completion: POST results to webhook URL
- On form submission: POST data to webhook URL
- Include JavaScript to handle webhook POST requests
- Fields to send: name, email, phone, quiz_score, quiz_result
- Webhook URL: {brand['email_automation'].get('webhook_url')}
- Auto-send quiz results email via webhook
- Notify {brand['email_automation'].get('lead_notification_email', 'admin@example.com')} of new leads
"""

        # Add CRM integration
        crm_integration_info = ""
        if brand.get('crm_integration', {}).get('enabled'):
            crm_data = json.dumps(brand['crm_integration'], indent=2)
            crm_integration_info = f"""

CRM INTEGRATION ({brand['crm_integration'].get('provider', 'HubSpot').upper()}):
{crm_data}

- Sync leads to CRM automatically
- POST quiz results to: {brand['crm_integration'].get('webhook_url')}
- Send fields: email, name, phone, company, quiz_score, result_tier
- Include JavaScript for CRM API calls
- Add hidden form for CRM submission
- Track lead source as "Landing Page - [Brand Name]"
"""

        # Add heatmap tracking
        heatmap_tracking_info = ""
        if brand.get('heatmap_tracking', {}).get('enabled'):
            heatmap_data = json.dumps(brand['heatmap_tracking'], indent=2)
            provider = brand['heatmap_tracking'].get('provider', 'microsoft_clarity')
            project_id = brand['heatmap_tracking'].get('project_id', 'YOUR_PROJECT_ID')

            if provider == 'microsoft_clarity':
                heatmap_tracking_info = f"""

HEATMAP TRACKING (Microsoft Clarity):
{heatmap_data}

- Add Microsoft Clarity tracking code to <head>
- Project ID: {project_id}
- Tracking code:
<script type="text/javascript">
    (function(c,l,a,r,i,t,y){{
        c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window, document, "clarity", "script", "{project_id}");
</script>
- Tracks: clicks, scrolls, sessions, heatmaps, session recordings
"""
            elif provider == 'hotjar':
                heatmap_tracking_info = f"""

HEATMAP TRACKING (Hotjar):
{heatmap_data}

- Add Hotjar tracking code to <head>
- Site ID: {project_id}
- Tracking code:
<script>
    (function(h,o,t,j,a,r){{
        h.hj=h.hj||function(){{(h.hj.q=h.hj.q||[]).push(arguments)}};
        h._hjSettings={{hjid:{project_id},hjsv:6}};
        a=o.getElementsByTagName('head')[0];
        r=o.createElement('script');r.async=1;
        r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
        a.appendChild(r);
    }})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
</script>
- Tracks: clicks, scrolls, heatmaps, session recordings, feedback polls
"""

        # Add dynamic pricing
        dynamic_pricing_info = ""
        if brand_content.get('pricing'):
            pricing_data = json.dumps(brand_content['pricing'], indent=2)
            dynamic_pricing_info = f"""

DYNAMIC PRICING DISPLAY:
{pricing_data}

- Show pricing tiers after quiz completion
- Display recommended tier based on quiz score:
  * "strong" → Recommend Premium Package
  * "moderate" → Recommend Standard Package
  * "weak" → Recommend Consultation Only
- Highlight "popular" tier with badge
- Show discount badge: "{brand_content['pricing'].get('discount_badge', '')}"
- Include feature lists for each tier
- Add CTA buttons with tier-specific text
- Use pricing cards with brand colors
- Make it look professional and trustworthy
"""

        # Use custom colors if available, otherwise use brand defaults
        colors = st.session_state.custom_colors if st.session_state.custom_colors else brand['colors']

        prompt = f"""Create a complete, production-ready HTML landing page with inline CSS and JavaScript.
{copy_guidance}
{hero_image_instruction}
{verified_content_instruction}
{credentials_info}
{trust_badges_info}
{faq_info}
{press_mentions_info}
{eligibility_quiz_info}
{video_testimonials_info}
{live_chat_info}
{multi_step_form_info}
{calendar_integration_info}
{email_automation_info}
{crm_integration_info}
{heatmap_tracking_info}
{dynamic_pricing_info}

BRAND INFORMATION:
- Brand Name: {brand['name']}
- Logo URL: {brand['logo']}
- Primary Color: {colors['primary']}
- Secondary Color: {colors['secondary']}
- Accent Color: {colors['accent']}
- Website: {brand['website']}{founder_info}

PHILOSOPHY: {philosophy}
{json.dumps(phil_info, indent=2)}

DESIGN STYLE: {style}

CALL-TO-ACTION:
- Primary: {cta['primary']['text']} → {cta['primary']['url']}
{'- Secondary: ' + cta.get('secondary', {}).get('text', '') + ' → ' + cta.get('secondary', {}).get('url', '') if 'secondary' in cta else ''}

USER GOAL/INTENT:
{intent}

REQUIREMENTS:
1. Fully responsive design (mobile-first)
2. Modern, professional aesthetic matching the {style} style
3. Use brand colors throughout
4. Include logo in header
5. Clear visual hierarchy
6. Fast loading (inline all CSS/JS)
7. Semantic HTML5
8. Accessibility best practices
9. Clear, compelling copy
10. Strong call-to-action buttons with brand colors

For Assessment-Driven Funnel philosophy, include:
- Compelling hook (frustration or readiness based)
- Subheading explaining the 15-question assessment
- Value proposition about measuring 3 key areas
- Credibility section
- Prominent CTA to start the assessment

Return ONLY the complete HTML code, no explanations or markdown formatting."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )

        html = response.content[0].text

        # Clean markdown code blocks if present
        if '```html' in html:
            html = html.split('```html')[1].split('```')[0]
        elif '```' in html:
            html = html.split('```')[1].split('```')[0]

        return html.strip()
    except Exception as e:
        st.error(f"Error generating landing page: {str(e)}")
        return f"<html><body><h1>Error generating page: {str(e)}</h1></body></html>"

def generate_image(brand, intent, style):
    """Generate hero image using DALL-E"""
    try:
        api_key = get_secret('OPENAI_API_KEY')
        if not api_key:
            st.error("OPENAI_API_KEY not set in secrets or environment")
            return None

        client = openai.OpenAI(api_key=api_key)

        prompt = f"""Professional hero image for {brand['name']} landing page.
Style: {style}, modern, high-quality.
Purpose: {intent[:200]}
Color scheme: {brand['colors']['primary']} primary color.
Professional photography style, clean composition, no text overlay, no people's faces.
Corporate, trustworthy aesthetic."""

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",
            quality="hd",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

def deploy_to_netlify(html, subdomain):
    """Deploy HTML to Netlify"""
    try:
        netlify_token = get_secret('NETLIFY_TOKEN')
        if not netlify_token:
            st.error("NETLIFY_TOKEN not set in secrets or environment")
            return None

        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('index.html', html)
        zip_buffer.seek(0)

        # Create site
        create_response = requests.post(
            "https://api.netlify.com/api/v1/sites",
            headers={
                "Authorization": f"Bearer {netlify_token}",
                "Content-Type": "application/json"
            },
            json={"name": subdomain}
        )

        if create_response.status_code not in [200, 201]:
            st.error(f"Error creating Netlify site: {create_response.text}")
            return None

        site_id = create_response.json()['id']

        # Deploy
        deploy_response = requests.post(
            f"https://api.netlify.com/api/v1/sites/{site_id}/deploys",
            headers={
                "Authorization": f"Bearer {netlify_token}",
                "Content-Type": "application/zip"
            },
            data=zip_buffer.read()
        )

        if deploy_response.status_code not in [200, 201]:
            st.error(f"Error deploying to Netlify: {deploy_response.text}")
            return None

        return deploy_response.json().get('ssl_url', deploy_response.json().get('url'))
    except Exception as e:
        st.error(f"Error deploying to Netlify: {str(e)}")
        return None

def save_to_airtable(data):
    """Save landing page data to Airtable"""
    try:
        airtable_key = get_secret('AIRTABLE_API_KEY')
        base_id = get_secret('AIRTABLE_BASE_ID')

        if not airtable_key or not base_id:
            st.error("AIRTABLE_API_KEY or AIRTABLE_BASE_ID environment variable not set")
            return None

        url = f"https://api.airtable.com/v0/{base_id}/Landing%20Pages"
        headers = {
            "Authorization": f"Bearer {airtable_key}",
            "Content-Type": "application/json"
        }

        record = {
            "fields": {
                "Campaign": data['campaign'],
                "Brand": data['brand'],
                "Philosophy": data['philosophy'],
                "Style": data['style'],
                "Created": datetime.now().isoformat(),
                "HTML": data['html'][:100000],  # Airtable field limit
                "URL": data.get('url', '')
            }
        }

        response = requests.post(url, json=record, headers=headers)

        if response.status_code not in [200, 201]:
            st.error(f"Error saving to Airtable: {response.text}")
            return None

        return response.json()
    except Exception as e:
        st.error(f"Error saving to Airtable: {str(e)}")
        return None

def track_analytics_event(event_type, data=None):
    """Track user analytics events to Airtable for funnel optimization"""
    try:
        airtable_key = get_secret('AIRTABLE_API_KEY')
        base_id = get_secret('AIRTABLE_BASE_ID')

        if not airtable_key or not base_id:
            # Analytics is optional, don't show error to user
            return None

        url = f"https://api.airtable.com/v0/{base_id}/Analytics"
        headers = {
            "Authorization": f"Bearer {airtable_key}",
            "Content-Type": "application/json"
        }

        # Get session ID (create if doesn't exist)
        if 'session_id' not in st.session_state:
            import uuid
            st.session_state.session_id = str(uuid.uuid4())[:8]

        record = {
            "fields": {
                "SessionID": st.session_state.session_id,
                "EventType": event_type,
                "Timestamp": datetime.now().isoformat(),
                "StepNumber": st.session_state.get('step', 0),
                "Brand": st.session_state.get('brand', ''),
                "Philosophy": st.session_state.get('philosophy', ''),
                "Style": st.session_state.get('style', ''),
                "ABTesting": st.session_state.get('ab_testing', False),
                "Data": json.dumps(data) if data else ''
            }
        }

        # Send async (don't block UI)
        response = requests.post(url, json=record, headers=headers, timeout=2)
        return response.json() if response.status_code in [200, 201] else None
    except:
        # Silently fail - analytics shouldn't break the app
        return None

# ============================================================================
# MODERN CSS STYLING
# ============================================================================
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* Main header with gradient */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.6s ease-out;
    }

    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
        animation: fadeIn 0.8s ease-out;
    }

    /* Modern step cards */
    .step-card {
        padding: 2rem;
        border-radius: 16px;
        border: 2px solid transparent;
        background: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideInUp 0.5s ease-out;
    }

    .step-card:hover {
        border-color: #667eea;
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.15);
        transform: translateY(-4px);
    }

    /* Brand cards with gradient hover */
    .brand-card {
        text-align: center;
        padding: 1.5rem;
        border-radius: 16px;
        border: 2px solid #f0f0f0;
        background: white;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }

    .brand-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        opacity: 0;
        transition: opacity 0.3s;
        z-index: 0;
    }

    .brand-card:hover::before {
        opacity: 1;
    }

    .brand-card:hover {
        border-color: #667eea;
        transform: translateY(-8px);
        box-shadow: 0 16px 32px rgba(102, 126, 234, 0.2);
    }

    /* Modern progress indicator */
    .progress-step {
        text-align: center;
        font-size: 0.75rem;
        padding: 0.75rem;
        border-radius: 12px;
        transition: all 0.3s;
        font-weight: 600;
    }

    /* Preview container with device frames */
    .preview-container {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
        border: 2px solid #f0f0f0;
    }

    .mobile-frame {
        max-width: 375px;
        margin: 2rem auto;
        border: 12px solid #1f1f1f;
        border-radius: 36px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        background: #1f1f1f;
        padding: 4px;
    }

    .desktop-frame {
        max-width: 100%;
        margin: 1rem auto;
        border: 8px solid #333;
        border-radius: 12px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
    }

    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Button improvements */
    .stButton button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }

    /* Modern input fields */
    .stTextInput input, .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PROGRESS INDICATOR
# ============================================================================
st.markdown("### 📍 Your Progress")
cols = st.columns(8)
steps = ["Intent", "Brand", "Philosophy", "Style", "CTAs", "Media", "Copy Review", "Generate"]
for i, (col, step_name) in enumerate(zip(cols, steps)):
    with col:
        if i + 1 < st.session_state.step:
            st.success(f"✅ {step_name}")
        elif i + 1 == st.session_state.step:
            st.info(f"**➡️ {step_name}**")
        else:
            st.text(f"⭕ {step_name}")

st.divider()

# ============================================================================
# START OVER BUTTON (Sidebar)
# ============================================================================
with st.sidebar:
    st.markdown("### 🔄 Quick Actions")
    if st.button("🔄 Start New Landing Page", use_container_width=True, type="secondary"):
        # Reset all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Save/Load Configuration
    if st.session_state.step > 1:
        st.divider()
        st.markdown("### 💾 Save/Load Config")

        # Create configuration dict
        config = {
            'intent_raw': st.session_state.get('intent_raw'),
            'brand': st.session_state.get('brand'),
            'philosophy': st.session_state.get('philosophy'),
            'style': st.session_state.get('style'),
            'custom_colors': st.session_state.get('custom_colors'),
            'cta': st.session_state.get('cta'),
            'media': st.session_state.get('media'),
        }

        # Download config
        config_json = json.dumps(config, indent=2)
        st.download_button(
            label="💾 Save Config",
            data=config_json,
            file_name=f"landing-config-{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
            help="Save your current configuration to reuse later"
        )

        # Load config
        uploaded_file = st.file_uploader("📁 Load Config", type=['json'], help="Upload a previously saved configuration")
        if uploaded_file:
            try:
                loaded_config = json.load(uploaded_file)
                # Apply loaded config to session state
                for key, value in loaded_config.items():
                    if value is not None:
                        st.session_state[key] = value
                # Reload brand data if brand ID exists
                if loaded_config.get('brand'):
                    brands = load_brands()
                    st.session_state.brand_data = brands.get(loaded_config['brand'])
                st.success("✅ Configuration loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading config: {str(e)}")

    if st.session_state.step > 1:
        st.divider()
        st.markdown("### 📊 Current Settings")
        if st.session_state.get('brand_data'):
            st.caption(f"**Brand:** {st.session_state.brand_data['name']}")
        if st.session_state.get('philosophy'):
            st.caption(f"**Philosophy:** {st.session_state.philosophy}")
        if st.session_state.get('style'):
            st.caption(f"**Style:** {st.session_state.style}")

# ============================================================================
# STEP 1: INTENT CAPTURE
# ============================================================================
if st.session_state.step == 1:
    st.markdown('<div class="main-header">🚀 Landing Page Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Create professional landing pages in minutes with AI</div>', unsafe_allow_html=True)
    st.markdown("### 💭 What are you looking to create today?")

    # Template Library
    st.info("✨ **Quick Start**: Choose a template below or describe your own custom landing page")

    templates = {
        "🎓 Webinar Registration": "Landing page for free O-1 visa eligibility webinar to capture athlete emails and book consultation calls",
        "📧 Lead Magnet Download": "Lead magnet page offering free immigration checklist download in exchange for email address",
        "🚀 Service Launch": "Product launch page for automation service targeting small businesses with free trial offer",
        "📞 Free Consultation": "Conversion page to book free visa consultation calls with calendar integration",
        "🎯 Event Registration": "Event registration page for immigration law conference with early bird discount",
        "💼 Case Study Showcase": "Landing page showcasing successful visa case studies to build credibility and capture leads"
    }

    cols = st.columns(3)
    for idx, (template_name, template_desc) in enumerate(templates.items()):
        with cols[idx % 3]:
            if st.button(template_name, key=f"template_{idx}", use_container_width=True):
                st.session_state.template_selected = template_desc
                st.rerun()

    st.divider()

    # Initialize user input from template if selected
    default_value = st.session_state.get('template_selected', '')

    user_input = st.text_area(
        "Describe your goal (or customize the template above):",
        value=default_value,
        height=150,
        placeholder="Example: I need a landing page that helps athletes understand O-1 visa eligibility and captures their email for a free consultation.",
        key="intent_input"
    )

    # Clear template selection after it's used
    if st.session_state.get('template_selected'):
        st.session_state.template_selected = None

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Continue →", type="primary", disabled=not user_input, use_container_width=True):
            with st.spinner("🤔 Understanding your goal..."):
                st.session_state.intent = parse_intent(user_input)
                st.session_state.intent_raw = user_input
                st.session_state.step = 2
                # Track analytics
                track_analytics_event("intent_submitted", {"intent_length": len(user_input)})
                st.rerun()

# ============================================================================
# STEP 2: BRAND SELECTION
# ============================================================================
elif st.session_state.step == 2:
    st.markdown('<div class="main-header">Select Your Brand</div>', unsafe_allow_html=True)

    # Show parsed intent
    with st.expander("📋 Your Goal (parsed)", expanded=False):
        st.info(st.session_state.intent)

    brands = load_brands()

    if not brands:
        st.error("No brands configured. Please check config/brands.json")
    else:
        cols = st.columns(3)
        for idx, (brand_id, brand) in enumerate(brands.items()):
            with cols[idx % 3]:
                st.markdown('<div class="brand-card">', unsafe_allow_html=True)
                st.image(brand['logo'], width=200)
                st.subheader(brand['name'])
                st.caption(brand['website'])

                # Color preview banner
                primary = brand['colors']['primary']
                secondary = brand['colors']['secondary']
                accent = brand['colors']['accent']
                st.markdown(
                    f'''<div style="display: flex; height: 40px; margin: 10px 0; border-radius: 8px; overflow: hidden; border: 2px solid #e0e0e0;">
                        <div style="flex: 1; background-color: {primary}; display: flex; align-items: center; justify-content: center; color: {get_contrast_text_color(primary)}; font-size: 0.75rem; font-weight: bold;">PRIMARY</div>
                        <div style="flex: 1; background-color: {secondary}; display: flex; align-items: center; justify-content: center; color: {get_contrast_text_color(secondary)}; font-size: 0.75rem; font-weight: bold;">SECONDARY</div>
                        <div style="flex: 1; background-color: {accent}; display: flex; align-items: center; justify-content: center; color: {get_contrast_text_color(accent)}; font-size: 0.75rem; font-weight: bold;">ACCENT</div>
                    </div>''',
                    unsafe_allow_html=True
                )

                if st.button(f"Select {brand['name']}", key=brand_id, use_container_width=True, type="primary"):
                    st.session_state.brand = brand_id
                    st.session_state.brand_data = brand
                    st.session_state.step = 3
                    # Track analytics
                    track_analytics_event("brand_selected", {"brand": brand_id})
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    if st.button("← Back to Intent"):
        st.session_state.step = 1
        st.rerun()

# ============================================================================
# STEP 3: PHILOSOPHY SELECTION
# ============================================================================
elif st.session_state.step == 3:
    st.markdown('<div class="main-header">Choose Your Philosophy</div>', unsafe_allow_html=True)
    st.caption(f"Brand: {st.session_state.brand_data['name']}")

    philosophies = {
        'assessment-funnel': {
            'name': '📊 Assessment-Driven Funnel',
            'emoji': '📊',
            'description': 'Lead generation through quiz/assessment that qualifies prospects',
            'conversion': '20-40% take assessment, 30-50% of those qualify',
            'best_for': 'High-intent lead capture, service businesses, coaching',
            'features': [
                '15-question assessment',
                'Automatic lead qualification',
                'Personalized results page',
                'Dynamic next steps based on score'
            ]
        },
        'traditional': {
            'name': '📈 Traditional Funnel',
            'emoji': '📈',
            'description': 'Standard top/middle/bottom approach with clear product offers',
            'conversion': '2-10% typical conversion rate',
            'best_for': 'Clear product offers, e-commerce, SaaS with defined pricing',
            'features': [
                'Hero with value prop',
                'Features & benefits',
                'Social proof section',
                'Pricing/offer details'
            ]
        },
        'story-driven': {
            'name': '📖 Story-Driven',
            'emoji': '📖',
            'description': 'Narrative emotional connection through founder or customer stories',
            'conversion': '5-15% engaged conversion',
            'best_for': 'Personal brands, mission-driven companies, nonprofits',
            'features': [
                'Compelling narrative arc',
                'Emotional connection points',
                'Transformation journey',
                'Mission-focused messaging'
            ]
        },
        'social-proof-heavy': {
            'name': '⭐ Social Proof Heavy',
            'emoji': '⭐',
            'description': 'Testimonials, case studies, and results-focused approach',
            'conversion': '10-25% with strong proof',
            'best_for': 'Established brands with strong track records',
            'features': [
                'Prominent testimonials',
                'Detailed case studies',
                'Results/stats grid',
                'Risk reversal guarantees'
            ]
        }
    }

    for phil_id, phil in philosophies.items():
        with st.expander(f"{phil['emoji']} {phil['name']}", expanded=(phil_id == 'assessment-funnel')):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**{phil['description']}**")
                st.markdown(f"**Conversion:** {phil['conversion']}")
                st.markdown(f"**Best for:** {phil['best_for']}")

                st.markdown("**Key Features:**")
                for feature in phil['features']:
                    st.markdown(f"- {feature}")

            with col2:
                if st.button(f"Select", key=f"phil_{phil_id}", type="primary", use_container_width=True):
                    st.session_state.philosophy = phil_id
                    st.session_state.step = 4
                    # Track analytics
                    track_analytics_event("philosophy_selected", {"philosophy": phil_id})
                    st.rerun()

    st.divider()
    if st.button("← Back to Brand"):
        st.session_state.step = 2
        st.rerun()

# ============================================================================
# STEP 4: STYLE SELECTION
# ============================================================================
elif st.session_state.step == 4:
    st.markdown('<div class="main-header">Choose Your Style</div>', unsafe_allow_html=True)
    st.caption(f"Brand: {st.session_state.brand_data['name']} | Philosophy: {st.session_state.philosophy}")

    styles = {
        'professional': {
            'name': 'Professional & Corporate',
            'desc': 'Clean, trustworthy, traditional business aesthetic',
            'emoji': '💼',
            'characteristics': 'Structured layouts, serif fonts, conservative colors'
        },
        'modern': {
            'name': 'Modern & Minimal',
            'desc': 'Sleek, contemporary, lots of white space',
            'emoji': '✨',
            'characteristics': 'Sans-serif fonts, clean lines, minimal elements'
        },
        'bold': {
            'name': 'Bold & Energetic',
            'desc': 'High-contrast, dynamic, attention-grabbing',
            'emoji': '⚡',
            'characteristics': 'Strong colors, large typography, dynamic layouts'
        },
        'warm': {
            'name': 'Warm & Trustworthy',
            'desc': 'Friendly, approachable, human-centered',
            'emoji': '🤝',
            'characteristics': 'Rounded corners, warm colors, inviting imagery'
        },
        'premium': {
            'name': 'Premium & Luxurious',
            'desc': 'Elegant, sophisticated, high-end',
            'emoji': '👑',
            'characteristics': 'Elegant fonts, refined colors, spacious layouts'
        }
    }

    # Show style selection if not yet selected
    if not st.session_state.style_selected:
        cols = st.columns(2)
        for idx, (style_id, style) in enumerate(styles.items()):
            with cols[idx % 2]:
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.subheader(f"{style['emoji']} {style['name']}")
                st.markdown(f"**{style['desc']}**")
                st.caption(style['characteristics'])
                if st.button(f"Select", key=style_id, use_container_width=True, type="primary"):
                    st.session_state.style = style_id
                    st.session_state.style_selected = True
                    # Track analytics
                    track_analytics_event("style_selected", {"style": style_id})
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Show selected style and color customization
        selected_style = styles[st.session_state.style]
        st.success(f"✅ Selected Style: {selected_style['emoji']} {selected_style['name']}")

        st.divider()
        st.subheader("🎨 Customize Brand Colors (Optional)")
        st.info("💡 Adjust the colors to match your exact brand. Leave as-is to use the default brand colors.")

        brand = st.session_state.brand_data
        col1, col2, col3 = st.columns(3)

        with col1:
            primary_color = st.color_picker(
                "Primary Color",
                value=st.session_state.custom_colors['primary'] if st.session_state.custom_colors else brand['colors']['primary'],
                help="Used for main buttons and headers",
                key="primary_color_picker"
            )

        with col2:
            secondary_color = st.color_picker(
                "Secondary Color",
                value=st.session_state.custom_colors['secondary'] if st.session_state.custom_colors else brand['colors']['secondary'],
                help="Used for backgrounds and accents",
                key="secondary_color_picker"
            )

        with col3:
            accent_color = st.color_picker(
                "Accent Color",
                value=st.session_state.custom_colors['accent'] if st.session_state.custom_colors else brand['colors']['accent'],
                help="Used for highlights and special elements",
                key="accent_color_picker"
            )

        # Store custom colors
        st.session_state.custom_colors = {
            'primary': primary_color,
            'secondary': secondary_color,
            'accent': accent_color
        }

        # Show color preview with smart text colors
        st.markdown("**Color Preview:**")
        primary_text = get_contrast_text_color(primary_color)
        secondary_text = get_contrast_text_color(secondary_color)
        accent_text = get_contrast_text_color(accent_color)

        st.markdown(
            f'''<div style="display: flex; gap: 10px; margin: 10px 0;">
                <div style="width: 100px; height: 50px; background-color: {primary_color}; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: {primary_text}; font-weight: bold;">Primary</div>
                <div style="width: 100px; height: 50px; background-color: {secondary_color}; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: {secondary_text}; font-weight: bold;">Secondary</div>
                <div style="width: 100px; height: 50px; background-color: {accent_color}; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: {accent_text}; font-weight: bold;">Accent</div>
            </div>''',
            unsafe_allow_html=True
        )

        # Accessibility check
        st.markdown("**♿ Accessibility Check:**")
        status_primary, ratio_primary = check_color_accessibility(primary_color, '#FFFFFF')
        status_secondary, ratio_secondary = check_color_accessibility(secondary_color, '#FFFFFF')
        status_accent, ratio_accent = check_color_accessibility(accent_color, '#FFFFFF')

        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"Primary: {status_primary}")
            st.caption(f"Ratio: {ratio_primary:.2f}:1")
        with col2:
            st.caption(f"Secondary: {status_secondary}")
            st.caption(f"Ratio: {ratio_secondary:.2f}:1")
        with col3:
            st.caption(f"Accent: {status_accent}")
            st.caption(f"Ratio: {ratio_accent:.2f}:1")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Philosophy"):
            st.session_state.step = 3
            st.session_state.style_selected = False
            st.session_state.custom_colors = None  # Reset custom colors
            st.rerun()

    with col2:
        if st.session_state.style_selected:
            if st.button("Continue to CTAs →", type="primary", use_container_width=True):
                st.session_state.step = 5
                st.rerun()

# ============================================================================
# STEP 5: CTA CONFIGURATION
# ============================================================================
elif st.session_state.step == 5:
    st.markdown('<div class="main-header">⚡ Configure Call-to-Action</div>', unsafe_allow_html=True)
    st.caption(f"Brand: {st.session_state.brand_data['name']} | Style: {st.session_state.style}")

    brand = st.session_state.brand_data
    phil = st.session_state.philosophy

    # Default CTA based on philosophy (only if not already set)
    if phil == 'assessment-funnel':
        default_text = "Take the Free Assessment"
        default_url = brand['ctas']['top']['url']
    else:
        default_text = brand['ctas']['middle']['text']
        default_url = brand['ctas']['middle']['url']

    # Use session state to preserve values if already set
    if 'cta_text_value' not in st.session_state:
        st.session_state.cta_text_value = default_text
    if 'cta_url_value' not in st.session_state:
        st.session_state.cta_url_value = default_url

    st.info("💡 These are the main action buttons on your landing page. Customize the text and destination URL.")

    st.subheader("Primary Call-to-Action")
    col1, col2 = st.columns(2)

    with col1:
        cta_text = st.text_input(
            "CTA Button Text",
            value=st.session_state.cta_text_value,
            key="cta_text_input",
            help="The text that appears on your main call-to-action button",
            placeholder="e.g., Get Started, Sign Up, Learn More"
        )
        if cta_text:
            st.session_state.cta_text_value = cta_text

    with col2:
        cta_url = st.text_input(
            "CTA URL",
            value=st.session_state.cta_url_value,
            key="cta_url_input",
            help="Where the button links to when clicked",
            placeholder="https://example.com/signup"
        )
        if cta_url:
            st.session_state.cta_url_value = cta_url

    # Preview - use custom colors if available
    st.markdown("**Preview:**")
    preview_color = st.session_state.custom_colors['primary'] if st.session_state.custom_colors else brand['colors']['primary']
    st.markdown(
        f'<a href="#" style="background-color: {preview_color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 600;">{cta_text}</a>',
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("Secondary Call-to-Action (Optional)")
    include_secondary = st.checkbox("Add secondary CTA?", key="secondary_cta_checkbox", help="Add a second button for alternative actions")

    sec_text = None
    sec_url = None
    if include_secondary:
        col1, col2 = st.columns(2)
        with col1:
            sec_text = st.text_input(
                "Secondary CTA Text",
                value="Learn More",
                key="sec_cta_text",
                placeholder="e.g., Learn More, Contact Us"
            )
        with col2:
            sec_url = st.text_input(
                "Secondary URL",
                value=brand['website'],
                key="sec_cta_url",
                placeholder="https://example.com"
            )

    st.divider()

    # Validation warnings
    has_errors = False
    if not cta_text or not cta_url:
        st.warning("⚠️ Please fill in both the CTA Button Text and CTA URL to continue")
        has_errors = True
    elif cta_url and not is_valid_url(cta_url):
        st.error("❌ Invalid URL format. Please include http:// or https:// (e.g., https://example.com)")
        has_errors = True

    # Validate secondary CTA URL if provided
    if include_secondary and sec_url and not is_valid_url(sec_url):
        st.error("❌ Invalid Secondary URL format. Please include http:// or https://")
        has_errors = True

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Style"):
            st.session_state.step = 4
            st.rerun()

    with col2:
        if st.button("Continue to Media Options →", type="primary", disabled=has_errors, use_container_width=True):
            st.session_state.cta = {
                'primary': {'text': cta_text, 'url': cta_url}
            }
            if include_secondary:
                st.session_state.cta['secondary'] = {'text': sec_text, 'url': sec_url}
            st.session_state.step = 6
            st.rerun()

# ============================================================================
# STEP 6: MEDIA OPTIONS
# ============================================================================
elif st.session_state.step == 6:
    st.markdown('<div class="main-header">Media Options</div>', unsafe_allow_html=True)

    st.info("💡 AI-generated images can enhance your landing page's visual appeal")

    generate_image_opt = st.checkbox(
        "Generate hero image with DALL-E 3?",
        value=True,
        help="Creates a professional hero image matching your brand and style"
    )

    custom_prompt = None
    if generate_image_opt:
        with st.expander("🎨 Customize Image Prompt (Optional)"):
            custom_prompt = st.text_area(
                "Custom image description",
                placeholder="Leave blank for auto-generated prompt based on your brand and intent",
                help="Provide specific details if you want to customize the image generation",
                height=100
            )
            st.caption("Example: 'Modern office setting with diverse team collaborating, bright natural lighting'")

    st.divider()

    # Video option (future feature)
    st.markdown("### Video Generation (Coming Soon)")
    st.caption("AI-generated video with Sora will be available in a future update")
    generate_video = False

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to CTAs"):
            st.session_state.step = 5
            st.rerun()

    with col2:
        if st.button("Continue →", type="primary", use_container_width=True):
            st.session_state.media = {
                'generate_image': generate_image_opt,
                'image_prompt': custom_prompt if generate_image_opt and custom_prompt else None,
                'generate_video': generate_video
            }
            st.session_state.step = 7
            st.rerun()

# ============================================================================
# STEP 7: COPY PREVIEW & APPROVAL
# ============================================================================
elif st.session_state.step == 7:
    st.markdown('<div class="main-header">📝 Review Your Copy & Content</div>', unsafe_allow_html=True)
    st.caption("Review the headlines, text, and structure before generating HTML")

    # Generate copy preview if not already done
    if not st.session_state.get('copy_preview'):
        with st.spinner("✍️ Generating content outline... ⏱️ 10-20 seconds"):
            copy_preview = generate_copy_preview(
                brand=st.session_state.brand_data,
                philosophy=st.session_state.philosophy,
                style=st.session_state.style,
                cta=st.session_state.cta,
                intent=st.session_state.intent_raw
            )
            if copy_preview:
                st.session_state.copy_preview = copy_preview
            else:
                st.error("Failed to generate copy preview. Please try again.")

    # Display the copy preview
    if st.session_state.get('copy_preview'):
        st.info("💡 Review and edit the content below, or add feedback for AI adjustments")

        # Tabs for viewing vs editing
        tab1, tab2 = st.tabs(["📄 View Copy", "✏️ Edit Copy"])

        with tab1:
            st.markdown("### Content Preview (Read-Only)")
            st.markdown(st.session_state.copy_preview)

        with tab2:
            st.markdown("### Edit Your Copy")
            st.caption("Edit the copy directly. Your changes will be used when generating the HTML.")

            edited_copy = st.text_area(
                "Copy Content",
                value=st.session_state.copy_preview,
                height=400,
                key="copy_editor",
                help="Edit the copy directly here"
            )

            if st.button("💾 Save Edits", type="secondary"):
                st.session_state.copy_preview = edited_copy
                st.success("✅ Copy updated! Switch to View tab to see formatted version.")
                st.rerun()

        st.divider()

        # Option for AI feedback
        with st.expander("🤖 Let AI Adjust the Copy (Optional)"):
            feedback = st.text_area(
                "Describe what changes you'd like AI to make:",
                placeholder="e.g., 'Make the headline more compelling' or 'Focus more on benefits than features'",
                help="This feedback will be sent to AI when generating the HTML",
                height=100,
                key="copy_feedback_input"
            )
            if feedback:
                st.session_state.copy_feedback = feedback

        st.divider()

        # A/B Testing Option
        st.markdown("### 🧪 A/B Testing (Optional)")
        ab_test = st.checkbox(
            "Generate 2 variations for A/B testing",
            help="Creates Version A and Version B with different headlines and copy approaches",
            key="ab_test_checkbox"
        )
        if ab_test:
            st.info("💡 We'll generate 2 landing page variations:\n- **Version A**: Focus on benefits and results\n- **Version B**: Focus on pain points and urgency")
            st.session_state.ab_testing = True
        else:
            st.session_state.ab_testing = False

        st.divider()

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("← Back to Media"):
                st.session_state.step = 6
                st.session_state.copy_preview = None  # Clear to regenerate if they come back
                st.rerun()

        with col2:
            if st.button("🔄 Regenerate Copy", help="Generate new copy with different approach"):
                st.session_state.copy_preview = None
                st.rerun()

        with col3:
            if st.button("Continue to HTML →", type="primary", use_container_width=True):
                st.session_state.copy_approved = True
                st.session_state.step = 8
                st.rerun()

# ============================================================================
# STEP 8: GENERATE HTML & PREVIEW
# ============================================================================
elif st.session_state.step == 8:
    st.markdown('<div class="main-header">Generate Your Landing Page</div>', unsafe_allow_html=True)

    # Generate if not already generated
    if not st.session_state.get('html'):
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Generate media FIRST if requested
        if st.session_state.media.get('generate_image'):
            status_text.text("🖼️ Generating hero image with DALL-E 3... ⏱️ This takes 30-60 seconds")
            progress_bar.progress(25)
            try:
                image_url = generate_image(
                    brand=st.session_state.brand_data,
                    intent=st.session_state.intent_raw,
                    style=st.session_state.style
                )
                if image_url:
                    st.session_state.generated_image = image_url
                    st.success(f"✅ Hero image generated!")
            except Exception as e:
                st.warning(f"⚠️ Image generation failed: {str(e)}")
            progress_bar.progress(50)

        # Generate HTML with the hero image
        status_text.text("🎨 Generating your landing page HTML... ⏱️ 15-30 seconds")
        progress_bar.progress(75)

        html = generate_landing_page(
            brand=st.session_state.brand_data,
            philosophy=st.session_state.philosophy,
            style=st.session_state.style,
            cta=st.session_state.cta,
            intent=st.session_state.intent_raw,
            copy_preview=st.session_state.get('copy_preview'),
            feedback=st.session_state.get('copy_feedback'),
            hero_image_url=st.session_state.get('generated_image'),
            brand_id=st.session_state.brand
        )
        st.session_state.html = html

        # Generate Variation B if A/B testing is enabled
        if st.session_state.ab_testing and not st.session_state.get('variation_b'):
            status_text.text("🧪 Generating Variation B for A/B testing... ⏱️ 15-30 seconds")
            progress_bar.progress(85)

            # Create alternative copy guidance for Variation B
            variation_b_feedback = "Create a DIFFERENT approach: Focus on pain points, urgency, and what they're losing by not taking action. Use more emotional triggers and scarcity."

            variation_b_html = generate_landing_page(
                brand=st.session_state.brand_data,
                philosophy=st.session_state.philosophy,
                style=st.session_state.style,
                cta=st.session_state.cta,
                intent=st.session_state.intent_raw,
                copy_preview=st.session_state.get('copy_preview'),
                feedback=variation_b_feedback,
                hero_image_url=st.session_state.get('generated_image'),
                brand_id=st.session_state.brand
            )
            st.session_state.variation_b = variation_b_html

        progress_bar.progress(100)
        if st.session_state.ab_testing:
            status_text.text("✅ Both variations generated successfully!")
        else:
            status_text.text("✅ Landing page generated successfully!")

        # Track analytics
        track_analytics_event("html_generated", {
            "ab_testing": st.session_state.ab_testing,
            "has_image": bool(st.session_state.get('generated_image'))
        })

    if st.session_state.ab_testing:
        st.success("✅ Your A/B test variations are ready!")
    else:
        st.success("✅ Your landing page is ready!")

    # Prominent Download Button(s)
    if st.session_state.ab_testing:
        st.markdown("### 📥 Download Your A/B Test Variations")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🅰️ Version A - Benefits Focused")
            st.download_button(
                label="⬇️ Download Version A",
                data=st.session_state.html,
                file_name=f"landing-{st.session_state.brand}-A-{datetime.now().strftime('%Y%m%d-%H%M')}.html",
                mime="text/html",
                use_container_width=True,
                type="primary",
                help="Benefits and results-focused approach",
                key="download_variation_a"
            )

        with col2:
            st.markdown("#### 🅱️ Version B - Pain Points & Urgency")
            st.download_button(
                label="⬇️ Download Version B",
                data=st.session_state.variation_b,
                file_name=f"landing-{st.session_state.brand}-B-{datetime.now().strftime('%Y%m%d-%H%M')}.html",
                mime="text/html",
                use_container_width=True,
                type="primary",
                help="Pain points and urgency-focused approach",
                key="download_variation_b"
            )
    else:
        st.markdown("### 📥 Download Your Landing Page")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.download_button(
                label="⬇️ Download HTML File",
                data=st.session_state.html,
                file_name=f"landing-{st.session_state.brand}-{datetime.now().strftime('%Y%m%d-%H%M')}.html",
                mime="text/html",
                use_container_width=True,
                type="primary",
                help="Download the complete HTML file with inline CSS"
            )
        with col2:
            # Create data URI for opening in new tab
            import base64
            b64_html = base64.b64encode(st.session_state.html.encode()).decode()
            href = f'data:text/html;base64,{b64_html}'
            st.markdown(f'<a href="{href}" target="_blank" style="text-decoration: none;"><button style="width:100%; padding:0.58rem; background:#667eea; color:white; border:none; border-radius:8px; font-weight:600; cursor:pointer; font-size:1rem;">🔗 Open in New Tab</button></a>', unsafe_allow_html=True)

    st.divider()

    # Show generated image if available
    if st.session_state.get('generated_image'):
        with st.expander("🖼️ Generated Hero Image", expanded=False):
            st.image(st.session_state.generated_image, caption="AI-Generated Hero Image")
            st.caption("This image has been generated and can be downloaded or used in your landing page.")

    # Preview tabs
    if st.session_state.ab_testing:
        tab1, tab2, tab3, tab4 = st.tabs(["👁️ Preview Version A", "👁️ Preview Version B", "💻 HTML Code", "✏️ Edit HTML"])
    else:
        tab1, tab2, tab3 = st.tabs(["👁️ Live Preview", "💻 HTML Code", "✏️ Edit HTML"])

    with tab1:
        if st.session_state.ab_testing:
            st.subheader("🅰️ Version A Preview - Benefits Focused")
        else:
            st.subheader("Preview Your Landing Page")

        # Preview mode toggle
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        with col1:
            if st.button("📱 Mobile", use_container_width=True, type="primary" if st.session_state.preview_mode == 'mobile' else "secondary", key="mobile_preview_a"):
                st.session_state.preview_mode = 'mobile'
                st.rerun()
        with col2:
            if st.button("💻 Desktop", use_container_width=True, type="primary" if st.session_state.preview_mode == 'desktop' else "secondary", key="desktop_preview_a"):
                st.session_state.preview_mode = 'desktop'
                st.rerun()
        with col3:
            # Create data URI for opening in new tab
            import base64
            b64_html = base64.b64encode(st.session_state.html.encode()).decode()
            href = f'data:text/html;base64,{b64_html}'
            st.markdown(f'<a href="{href}" target="_blank"><button style="width:100%; padding:0.5rem; background:#667eea; color:white; border:none; border-radius:8px; font-weight:600; cursor:pointer;">🔗 New Tab</button></a>', unsafe_allow_html=True)

        st.divider()

        # Render preview based on mode
        if st.session_state.preview_mode == 'mobile':
            st.markdown("**Mobile View (375px)**")
            st.markdown('<div class="mobile-frame">', unsafe_allow_html=True)
            st.components.v1.html(st.session_state.html, height=800, scrolling=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("**Desktop View (Full Width)**")
            st.markdown('<div class="desktop-frame">', unsafe_allow_html=True)
            st.components.v1.html(st.session_state.html, height=1000, scrolling=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Version B preview tab (only if A/B testing)
    if st.session_state.ab_testing:
        with tab2:
            st.subheader("🅱️ Version B Preview - Pain Points & Urgency")

            # Preview mode toggle for B
            col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
            with col1:
                if st.button("📱 Mobile", use_container_width=True, type="primary" if st.session_state.preview_mode == 'mobile' else "secondary", key="mobile_preview_b"):
                    st.session_state.preview_mode = 'mobile'
                    st.rerun()
            with col2:
                if st.button("💻 Desktop", use_container_width=True, type="primary" if st.session_state.preview_mode == 'desktop' else "secondary", key="desktop_preview_b"):
                    st.session_state.preview_mode = 'desktop'
                    st.rerun()
            with col3:
                # Create data URI for opening in new tab
                import base64
                b64_html_b = base64.b64encode(st.session_state.variation_b.encode()).decode()
                href_b = f'data:text/html;base64,{b64_html_b}'
                st.markdown(f'<a href="{href_b}" target="_blank"><button style="width:100%; padding:0.5rem; background:#667eea; color:white; border:none; border-radius:8px; font-weight:600; cursor:pointer;">🔗 New Tab</button></a>', unsafe_allow_html=True)

            st.divider()

            # Render preview based on mode
            if st.session_state.preview_mode == 'mobile':
                st.markdown("**Mobile View (375px)**")
                st.markdown('<div class="mobile-frame">', unsafe_allow_html=True)
                st.components.v1.html(st.session_state.variation_b, height=800, scrolling=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("**Desktop View (Full Width)**")
                st.markdown('<div class="desktop-frame">', unsafe_allow_html=True)
                st.components.v1.html(st.session_state.variation_b, height=1000, scrolling=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # HTML Code tab - use correct tab number based on A/B testing
    html_code_tab = tab3 if st.session_state.ab_testing else tab2
    with html_code_tab:
        st.subheader("HTML Source Code")
        if st.session_state.ab_testing:
            version_select = st.radio("Select Version:", ["Version A", "Version B"], horizontal=True)
            html_to_show = st.session_state.variation_b if version_select == "Version B" else st.session_state.html
        else:
            html_to_show = st.session_state.html

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📋 Copy to Clipboard"):
                st.info("Use the download button to save the HTML file")
        st.code(html_to_show, language='html', line_numbers=True)

    # Edit HTML tab - use correct tab number based on A/B testing
    edit_html_tab = tab4 if st.session_state.ab_testing else tab3
    with edit_html_tab:
        st.subheader("Edit HTML (Advanced)")
        st.warning("⚠️ Advanced feature: Edit the HTML code directly before deploying")

        if st.session_state.ab_testing:
            version_edit = st.radio("Select Version to Edit:", ["Version A", "Version B"], horizontal=True, key="edit_version_select")
            html_to_edit = st.session_state.variation_b if version_edit == "Version B" else st.session_state.html
            edit_key = "html_editor_b" if version_edit == "Version B" else "html_editor_a"
        else:
            html_to_edit = st.session_state.html
            edit_key = "html_editor"

        edited_html = st.text_area(
            "HTML Code",
            value=html_to_edit,
            height=400,
            key=edit_key
        )
        if st.button("💾 Update Preview", type="primary", key=f"update_{edit_key}"):
            if st.session_state.ab_testing and version_edit == "Version B":
                st.session_state.variation_b = edited_html
            else:
                st.session_state.html = edited_html
            st.success("✅ HTML updated! Switch to Preview tab to see changes.")
            st.rerun()

    # Actions
    st.divider()
    st.subheader("Next Steps")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.download_button(
            label="📥 Download HTML",
            data=st.session_state.html,
            file_name=f"landing-{st.session_state.brand}-{datetime.now().strftime('%Y%m%d-%H%M')}.html",
            mime="text/html",
            use_container_width=True,
            type="primary"
        )

    with col2:
        if st.button("🚀 Deploy to Netlify", use_container_width=True):
            st.session_state.show_netlify_form = True

    with col3:
        if st.button("💾 Save to Airtable", use_container_width=True):
            with st.spinner("Saving to Airtable..."):
                result = save_to_airtable({
                    'campaign': st.session_state.intent_raw[:50],
                    'brand': st.session_state.brand_data['name'],
                    'philosophy': st.session_state.philosophy,
                    'style': st.session_state.style,
                    'html': st.session_state.html,
                    'url': st.session_state.get('deployed_url', '')
                })
                if result:
                    st.success("✅ Saved to Airtable!")
                else:
                    st.error("❌ Failed to save to Airtable")

    with col4:
        if st.button("🔄 Start Over", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Netlify deployment form
    if st.session_state.get('show_netlify_form'):
        st.divider()
        st.subheader("Deploy to Netlify")

        default_subdomain = f"{st.session_state.brand}-{datetime.now().strftime('%Y%m%d-%H%M')}"
        subdomain = st.text_input(
            "Choose a subdomain",
            value=default_subdomain,
            help="This will be your site's URL: https://[subdomain].netlify.app"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_netlify_form = False
                st.rerun()

        with col2:
            if st.button("Deploy Now", type="primary", use_container_width=True, disabled=not subdomain):
                with st.spinner("🚀 Deploying to Netlify..."):
                    url = deploy_to_netlify(st.session_state.html, subdomain)
                    if url:
                        st.session_state.deployed_url = url
                        st.success(f"✅ Deployed successfully!")
                        st.markdown(f"**Your landing page is live at:** [{url}]({url})")
                        # Track analytics
                        track_analytics_event("deployed_to_netlify", {"url": url})
                        st.balloons()
                    else:
                        st.error("❌ Deployment failed. Please check your Netlify token and try again.")
                        track_analytics_event("deployment_failed")

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.caption("🚀 Landing Page Generator | Powered by Claude & DALL-E | Built with Streamlit")
