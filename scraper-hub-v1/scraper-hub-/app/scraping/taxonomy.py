# Standard Taxonomy for Products and Services
# Based on the Comparison Table provided by the user

TAXONOMY = {
    "DATA": {
        "subcategories": {
            "Data bundle": {"unit": "$/MB", "compare": "Econet v NetOne", "formula": "price / MB"},
            "Data bundle (GB)": {"unit": "$/GB", "compare": "Cost per 1GB", "formula": "price / GB"},
            "Night data": {"unit": "$/GB off-peak", "compare": "$1.22 per 1GB night bundle", "formula": "price / GB"},
            "Streaming bundle": {"unit": "$/hour", "compare": "$1.43 per 1 hour video", "formula": "price / duration"},
            "Out of bundle": {"unit": "$/MB", "compare": "Raw excess rate", "formula": "price / MB"},
            "Social bundles": {"unit": "$/app/day", "compare": "WhatsApp/Facebook/TikTok", "formula": "price / app / period"},
            "Unlimited Bundles": {"unit": "Mbps + FUP", "compare": "Fair usage plans", "formula": "bandwidth + cap"},
        }
    },
    "VOICE": {
        "subcategories": {
            "On-net calls": {"unit": "$/min", "compare": "Econet -> Econet", "formula": "cost / min"},
            "Off-net calls": {"unit": "$/min", "compare": "Econet -> NetOne/Telecel", "formula": "cost / min"},
            "International calls": {"unit": "$/min", "compare": "Per country rates", "formula": "cost / min"},
            "All Net Tariffs": {"unit": "$/min", "compare": "Flat pricing", "formula": "cost / min"},
            "Bundle Voice": {"unit": "$/100 mins", "compare": "$1.52 per 100 minutes", "formula": "price / minutes"},
        }
    },
    "SMS": {
        "subcategories": {
            "Local SMS": {"unit": "$/SMS", "compare": "Standard SMS", "formula": "price / count"},
            "Bulk SMS": {"unit": "$/100 SMS", "compare": "$1 per 100 SMS", "formula": "price / count"},
            "International SMS": {"unit": "$/SMS", "compare": "Global SMS", "formula": "price / count"},
        }
    },
    "INTERNET": {
        "subcategories": {
            "Fibre Internet": {"unit": "Mbps", "compare": "Home Fibre", "formula": "price / bandwidth"},
            "Wireless Internet": {"unit": "Mbps + GB", "compare": "LTE/WiMAX", "formula": "price / (bandwidth + data)"},
            "Dedicated Internet": {"unit": "Mbps", "compare": "Enterprise leased line", "formula": "price / bandwidth"},
            "Installation fees": {"unit": "$/installation", "compare": "Once-off cost", "formula": "fixed cost"},
            "Router/Modem Costs": {"unit": "$/device", "compare": "Device costs", "formula": "fixed cost"},
            "Subscriptions": {"unit": "$/month", "compare": "Monthly retainers", "formula": "fixed cost / month"},
        }
    },
    "BANKING": {
        "subcategories": {
            "Current Account": {"unit": "$/month", "compare": "Account maintenance", "formula": "price / month"},
            "Savings Account": {"unit": "$/year", "compare": "Savings product", "formula": "price / year"},
            "Cash Withdrawal": {"unit": "$/transaction", "compare": "ATM/branch withdrawals", "formula": "fixed cost"},
            "Bank Transfer": {"unit": "$/transaction", "compare": "RTGS/EFT transfers", "formula": "fixed cost"},
            "Internet Banking": {"unit": "$/month", "compare": "Online banking service", "formula": "fixed cost / month"},
            "Mobile Banking": {"unit": "$/month", "compare": "Mobile banking service", "formula": "fixed cost / month"},
            "Bill Payment": {"unit": "$/transaction", "compare": "Utility/meter payments", "formula": "fixed cost"},
            "Card Service": {"unit": "$/year", "compare": "Debit/Credit card fees", "formula": "fixed cost"},
            "Loan": {"unit": "% APR", "compare": "Borrowing cost", "formula": "APR"},
            "Account Maintenance": {"unit": "$/month", "compare": "Account upkeep fees", "formula": "fixed cost / month"}
        }
    },
    "QUALITY": {
        "subcategories": {
            "Download Speed": {"unit": "Mbps", "compare": "Internet speed", "formula": "throughput"},
            "Upload Speed": {"unit": "Mbps", "compare": "Upload performance", "formula": "throughput"},
            "Latency": {"unit": "ms", "compare": "Delay", "formula": "ping time"},
            "Jitter": {"unit": "ms", "compare": "Network stability", "formula": "ms variation"},
            "Network Uptime": {"unit": "% uptime", "compare": "Availability", "formula": "% uptime"},
        }
    },
    "COVERAGE": {
        "subcategories": {
            "Population Coverage": {"unit": "% coverage", "compare": "Percentage of people", "formula": "% reach"},
            "Rural Coverage": {"unit": "% rural", "compare": "Rural reach", "formula": "% reach"},
            "Urban Coverage": {"unit": "% urban", "compare": "City access", "formula": "% reach"},
            "4G/5G Availability": {"unit": "% coverage", "compare": "Mobile generation", "formula": "geographic reach"},
            "Fiber Reach": {"unit": "households", "compare": "Fiber home pass count", "formula": "infrastructure count"},
        }
    },
    "RESTRICTIONS": {
        "subcategories": {
            "Fair Usage Policy": {"unit": "Mbps after cap", "compare": "Speed throttling", "formula": "bandwidth limit"},
        }
    },
    "CUSTOMER EXPERIENCE": {
        "subcategories": {
            "Support Response": {"unit": "minutes/hours", "compare": "Customer service", "formula": "response time"},
            "Downtime incidence": {"unit": "avg hours/mo", "compare": "Outages", "formula": "downtime count"},
            "Complaint Resolution": {"unit": "hours/day", "compare": "Ticket handling", "formula": "issue resolution time"},
        }
    }
}

PERIODS = [
    "per_second", "per_minute", "per_hour", "daily", 
    "three_days", "weekly", "bi_weekly", "monthly", "yearly"
]
