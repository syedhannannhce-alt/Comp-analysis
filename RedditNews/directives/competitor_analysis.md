# Directive: Competitor Analysis

## Goal
Extract structured data from a competitor's website and format it for presentation in PowerPoint (or Google Slides) as part of a standardized competitor analysis module.

## Inputs
1. **Website Link**: The main URL of the competitor.
2. **LLM Ranking & Prompt Used**: How this competitor ranks when manually queried against common customer search prompts in an LLM, and what the prompt was.

## Execution Tools
- **Tool Name**: `competitor_app.py`
- **Location**: `execution/competitor_app.py`
- **Type**: Streamlit Application

## Output Formats
The tool will automatically gather and format the following points into a copy-pasteable structure:
1. Website links
2. Company's base of operations/Headquarters
3. What claim they are giving / how they market themselves
4. Their Unique Selling Proposition (USP)
5. Industry Focus
6. Locations/Global presence
7. Social Media links
8. Blog Posting Frequency

(The LLM ranking is injected based on manual input).

## Instructions for Agent / User
1. Ensure the necessary packages are installed before running:
   ```bash
   pip install streamlit requests beautifulsoup4 google-generativeai python-dotenv
   ```
2. Run the Streamlit application from the terminal:
   ```bash
   python -m streamlit run execution/competitor_app.py
   ```
3. Open the browser window that pops up.
4. Input the `Website Link`.
5. Provide the `LLM Ranking & Prompt Used` manually in the provided text area.
6. Click **Analyze & Generate Slides**.
7. The application will scrape the website and query the active AI endpoint to generate the required fields.
8. Copy and paste the resulting markdown outputs directly into your presentation slides.

## Edge Cases
- **Cannot fetch website**: Some websites block automated scrapers (`requests`). In such cases, the tool gracefully falls back to displaying an error. A future iteration will include a headless browser fallback (e.g. `playwright`).
- **Missing API Key**: The Google Gemini API key must be provided either as a `.env` file in the root directory under `GEMINI_API_KEY` or manually pasted into the app's sidebar.
