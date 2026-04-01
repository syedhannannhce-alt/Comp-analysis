import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
import re

# Use Google Gemini OR OpenAI API for extraction depending on what's available
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Competitor Analysis Tool", page_icon="🕵️", layout="wide")

st.title("Automated Competitor Analysis PPT Builder")
st.markdown("Enter a competitor's website, provide your LLM ranking manually, and let AI extract the rest to generate a structure ready for your PowerPoint slides.")

# Sidebar for Setup
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key_env = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.text_input("Gemini API Key", value=api_key_env, type="password", help="Get your API key from Google AI Studio")
    if api_key:
        if HAS_GENAI:
            genai.configure(api_key=api_key)
        else:
            st.error("Please ensure the 'google-generativeai' python package is installed.")
            
    st.markdown("---")
    st.markdown("**Required Packages:**")
    st.code("pip install streamlit requests beautifulsoup4 google-generativeai python-dotenv", language="bash")

# Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Inputs")
    website_url = st.text_input("1. Website Link", placeholder="https://www.competitor.com")
    llm_ranking = st.text_area("3. LLM Ranking & Prompt Used (Manual)", placeholder="e.g. Prompt: 'What is the top auto CRM?'\\nRanking: Came 3rd on ChatGPT")
    
    analyze_btn = st.button("🚀 Analyze & Generate Slides", type="primary", use_container_width=True)

with col2:
    st.header("📊 Scraped Data preview")
    scrape_status = st.empty()

# Helper Functions
def scrape_website(url):
    """Basic extraction of a website's text and social links"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Give more weight to certain tags
        text_elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'span', 'a'])
        texts = [elem.get_text(strip=True) for elem in text_elements if elem.get_text(strip=True)]
        
        # Remove empty or super short strings
        cleaned_texs = [t for t in texts if len(t) > 10]
        
        # Join limiting to ~15000 chars to avoid massive LLM context
        website_content = " \\n ".join(cleaned_texs)[:15000]
        
        # Specifically look for social media links
        social_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if any(social in href.lower() for social in ['linkedin.com', 'twitter.com', 'x.com', 'facebook.com', 'instagram.com', 'youtube.com', 'medium.com']):
                social_links.append(href)
                
        return {"content": website_content, "socials": list(set(social_links))}
    except Exception as e:
        return {"error": str(e)}

def extract_details_with_ai(content, socials):
    """Use Gemini to extract structured info from the text"""
    if not api_key:
        return {"error": "API Key is missing. Please provide it in the sidebar."}
        
    prompt = f"""
    You are an expert market researcher. I have scraped the text and links from a competitor's website.
    Please analyze the text and extract the following specific bullet points. 
    If a bullet point cannot be definitively answered from the text, make a best educated guess or state "Not explicitly mentioned, likely [Guess]".

    Website Social Links Found: {', '.join(socials)}

    Extract the following details:
    1. Where the company is based out of (Headquarters/Location)
    2. What claim they are giving / what they market themselves as (e.g. AI Assistant, Dealership Agent)
    3. What is their USP (Unique Selling Proposition)
    4. What is their industry (e.g. Auto Specific, Generic B2B, etc.)
    5. Where are they globally present (Countries/Regions)
    6. What social media do they use (List the platforms implicitly or explicitly found)
    7. How often they post blogs (Look for blog dates or frequency mention, if impossible state 'Cannot determine from homepage alone')

    Website Text Dump:
    {content}

    Output valid JSON in EXACTLY this structure:
    {{
        "location": "",
        "claim": "",
        "usp": "",
        "industry": "",
        "presence": "",
        "social_media": "",
        "blog_frequency": ""
    }}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest' if '1.5' in genai.__version__ or True else 'gemini-pro')
        # Gemini setup
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
        response = model.generate_content(prompt, generation_config=generation_config)
        return json.loads(response.text)
    except Exception as e:
        # Fallback without json mime type enforcement for older SDKs
        try:
             model = genai.GenerativeModel('gemini-pro')
             response = model.generate_content(prompt + " Only output the RAW JSON block without markdown ticks.")
             text = response.text.strip('`').replace('json', '').strip()
             return json.loads(text)
        except Exception as inner_e:
             return {"error": f"LLM Generation Failed. Error: {str(inner_e)}"}


if analyze_btn:
    if not website_url:
        st.error("Please provide a website URL.")
    elif not HAS_GENAI:
        st.error("Please install the google-generativeai package (see sidebar).")
    else:
        st.markdown("---")
        st.header("📋 Generated Presentation Structure")
        
        with col2:
            scrape_status.info(f"Scraping '{website_url}'...")
            scraped_data = scrape_website(website_url)
            
            if "error" in scraped_data:
                scrape_status.error(f"Failed to scrape website: {scraped_data['error']}")
                st.stop()
            else:
                scrape_status.success(f"Successfully scraped {len(scraped_data['content'])} characters and {len(scraped_data['socials'])} social links.")
                with st.expander("View Raw Text"):
                    st.write(scraped_data['content'][:2000] + "...")
        
        with st.spinner("Extracting insights with AI..."):
            extracted = extract_details_with_ai(scraped_data['content'], scraped_data['socials'])
        
        if "error" in extracted:
            st.error(extracted["error"])
        else:
            # Format outputs for PPT copy pasting
            st.success("Analysis Complete! Copy the sections below into your PPT slides.")
            
            # --- PPT Slide 1 ---
            st.subheader("Slide 1: Overview & Performance")
            slide_1_content = f"""
**Company:** {website_url.replace("https://", "").replace("http://", "").split('/')[0]}
**Location / HQ:** {extracted.get('location', 'N/A')}
**Global Presence:** {extracted.get('presence', 'N/A')}
**Industry:** {extracted.get('industry', 'N/A')}

**LLM Performance & Methodology:**
{llm_ranking if llm_ranking else '*No manual ranking provided*'}
            """.strip()
            st.code(slide_1_content, language="markdown")
            
            # --- PPT Slide 2 ---
            st.subheader("Slide 2: Marketing & Go-To-Market")
            slide_2_content = f"""
**Core Claim / Marketing Message:**
- {extracted.get('claim', 'N/A')}

**Unique Selling Proposition (USP):**
- {extracted.get('usp', 'N/A')}

**Social Media Presence:**
- {extracted.get('social_media', 'N/A')}
- Relevant Links: {", ".join(scraped_data.get('socials', []))}

**Content Strategy (Blog Frequency):**
- {extracted.get('blog_frequency', 'N/A')}
            """.strip()
            st.code(slide_2_content, language="markdown")
