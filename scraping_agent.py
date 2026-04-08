from dataclasses import dataclass, field
from typing import Any

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

load_dotenv()


# --- Deps ---

@dataclass
class ScraperDeps:
    massive_token: str
    target_url: str
    additional_instructions: str = ""
    custom_output_schema: dict[str, str] | None = None
    text_limit: int = 10000
    raw_content: list[str] = field(default_factory=list)


# --- Output types ---

class ScrapedResult(BaseModel):
    url: str
    summary: str
    key_facts: list[str]


class ScrapedResultWithCustomOutput(BaseModel):
    url: str
    summary: str
    key_facts: list[str]
    custom_output: list[dict[str, Any]]


# --- Agent factory ---

def _build_agent(use_custom_output: bool) -> Agent:
    output_type = ScrapedResultWithCustomOutput if use_custom_output else ScrapedResult

    base_instructions = (
        "You are a web scraping assistant. "
        "Always respond in English regardless of the page language. "
        "When given a URL, always call the `scrape_website` tool first to fetch the page content. "
        "Then extract a summary and key facts from the page content. "
        "Do NOT include the raw HTML or page source in your response fields."
    )

    return Agent(
        "openai:gpt-4o-mini",
        deps_type=ScraperDeps,
        output_type=output_type,
        instructions=base_instructions,
    )


_agent = _build_agent(use_custom_output=False)
_agent_custom = _build_agent(use_custom_output=True)


# --- Tool (registered on both agents) ---

def _scrape_tool(ctx: RunContext[ScraperDeps]) -> str:
    """Fetch the target URL using the Massive Unblocker API and return page content."""
    response = requests.get(
        "https://unblocker.joinmassive.com/browser",
        params={"url": ctx.deps.target_url},
        headers={"Authorization": f"Bearer {ctx.deps.massive_token}"},
        timeout=(10, 190),
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "head", "noscript", "meta", "link"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    content = text[:ctx.deps.text_limit]
    ctx.deps.raw_content.append(response.text[:4000])
    return content


_agent.tool(_scrape_tool)
_agent_custom.tool(_scrape_tool)


# --- Run helper ---

def run_scrape(
    url: str,
    massive_token: str,
    additional_instructions: str = "",
    custom_output_schema: dict[str, str] | None = None,
    text_limit: int = 10000,
) -> tuple[ScrapedResult | ScrapedResultWithCustomOutput, str]:
    """
    Returns (result, raw_html).
    """
    deps = ScraperDeps(
        massive_token=massive_token,
        target_url=url,
        additional_instructions=additional_instructions,
        custom_output_schema=custom_output_schema,
        text_limit=text_limit,
    )

    # Build the prompt
    prompt_parts = [f"Scrape and analyze this website: {url}"]

    if additional_instructions:
        prompt_parts.append(f"Additional instructions: {additional_instructions}")

    if custom_output_schema:
        schema_desc = "; ".join(f'"{k}": {v}' for k, v in custom_output_schema.items())
        prompt_parts.append(
            f"Populate the custom_output field as a JSON array of objects, each with exactly these keys: {schema_desc}. "
            "If there is only one item, still return a list with one element."
        )

    prompt = "\n\n".join(prompt_parts)

    use_custom = custom_output_schema is not None
    active_agent = _agent_custom if use_custom else _agent

    result = active_agent.run_sync(prompt, deps=deps)
    raw_html = deps.raw_content[0] if deps.raw_content else ""
    return result.output, raw_html
