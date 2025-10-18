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

def parse_intent(user_input):
    """Parse user intent using Claude API"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            st.error("ANTHROPIC_API_KEY environment variable not set")
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

def generate_landing_page(brand, philosophy, style, cta, intent):
    """Generate landing page HTML using Claude API"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            st.error("ANTHROPIC_API_KEY environment variable not set")
            return "<html><body><h1>Error: API key missing</h1></body></html>"

        client = Anthropic(api_key=api_key)

        # Load philosophy details
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
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            st.error("OPENAI_API_KEY environment variable not set")
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
        netlify_token = os.getenv('NETLIFY_TOKEN')
        if not netlify_token:
            st.error("NETLIFY_TOKEN environment variable not set")
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
st.markdown("### Progress")
cols = st.columns(7)
steps = ["Intent", "Brand", "Philosophy", "Style", "CTAs", "Media", "Generate"]
for i, (col, step_name) in enumerate(zip(cols, steps)):
    with col:
        if i + 1 < st.session_state.step:
            st.success(f"✅ {step_name}")
        elif i + 1 == st.session_state.step:
            st.info(f"➡️ {step_name}")
        else:
            st.text(f"⭕ {step_name}")

st.divider()

# ============================================================================
# STEP 1: INTENT CAPTURE
# ============================================================================
if st.session_state.step == 1:
    st.markdown('<div class="main-header">🚀 Landing Page Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Create professional landing pages in minutes with AI</div>', unsafe_allow_html=True)
    st.markdown("### 💭 What are you looking to create today?")

    with st.expander("💡 Need inspiration? See examples"):
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

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Continue →", type="primary", disabled=not user_input, use_container_width=True):
            with st.spinner("🤔 Understanding your goal..."):
                st.session_state.intent = parse_intent(user_input)
                st.session_state.intent_raw = user_input
                st.session_state.step = 2
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

                color_cols = st.columns(3)
                for i, (color_name, color_value) in enumerate(list(brand['colors'].items())[:3]):
                    with color_cols[i]:
                        st.color_picker(
                            color_name.title(),
                            color_value,
                            disabled=True,
                            key=f"c_{brand_id}_{i}",
                            label_visibility="collapsed"
                        )
                        st.caption(color_name.title())

                if st.button(f"Select {brand['name']}", key=brand_id, use_container_width=True, type="primary"):
                    st.session_state.brand = brand_id
                    st.session_state.brand_data = brand
                    st.session_state.step = 3
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

    cols = st.columns(2)
    for idx, (style_id, style) in enumerate(styles.items()):
        with cols[idx % 2]:
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.subheader(f"{style['emoji']} {style['name']}")
            st.markdown(f"**{style['desc']}**")
            st.caption(style['characteristics'])
            if st.button(f"Select", key=style_id, use_container_width=True, type="primary"):
                st.session_state.style = style_id
                st.session_state.step = 5
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    if st.button("← Back to Philosophy"):
        st.session_state.step = 3
        st.rerun()

# ============================================================================
# STEP 5: CTA CONFIGURATION
# ============================================================================
elif st.session_state.step == 5:
    st.markdown('<div class="main-header">Configure Call-to-Action</div>', unsafe_allow_html=True)
    st.caption(f"Brand: {st.session_state.brand_data['name']} | Style: {st.session_state.style}")

    brand = st.session_state.brand_data
    phil = st.session_state.philosophy

    # Default CTA based on philosophy
    if phil == 'assessment-funnel':
        default_text = "Take the Free Assessment"
        default_url = brand['ctas']['top']['url']
    else:
        default_text = brand['ctas']['middle']['text']
        default_url = brand['ctas']['middle']['url']

    st.subheader("Primary Call-to-Action")
    col1, col2 = st.columns(2)

    with col1:
        cta_text = st.text_input("CTA Button Text", value=default_text, key="cta_text_input")

    with col2:
        cta_url = st.text_input("CTA URL", value=default_url, key="cta_url_input")

    # Preview
    st.markdown("**Preview:**")
    preview_color = brand['colors']['primary']
    st.markdown(
        f'<a href="#" style="background-color: {preview_color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 600;">{cta_text}</a>',
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("Secondary Call-to-Action (Optional)")
    include_secondary = st.checkbox("Add secondary CTA?", key="secondary_cta_checkbox")

    if include_secondary:
        col1, col2 = st.columns(2)
        with col1:
            sec_text = st.text_input("Secondary CTA Text", value="Learn More", key="sec_cta_text")
        with col2:
            sec_url = st.text_input("Secondary URL", value=brand['website'], key="sec_cta_url")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Style"):
            st.session_state.step = 4
            st.rerun()

    with col2:
        if st.button("Continue →", type="primary", disabled=not (cta_text and cta_url), use_container_width=True):
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
# STEP 7: GENERATE & PREVIEW
# ============================================================================
elif st.session_state.step == 7:
    st.markdown('<div class="main-header">Generate Your Landing Page</div>', unsafe_allow_html=True)

    # Generate if not already generated
    if not st.session_state.get('html'):
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Generate HTML
        status_text.text("🎨 Generating your landing page HTML...")
        progress_bar.progress(25)

        html = generate_landing_page(
            brand=st.session_state.brand_data,
            philosophy=st.session_state.philosophy,
            style=st.session_state.style,
            cta=st.session_state.cta,
            intent=st.session_state.intent_raw
        )
        st.session_state.html = html
        progress_bar.progress(50)

        # Generate media if requested
        if st.session_state.media.get('generate_image'):
            status_text.text("🖼️ Generating hero image with DALL-E 3...")
            progress_bar.progress(75)
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

        progress_bar.progress(100)
        status_text.text("✅ Landing page generated successfully!")

    st.success("✅ Your landing page is ready!")

    # Show generated image if available
    if st.session_state.get('generated_image'):
        with st.expander("🖼️ Generated Hero Image", expanded=False):
            st.image(st.session_state.generated_image, caption="AI-Generated Hero Image")
            st.caption("This image has been generated and can be downloaded or used in your landing page.")

    # Preview tabs
    tab1, tab2, tab3 = st.tabs(["👁️ Live Preview", "💻 HTML Code", "✏️ Edit HTML"])

    with tab1:
        st.subheader("Preview Your Landing Page")

        # Preview mode toggle
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        with col1:
            if st.button("📱 Mobile", use_container_width=True, type="primary" if st.session_state.preview_mode == 'mobile' else "secondary"):
                st.session_state.preview_mode = 'mobile'
                st.rerun()
        with col2:
            if st.button("💻 Desktop", use_container_width=True, type="primary" if st.session_state.preview_mode == 'desktop' else "secondary"):
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

    with tab2:
        st.subheader("HTML Source Code")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📋 Copy to Clipboard"):
                st.info("Use the download button to save the HTML file")
        st.code(st.session_state.html, language='html', line_numbers=True)

    with tab3:
        st.subheader("Edit HTML (Advanced)")
        st.warning("⚠️ Advanced feature: Edit the HTML code directly before deploying")
        edited_html = st.text_area(
            "HTML Code",
            value=st.session_state.html,
            height=400,
            key="html_editor"
        )
        if st.button("💾 Update Preview", type="primary"):
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
                        st.balloons()
                    else:
                        st.error("❌ Deployment failed. Please check your Netlify token and try again.")

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.caption("🚀 Landing Page Generator | Powered by Claude & DALL-E | Built with Streamlit")
