"""Zimbabwe organizations master catalog — Part 1 of 2 (Banks, Hotels, Telecoms, Mobility)"""
import re

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

ORGANIZATIONS = [
    # ── BANKS ────────────────────────────────────────────────────────────────
    {"name": "Reserve Bank of Zimbabwe", "category": "banks", "website": "https://www.rbz.co.zw", "keywords": ["central bank", "monetary policy", "forex"]},
    {"name": "First Capital Bank Zimbabwe", "category": "banks", "website": "https://www.firstcapitalbank.co.zw", "keywords": ["banking", "loans", "savings"]},
    {"name": "POSB Zimbabwe", "category": "banks", "website": "https://www.posb.co.zw", "keywords": ["savings", "retail banking"]},
    {"name": "CBZ Bank", "category": "banks", "website": "https://www.cbz.co.zw", "keywords": ["banking", "mortgage", "loans"]},
    {"name": "Steward Bank", "category": "banks", "website": "https://www.stewardbank.co.zw", "keywords": ["digital banking", "ecocash", "loans"]},
    {"name": "Stanbic Bank Zimbabwe", "category": "banks", "website": "https://www.stanbicbank.co.zw", "keywords": ["banking", "corporate", "trade finance"]},
    {"name": "NMB Bank", "category": "banks", "website": "https://www.nmbz.co.zw", "keywords": ["banking", "mortgages"]},
    {"name": "FBC Bank", "category": "banks", "website": "https://www.fbc.co.zw", "keywords": ["banking", "insurance", "microfinance"]},
    {"name": "BancABC Zimbabwe", "category": "banks", "website": "https://www.bancabc.co.zw", "keywords": ["banking", "africa"]},
    {"name": "Ecobank Zimbabwe", "category": "banks", "website": "https://www.ecobank.com/zw", "keywords": ["banking", "pan-africa"]},
    {"name": "CABS", "category": "banks", "website": "https://www.cabs.co.zw", "keywords": ["building society", "mortgages", "savings"]},
    {"name": "ZB Bank", "category": "banks", "website": "https://www.zb.co.zw", "keywords": ["banking", "insurance"]},
    {"name": "AFC Commercial Bank", "category": "banks", "website": "https://www.afcholdings.co.zw", "keywords": ["agriculture", "commercial banking"]},
    {"name": "Infrastructure Development Bank of Zimbabwe", "category": "banks", "website": "https://www.idbz.co.zw", "keywords": ["infrastructure", "development finance"]},
    {"name": "MetBank", "category": "banks", "website": "https://www.metbank.co.zw", "keywords": ["banking", "finance"]},
    {"name": "Nedbank Zimbabwe", "category": "banks", "website": "https://www.nedbank.co.zw", "keywords": ["banking", "south africa"]},
    {"name": "Agribank", "category": "banks", "website": "https://www.agribank.co.zw", "keywords": ["agriculture", "farming", "rural banking"]},
    {"name": "GetBucks Microfinance Bank", "category": "banks", "website": "https://www.getbucks.co.zw", "keywords": ["microfinance", "personal loans"]},
    {"name": "EmpowerBank", "category": "banks", "website": "https://www.empowerbank.co.zw", "keywords": ["microfinance", "empowerment"]},
    {"name": "Women's Microfinance Bank", "category": "banks", "website": "https://www.womensmicrofinancebank.co.zw", "keywords": ["women", "microfinance"]},
    {"name": "ZB Building Society", "category": "banks", "website": "https://www.zb.co.zw", "keywords": ["building society", "mortgages"]},
    {"name": "National Building Society", "category": "banks", "website": "https://www.nbs.co.zw", "keywords": ["building society", "housing"]},
    {"name": "TN Bank", "category": "banks", "website": "https://www.tnbank.co.zw", "keywords": ["banking"]},
    {"name": "Homelink Finance", "category": "banks", "website": "https://www.homelink.co.zw", "keywords": ["diaspora", "remittance", "finance"]},

    # ── HOTELS ───────────────────────────────────────────────────────────────
    {"name": "The Victoria Falls Hotel", "category": "hotels", "website": "https://www.victoriafallshotel.com", "keywords": ["luxury", "victoria falls", "heritage hotel"]},
    {"name": "Hyatt Regency Harare The Meikles", "category": "hotels", "website": "https://www.hyatt.com", "keywords": ["luxury", "harare", "5-star"]},
    {"name": "Monomotapa Hotel", "category": "hotels", "website": "https://www.monomotapahotel.com", "keywords": ["harare", "conference", "hotel"]},
    {"name": "Rainbow Towers Hotel", "category": "hotels", "website": "https://www.rainbowharare.com", "keywords": ["harare", "conference", "hotel"]},
    {"name": "Elephant Hills Resort", "category": "hotels", "website": "https://www.elephanthills.com", "keywords": ["victoria falls", "resort", "golf"]},
    {"name": "Palm River Hotel", "category": "hotels", "website": "https://www.palmriverhotel.com", "keywords": ["victoria falls", "boutique hotel"]},
    {"name": "Cresta Lodge Harare", "category": "hotels", "website": "https://www.crestahotels.com", "keywords": ["harare", "lodge", "conference"]},
    {"name": "Cresta Jameson Hotel", "category": "hotels", "website": "https://www.crestahotels.com", "keywords": ["harare", "business hotel"]},
    {"name": "Holiday Inn Harare", "category": "hotels", "website": "https://www.ihg.com", "keywords": ["harare", "international", "hotel"]},
    {"name": "Bronte Hotel", "category": "hotels", "website": "https://www.brontehotel.co.zw", "keywords": ["harare", "boutique"]},
    {"name": "Troutbeck Resort", "category": "hotels", "website": "https://www.troutbeck.co.zw", "keywords": ["nyanga", "resort", "highlands"]},
    {"name": "Leopard Rock Hotel", "category": "hotels", "website": "https://www.leopardrock.co.zw", "keywords": ["bvumba", "luxury", "golf"]},
    {"name": "Great Zimbabwe Hotel", "category": "hotels", "website": "https://www.greatzimbabwehotel.com", "keywords": ["masvingo", "heritage"]},
    {"name": "Ilala Lodge Hotel", "category": "hotels", "website": "https://www.ilalalodge.com", "keywords": ["victoria falls", "luxury lodge"]},
    {"name": "Victoria Falls Safari Lodge", "category": "hotels", "website": "https://www.victoria-falls-safari-lodge.com", "keywords": ["victoria falls", "safari", "wildlife"]},
    {"name": "Bulawayo Rainbow Hotel", "category": "hotels", "website": "https://www.rainbowbulawayo.com", "keywords": ["bulawayo", "conference", "hotel"]},
    {"name": "N1 Hotel Harare", "category": "hotels", "website": "https://www.n1hotels.com", "keywords": ["harare", "budget hotel"]},
    {"name": "New Ambassador Hotel", "category": "hotels", "website": "https://www.ambassadorhotel.co.zw", "keywords": ["harare", "hotel"]},

    # ── TELECOMS ─────────────────────────────────────────────────────────────
    {"name": "Econet Wireless Zimbabwe", "category": "telecoms", "website": "https://www.econet.co.zw", "keywords": ["mobile", "data", "ecocash", "broadband"]},
    {"name": "Telecel Zimbabwe", "category": "telecoms", "website": "https://www.telecel.co.zw", "keywords": ["mobile", "data", "voice"]},
    {"name": "NetOne", "category": "telecoms", "website": "https://www.netone.co.zw", "keywords": ["mobile", "one money", "data"]},
    {"name": "TelOne", "category": "telecoms", "website": "https://www.telone.co.zw", "keywords": ["fixed line", "fibre", "internet", "adsl"]},
    {"name": "Liquid Intelligent Technologies Zimbabwe", "category": "telecoms", "website": "https://www.liquid.tech", "keywords": ["fibre", "enterprise", "cloud"]},
    {"name": "Powertel Communications", "category": "telecoms", "website": "https://www.powertel.co.zw", "keywords": ["internet", "broadband", "wimax"]},
    {"name": "Africom", "category": "telecoms", "website": "https://www.africom.co.zw", "keywords": ["internet", "wireless", "broadband"]},
    {"name": "Dandemutande", "category": "telecoms", "website": "https://www.dandemutande.co.zw", "keywords": ["internet", "wireless"]},
    {"name": "YoAfrica", "category": "telecoms", "website": "https://www.yoafrica.com", "keywords": ["internet", "fibre", "wireless"]},
    {"name": "Utande Internet Services", "category": "telecoms", "website": "https://www.utande.co.zw", "keywords": ["internet", "isp"]},
    {"name": "ZOL Zimbabwe", "category": "telecoms", "website": "https://www.zol.co.zw", "keywords": ["internet", "fibre", "wifi"]},
    {"name": "Paratus Zimbabwe", "category": "telecoms", "website": "https://www.paratus.co.zw", "keywords": ["internet", "satellite", "enterprise"]},
    {"name": "Zarnet", "category": "telecoms", "website": "https://www.zarnet.ac.zw", "keywords": ["internet", "education", "research"]},
    {"name": "Brodacom", "category": "telecoms", "website": "https://www.brodacom.co.zw", "keywords": ["internet", "wireless"]},
    {"name": "Dolphin Telecoms", "category": "telecoms", "website": "https://www.dolphintelecom.co.zw", "keywords": ["internet", "broadband"]},
    {"name": "Microcom Technologies Zimbabwe", "category": "telecoms", "website": "https://www.microcom.co.zw", "keywords": ["internet", "it solutions"]},

    # ── MOBILITY ─────────────────────────────────────────────────────────────
    {"name": "Vaya Africa", "category": "mobility", "website": "https://www.vaya.africa", "keywords": ["ride hailing", "logistics", "fintech"]},
    {"name": "Hwindi", "category": "mobility", "website": "https://www.hwindi.com", "keywords": ["ride hailing", "transport", "zimbabwe"]},
    {"name": "InDrive Zimbabwe", "category": "mobility", "website": "https://www.indrive.com", "keywords": ["ride hailing", "negotiable fare"]},
    {"name": "ZUPCO", "category": "mobility", "website": "https://www.zupco.co.zw", "keywords": ["public transport", "bus", "commuter"]},
    {"name": "Rimbi Mobility", "category": "mobility", "website": "https://www.rimbi.co.zw", "keywords": ["mobility", "transport tech"]},
    {"name": "Tap and Go Zimbabwe", "category": "mobility", "website": "https://www.tapandgo.co.zw", "keywords": ["contactless payment", "transport", "fintech"]},
]

def get_organizations():
    """Return all organizations with computed slugs."""
    result = []
    seen_slugs = {}
    for org in ORGANIZATIONS:
        base_slug = slugify(org["name"])
        count = seen_slugs.get(base_slug, 0)
        slug = base_slug if count == 0 else f"{base_slug}-{count}"
        seen_slugs[base_slug] = count + 1
        result.append({**org, "slug": slug})
    return result
