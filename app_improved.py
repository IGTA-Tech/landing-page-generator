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
if 'fullscreen_preview' not in st.session_state:
    st.session_state.fullscreen_preview = False
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

# ============================================================================
# MODERN CSS STYLING
# ============================================================================
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Main header styling */
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

    /* Step cards with modern design */
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

    .progress-complete {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .progress-current {
        background: #fff;
        color: #667eea;
        border: 2px solid #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }

    .progress-pending {
        background: #f8f9fa;
        color: #aaa;
    }

    /* Preview container */
    .preview-container {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border: 2px solid #f0f0f0;
    }

    .preview-controls {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    .preview-device-frame {
        margin: 0 auto;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 0 40px rgba(0,0,0,0.15);
    }

    /* Mobile frame */
    .mobile-frame {
        max-width: 375px;
        margin: 2rem auto;
        border: 12px solid #1f1f1f;
        border-radius: 36px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        background: #1f1f1f;
    }

    .mobile-frame .preview-screen {
        border-radius: 24px;
        overflow: hidden;
    }

    /* Desktop frame */
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
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
        border: none;
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

    /* Demo mode badge */
    .demo-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }

    /* Success messages */
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 8px 24px rgba(17, 153, 142, 0.3);
    }

    /* Philosophy cards */
    .philosophy-card {
        padding: 1.5rem;
        border-radius: 12px;
        background: white;
        border: 2px solid #f0f0f0;
        transition: all 0.3s;
        cursor: pointer;
    }

    .philosophy-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
    }
</style>
""", unsafe_allow_html=True)

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

def get_demo_html(brand, philosophy, style, cta, intent):
    """Generate demo HTML when in demo mode"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand['name']} - Landing Page</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        header {{
            background: linear-gradient(135deg, {brand['colors']['primary']} 0%, {brand['colors']['secondary']} 100%);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{
            max-height: 50px;
        }}
        .hero {{
            text-align: center;
            padding: 80px 20px;
            background: linear-gradient(135deg, {brand['colors']['primary']}10 0%, {brand['colors']['secondary']}10 100%);
        }}
        .hero h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
            color: {brand['colors']['primary']};
        }}
        .hero p {{
            font-size: 1.25rem;
            color: #666;
            max-width: 600px;
            margin: 0 auto 2rem;
        }}
        .cta-button {{
            display: inline-block;
            background: {brand['colors']['primary']};
            color: white;
            padding: 1rem 2rem;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }}
        .features {{
            padding: 60px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }}
        .feature-card {{
            padding: 2rem;
            border-radius: 12px;
            background: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 4px solid {brand['colors']['accent']};
        }}
        .feature-card h3 {{
            color: {brand['colors']['primary']};
            margin-bottom: 1rem;
        }}
        footer {{
            background: #1a1a1a;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 4rem;
        }}
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2rem; }}
            .feature-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <header>
        <img src="{brand['logo']}" alt="{brand['name']}" class="logo">
        <nav>
            <a href="{brand['website']}" style="color: white; text-decoration: none; font-weight: 600;">Visit Website</a>
        </nav>
    </header>

    <section class="hero">
        <h1>Transform Your Future Today</h1>
        <p>{intent[:200]}...</p>
        <a href="{cta['primary']['url']}" class="cta-button">{cta['primary']['text']}</a>
    </section>

    <section class="features">
        <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 1rem; color: {brand['colors']['primary']};">Why Choose Us?</h2>
        <div class="feature-grid">
            <div class="feature-card">
                <h3>Expert Guidance</h3>
                <p>Our team of professionals brings years of experience to help you achieve your goals.</p>
            </div>
            <div class="feature-card">
                <h3>Proven Results</h3>
                <p>Hundreds of successful clients have transformed their situation with our help.</p>
            </div>
            <div class="feature-card">
                <h3>Personalized Approach</h3>
                <p>We understand every situation is unique and tailor our solutions to your needs.</p>
            </div>
        </div>
    </section>

    <section class="hero">
        <h2 style="font-size: 2rem; margin-bottom: 1rem;">Ready to Get Started?</h2>
        <a href="{cta['primary']['url']}" class="cta-button">{cta['primary']['text']}</a>
    </section>

    <footer>
        <p>&copy; 2025 {brand['name']}. All rights reserved.</p>
        <p style="margin-top: 0.5rem; opacity: 0.8;">Generated with Landing Page Generator</p>
    </footer>
</body>
</html>"""

def parse_intent(user_input):
    """Parse user intent using Claude API or demo mode"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            st.session_state.demo_mode = True
            return f"""**Demo Mode Analysis**

Campaign Type: Lead Generation
Target Audience: Professionals seeking specialized services
Primary Objective: Capture qualified leads and build trust
Suggested Approach: Assessment-driven funnel with strong social proof

*Note: Running in demo mode. Set ANTHROPIC_API_KEY for AI-powered analysis.*"""

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
        st.session_state.demo_mode = False
        return response.content[0].text
    except Exception as e:
        st.session_state.demo_mode = True
        return f"**Demo Mode** (Error: {str(e)[:50]}...)\n\nCampaign analysis will be generated in demo mode."

def generate_landing_page(brand, philosophy, style, cta, intent):
    """Generate landing page HTML using Claude API or demo mode"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or st.session_state.demo_mode:
            return get_demo_html(brand, philosophy, style, cta, intent)

        client = Anthropic(api_key=api_key)
        phil_data = load_philosophy()
        phil_info = phil_data.get(philosophy, {})

        prompt = f"""Create a complete, production-ready HTML landing page with inline CSS and JavaScript.

BRAND INFORMATION:
- Brand Name: {brand['name']}
- Logo URL: {brand['logo']}
- Primary Color: {brand['colors']['primary']}
- Secondary Color: {brand['colors']['secondary']}
- Accent Color: {brand['colors']['accent']}
- Website: {brand['website']}

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
        if '```html' in html:
            html = html.split('```html')[1].split('```')[0]
        elif '```' in html:
            html = html.split('```')[1].split('```')[0]

        return html.strip()
    except Exception as e:
        st.warning(f"API Error: {str(e)[:100]}... Switching to demo mode.")
        st.session_state.demo_mode = True
        return get_demo_html(brand, philosophy, style, cta, intent)

def generate_image(brand, intent, style):
    """Generate hero image using DALL-E or return placeholder"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or st.session_state.demo_mode:
            return f"https://via.placeholder.com/1792x1024/{brand['colors']['primary'][1:]}/ffffff?text={brand['name']}+Hero+Image"

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
        st.warning(f"Image generation unavailable: {str(e)[:50]}...")
        return f"https://via.placeholder.com/1792x1024/{brand['colors']['primary'][1:]}/ffffff?text={brand['name']}+Hero+Image"

def deploy_to_netlify(html, subdomain):
    """Deploy HTML to Netlify"""
    try:
        netlify_token = os.getenv('NETLIFY_TOKEN')
        if not netlify_token:
            st.error("NETLIFY_TOKEN environment variable not set")
            return None

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('index.html', html)
        zip_buffer.seek(0)

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
        airtable_key = os.getenv('AIRTABLE_API_KEY')
        base_id = os.getenv('AIRTABLE_BASE_ID')

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
                "HTML": data['html'][:100000],
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

def create_download_link(html, filename):
    """Create download link for HTML"""
    b64 = base64.b64encode(html.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" style="text-decoration: none;"><button style="background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer;">📥 Download HTML</button></a>'

# ============================================================================
# PROGRESS INDICATOR (MODERN)
# ============================================================================
st.markdown("### 🚀 Your Progress")
cols = st.columns(7)
steps = [
    ("Intent", "🎯"),
    ("Brand", "🎨"),
    ("Philosophy", "📊"),
    ("Style", "✨"),
    ("CTAs", "🔗"),
    ("Media", "🖼️"),
    ("Generate", "⚡")
]

for i, (col, (step_name, emoji)) in enumerate(zip(cols, steps)):
    with col:
        if i + 1 < st.session_state.step:
            st.markdown(f'<div class="progress-step progress-complete">{emoji}<br/>{step_name}</div>', unsafe_allow_html=True)
        elif i + 1 == st.session_state.step:
            st.markdown(f'<div class="progress-step progress-current">{emoji}<br/>{step_name}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="progress-step progress-pending">{emoji}<br/>{step_name}</div>', unsafe_allow_html=True)

st.divider()

# Show demo mode indicator if active
if st.session_state.demo_mode:
    st.markdown('<div class="demo-badge">🎭 DEMO MODE - Set API keys for AI generation</div>', unsafe_allow_html=True)
    st.info("💡 Running in demo mode with pre-built templates. Set ANTHROPIC_API_KEY and OPENAI_API_KEY environment variables for full AI-powered generation.")
    st.divider()

# ============================================================================
# STEP 1: INTENT CAPTURE
# ============================================================================
if st.session_state.step == 1:
    st.markdown('<div class="main-header">🚀 Landing Page Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Create professional landing pages in minutes with AI</div>', unsafe_allow_html=True)

    with st.expander("💡 Need inspiration? See examples", expanded=False):
        st.markdown("""
        **Example requests:**
        - "Landing page for free O-1 visa webinar to capture athlete emails"
        - "Conversion page for automation service targeting small businesses"
        - "Lead magnet for immigration law firm offering visa assessment"
        - "Product launch page for SaaS tool with free trial offer"
        - "Event registration page for legal tech conference"
        """)

    user_input = st.text_area(
        "Describe your goal:",
        height=150,
        placeholder="Example: I need a landing page that helps athletes understand O-1 visa eligibility and captures their email for a free consultation.",
        key="intent_input"
    )

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Continue →", type="primary", disabled=not user_input, use_container_width=True):
            with st.spinner("🤔 Understanding your goal..."):
                st.session_state.intent = parse_intent(user_input)
                st.session_state.intent_raw = user_input
                st.session_state.step = 2
                st.rerun()

# Continue with other steps... (I'll add them in the next part due to length)
# Let me know if you want me to continue with the remaining steps!
