# Scraper Hub Intelligence -- Complete API Developer Guide
==========================================================
Version: 1.0  |  Base URL: http://localhost:8000
Swagger UI:   http://localhost:8000/docs
OpenAPI JSON: http://localhost:8000/openapi.json

==============================================================
SECTION 1 -- FOR AI CODING ASSISTANTS
(Cursor, GitHub Copilot, Gemini Code, ChatGPT with Code Plugin)
==============================================================

## System Prompt Context (copy into your AI session)

"I am building integrations for Scraper Hub, a market intelligence scraping platform.
Base URL: http://localhost:8000
OpenAPI schema is available at http://localhost:8000/openapi.json.

Endpoints I care about:
- POST /api/v1/manual-scrape/   -- trigger real-time extraction
- GET  /api/v1/records/         -- fetch structured price records
- GET  /api/v1/sources/         -- list configured source URLs
- POST /api/v1/webhook-targets/ -- subscribe to real-time updates"

## Trigger a Scrape (Python)

    import httpx

    resp = httpx.post(
        "http://localhost:8000/api/v1/manual-scrape/",
        json={
            "url": "https://www.econet.co.zw/usd-data-bundles",
            "category": "telecoms",
            "extractor_type": "auto",
            "store_result": True
        },
        timeout=90
    )
    print(resp.json())

## Read Back Records (Python)

    import httpx

    records = httpx.get(
        "http://localhost:8000/api/v1/records/",
        params={"category": "telecoms", "limit": 20}
    ).json()

    for r in records:
        print(r["entity_name"], r["title"], r["price_currency"], r["price_value"])

## AI Tip: Auto-Generate Typed Client

Paste the full OpenAPI schema into your AI assistant:
    curl http://localhost:8000/openapi.json

Then ask: "Generate a fully typed Python httpx client from this OpenAPI schema."


==============================================================
SECTION 2 -- FOR AUTONOMOUS AGENTS
(LangChain, CrewAI, OpenAI Agents SDK, AutoGPT, Phidata)
==============================================================

## Step 1 -- Define Scraper Hub as Agent Tools (LangChain)

    from langchain.tools import tool
    import httpx

    BASE = "http://localhost:8000"

    @tool
    def scrape_url(url: str, category: str = "auto") -> dict:
        """Trigger real-time price and product intelligence extraction.
        Args:
            url:      Target page URL (e.g. 'https://econet.co.zw/usd-data-bundles')
            category: Sector (telecoms, banking, insurance, retail, transport)
        """
        return httpx.post(
            f"{BASE}/api/v1/manual-scrape/",
            json={"url": url, "category": category, "extractor_type": "auto"},
            timeout=90
        ).json()

    @tool
    def get_records(category: str = None, market: str = None, limit: int = 50) -> list:
        """Fetch stored intelligence records.
        Args:
            category: Filter by sector (optional)
            market:   Filter by market geography (optional)
            limit:    Max records to return (default 50)
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        if market:
            params["market"] = market
        return httpx.get(f"{BASE}/api/v1/records/", params=params).json()

    @tool
    def list_sources() -> list:
        """Get all configured crawling sources -- URLs, categories, and schedules.
        Use this to know what sources are available before choosing a URL to scrape."""
        return httpx.get(f"{BASE}/api/v1/sources/").json()

    @tool
    def get_organizations(category: str = None, search: str = None) -> list:
        """Browse the registry of tracked institutional entities."""
        params = {}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        return httpx.get(f"{BASE}/api/v1/organizations/", params=params).json()

    @tool
    def subscribe_webhook(callback_url: str, name: str = "Agent Hook") -> dict:
        """Subscribe your agent to real-time notifications when new records are scraped."""
        return httpx.post(f"{BASE}/api/v1/webhook-targets/", json={
            "name": name,
            "url": callback_url,
            "is_active": True
        }).json()

## Step 2 -- Initialize and Run the Agent

    from langchain.agents import initialize_agent, AgentType
    from langchain.chat_models import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    tools = [scrape_url, get_records, list_sources, get_organizations]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )
    agent.run("Scrape the latest Econet Zimbabwe USD data bundle prices and summarise them.")

## Step 3 -- CrewAI Example

    from crewai import Agent, Task, Crew

    scraper_agent = Agent(
        role="Market Intelligence Collector",
        goal="Extract and store the latest institutional pricing data from Zimbabwe",
        tools=[scrape_url, list_sources],
        verbose=True
    )

    task = Task(
        description="Scrape Econet, NetOne, and Telecel Zimbabwe for latest USD data bundle prices.",
        agent=scraper_agent,
        expected_output="Structured JSON list of all extracted pricing records."
    )

    crew = Crew(agents=[scraper_agent], tasks=[task])
    crew.kickoff()

## Recommended Agent Boot Sequence

1. GET  /api/v1/sources/        -- discover available sources and categories
2. GET  /api/v1/health/         -- confirm platform is healthy
3. POST /api/v1/manual-scrape/  -- trigger scrapes for target URLs
4. GET  /api/v1/records/        -- retrieve structured results
5. POST /api/v1/webhook-targets/ -- subscribe for future real-time updates


==============================================================
SECTION 3 -- COMPLETE API ENDPOINT REFERENCE
==============================================================

Core Intelligence APIs (v1)

  Method  Endpoint                           Description
  ------  ---------------------------------  ------------------------------------
  GET     /api/v1/records/                   Fetch extracted price/product records
  POST    /api/v1/manual-scrape/             Trigger real-time scraping
  GET     /api/v1/sources/                   List all configured sources
  POST    /api/v1/sources/                   Register a new source
  GET     /api/v1/sources/{id}/              Get single source details
  PUT     /api/v1/sources/{id}/              Update a source
  DELETE  /api/v1/sources/{id}/              Remove a source
  GET     /api/v1/organizations/             Browse tracked institutions
  GET     /api/v1/organizations/{slug}/      Get institution profile and changes
  GET     /api/v1/webhook-targets/           List webhook subscriptions
  POST    /api/v1/webhook-targets/           Subscribe to real-time events
  DELETE  /api/v1/webhook-targets/{id}/      Remove a webhook subscription
  GET     /api/v1/delivery-attempts/         Inspect webhook delivery logs
  GET     /api/v1/health/                    Liveness health check

Market Data APIs (v2)

  Method  Endpoint                  Description
  ------  ------------------------  --------------------------
  GET     /api/v2/market-data/      Live exchange rates and metrics

Data Export Endpoints

  Method  Endpoint             Format  Description
  ------  -------------------  ------  ---------------------------
  GET     /export/records      .xlsx   Download all records as Excel
  GET     /export/api-docs     .md     Download this guide


==============================================================
SECTION 4 -- REQUEST / RESPONSE SCHEMAS
==============================================================

POST /api/v1/manual-scrape/ -- Request Body

  url             string   (required) Target URL to scrape
  category        string   (required) Sector: telecoms|banking|insurance|retail|transport
  extractor_type  string   (optional) auto|generic|telecom|banking  (default: auto)
  store_result    boolean  (optional) Persist to DB? (default: true)

GET /api/v1/records/ -- Query Parameters

  category  string   Filter by sector
  market    string   Filter by geography
  limit     integer  Max records (default 50)
  offset    integer  Pagination offset

GET /api/v1/records/ -- Response Item Schema

  id               integer
  entity_name      string    e.g. "Econet Wireless"
  category         string    e.g. "telecoms"
  subcategory      string    e.g. "mobile_data"
  title            string    e.g. "Private Bundle 50GB"
  description      string
  price_value      float     e.g. 45.0
  price_currency   string    e.g. "USD"
  unit_value       float     e.g. 50.0
  unit_type        string    e.g. "GB"
  billing_period   string    e.g. "monthly"
  confidence_score float     0.0 to 1.0
  source_url       string
  captured_at      datetime  ISO 8601
