import os
import json

import streamlit as st
from dotenv import load_dotenv

from scraping_agent import run_scrape

load_dotenv()

st.set_page_config(page_title="Web Scraper Agent with ClawPod", page_icon="🕷️", layout="centered")
st.title("🕷️ Web Scraper Agent with ClawPod")
st.caption("Powered by Pydantic AI + Massive Unblocker")

with st.form("scrape_form"):
    url = st.text_input("URL to scrape", placeholder="https://example.com")
    token = st.text_input(
        "Massive Unblocker Token",
        value=os.getenv("MASSIVE_UNBLOCKER_TOKEN", ""),
        type="password",
    )

    additional_instructions = st.text_area(
        "Additional instructions (optional)",
        placeholder="e.g. Focus on pricing information, ignore navigation menus...",
        height=80,
    )

    text_limit = st.number_input(
        "Extracted text limit (chars)",
        min_value=1000,
        max_value=50000,
        value=10000,
        step=1000,
        help="Max characters of cleaned page text sent to the AI.",
    )
    if text_limit > 20000:
        st.warning("⚠️ High text limit: the AI will consume significantly more tokens, which may increase cost and latency.")

    submitted = st.form_submit_button("Scrape", use_container_width=True)

# Custom output schema toggle lives outside the form so the textarea can appear conditionally
custom_output_enabled = st.toggle("Enable custom output schema")
custom_schema_input = ""
if custom_output_enabled:
    custom_schema_input = st.text_area(
        "Custom output schema (JSON object: field name → description)",
        placeholder='{"title": "page title", "price": "product price if any", "author": "author name"}',
        height=100,
    )

if submitted:
    if not url:
        st.error("Please enter a URL.")
    elif not token:
        st.error("Please provide a Massive Unblocker token.")
    else:
        custom_output_schema = None
        if custom_output_enabled:
            if not custom_schema_input.strip():
                st.error("Please enter a custom output schema or disable that option.")
                st.stop()
            try:
                custom_output_schema = json.loads(custom_schema_input)
                if not isinstance(custom_output_schema, dict):
                    raise ValueError("Schema must be a JSON object.")
            except (json.JSONDecodeError, ValueError) as e:
                st.error(f"Invalid schema JSON: {e}")
                st.stop()

        with st.spinner("Scraping..."):
            try:
                result, raw_html = run_scrape(
                    url=url,
                    massive_token=token,
                    additional_instructions=additional_instructions,
                    custom_output_schema=custom_output_schema,
                    text_limit=int(text_limit),
                )

                st.success("Done!")

                st.subheader("Summary")
                st.write(result.summary)

                st.subheader("Key Facts")
                for fact in result.key_facts:
                    st.markdown(f"- {fact}")

                if custom_output_enabled and hasattr(result, "custom_output") and result.custom_output:
                    st.subheader("Custom Output")
                    st.json(result.custom_output)

                with st.expander("See raw snippet"):
                    st.code(raw_html, language="html")

            except Exception as e:
                st.error(f"Error: {e}")
