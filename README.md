# 🕷️ ClawPod — General Purpose Web Scraper Agent

An AI-powered web scraping agent built with [Pydantic AI](https://ai.pydantic.dev/) and the [Massive Unblocker API](https://docs.joinmassive.com/unblocker/browser). Point it at any URL, give it instructions, and get back structured data — no manual parsing required.

---

## DEMO
https://github.com/user-attachments/assets/fa1d5af5-f2a4-4aa2-af92-f3a3a849d97e
---

## What it does

ClawPod takes a URL and optional instructions, fetches the page through the Massive Unblocker, strips all HTML noise, and passes clean text to an LLM. The agent returns a summary, key facts, and optionally a fully custom structured output you define yourself via a JSON schema.

---

## Powered by Massive Unblocker

ClawPod uses the [Massive Unblocker Browser API](https://docs.joinmassive.com/unblocker/browser) to fetch pages — and it's what makes this agent actually work on the modern web.

Most scrapers fail on sites that use:
- **Cloudflare** and other WAF/bot protection layers
- **Anti-bot fingerprinting** (TLS, headers, browser behavior checks)
- **JavaScript rendering** (Next.js, React, Vue SPAs)

Massive Unblocker handles all of that automatically. It runs a real browser in the background, bypasses bot detection, solves challenges, and returns the fully rendered HTML — so the agent sees exactly what a human visitor would see, without any manual configuration.

---

## Features

- Scrape any URL with a single click
- AI-generated summary and key facts in English
- **Additional instructions** — guide the agent on what to focus on
- **Custom output schema** — define your own JSON structure and the agent fills it in, returning a list of objects
- **Configurable character limits** — tune how much content is sent to the AI vs. shown in the raw snippet viewer
- **Raw snippet viewer** — inspect the actual HTML returned by the scraper

---

## Setup

```bash
# Install dependencies
uv sync

# Copy and fill in your env
cp .env.example .env
```

`.env`:
```
MASSIVE_UNBLOCKER_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key_here
```

```bash
# Run the app
uv run streamlit run app.py
```

---

## Custom Output Schema

Enable the toggle in the UI and provide a JSON object where keys are field names and values describe what to extract:

```json
{
  "title": "job title",
  "city": "city of the salary listing",
  "salary": "monthly salary amount"
}
```

The agent will return a list of objects matching that schema — one item if only one match is found, multiple if there are many.

---

## Stack

- [Pydantic AI](https://ai.pydantic.dev/) — agent framework
- [Massive Unblocker](https://docs.joinmassive.com/unblocker/browser) — browser-grade scraping API
- [Streamlit](https://streamlit.io/) — UI
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — HTML cleaning
