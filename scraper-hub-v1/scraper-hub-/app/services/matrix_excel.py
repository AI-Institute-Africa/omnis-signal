import io
import pandas as pd
from app.services.email_reporter import EmailReporterService
from app.data.retail_commodities import RETAIL_COMMODITIES_DATA

def generate_comprehensive_matrix_excel() -> io.BytesIO:
    """
    Generates a beautifully structured Excel workbook containing:
    1. Master Full Matrix (All Sectors in One Unified Sheet, 165+ rows)
    2. Retail & Supermarket Commodities (78 Products across 10 Departments)
    3. Banking & Transfers (13 Financial Institutions, 58 Services)
    4. Telecom & Mobile Data (14 Services)
    5. Fixed Broadband & ISPs (6 Services)
    6. Transport & Transit (5 Routes)
    7. Fast Food & Dining (3 Meal Tiers)
    8. Hospitality & Hotels (3 Tiers)
    9. Education & Tuition (2 Tiers)
    """
    telecom_data = EmailReporterService.get_structured_telecom_data()
    banking_data = EmailReporterService.get_structured_banking_data()
    retail_data = RETAIL_COMMODITIES_DATA
    
    # ── Sector 1: Retail Commodities (78 Products) ─────────────────
    retail_rows = []
    for item in retail_data:
        retail_rows.append({
            "Department": item.get("dept"),
            "Code": item.get("code"),
            "Commodity / Product Name": item.get("product"),
            "Unit Size": item.get("unit"),
            "OK Zimbabwe": item.get("ok"),
            "Spar Zimbabwe": item.get("spar"),
            "TM Pick n Pay": item.get("tm_pnp"),
            "Gain / Choppies Wholesalers": item.get("gain_choppies"),
            "Category": item.get("category")
        })
    df_retail = pd.DataFrame(retail_rows)

    # ── Sector 2: Telecom ──────────────────────────────────────────
    telecom_rows = []
    for item in telecom_data.get("voice_out_of_bundle", []):
        telecom_rows.append({
            "Sector": "1.0 Telecom Voice OOB",
            "Code": item.get("code"),
            "Service Line / Plan": item.get("plan"),
            "Econet": f"On-Net: {item.get('econet_on_net', '')} | Off-Net: {item.get('econet_off_net', '')}",
            "NetOne": item.get("netone_on_net", ""),
            "Telecel": item.get("telecel", ""),
            "TelOne / Africom": item.get("telone_fixed", ""),
            "Notes / Details": item.get("notes", "")
        })
    for item in telecom_data.get("voice_bundles", []):
        telecom_rows.append({
            "Sector": "1.2 Voice Bundles",
            "Code": item.get("code"),
            "Service Line / Plan": item.get("name"),
            "Econet": item.get("econet"),
            "NetOne": item.get("netone"),
            "Telecel": item.get("telecel"),
            "TelOne / Africom": "Dial 150 / *150#",
            "Notes / Details": "Prepaid Voice Bundles"
        })
    for item in telecom_data.get("data_bundles", []):
        telecom_rows.append({
            "Sector": "2.0 Mobile Data & Social",
            "Code": item.get("code"),
            "Service Line / Plan": item.get("tier"),
            "Econet": item.get("econet"),
            "NetOne": item.get("netone"),
            "Telecel": item.get("telecel"),
            "TelOne / Africom": item.get("telone_blaze", "N/A"),
            "Notes / Details": "Data Bundles"
        })
    df_telecom = pd.DataFrame(telecom_rows)

    # ── Sector 3: Fixed Broadband & ISPs ───────────────────────────
    isp_rows = []
    for item in telecom_data.get("fixed_broadband_isps", []):
        isp_rows.append({
            "Code": item.get("code"),
            "Service Tier": item.get("tier"),
            "Liquid Home (Fibroniks/Wibronix)": item.get("liquid"),
            "TelOne (Blaze LTE / Speed Fibre)": item.get("telone"),
            "Starlink Zimbabwe (Satellite)": item.get("starlink"),
            "Africom": item.get("africom"),
            "Econet SmartSuite": item.get("econet_smartsuite", "See Mobile Data"),
            "Powertel (ZESA)": item.get("powertel"),
            "Utande (Dandemutande)": item.get("utande")
        })
    df_isp = pd.DataFrame(isp_rows)

    # ── Sector 4: Banking & Financial Institutions (13 Banks) ─────
    bank_rows = []
    for sec in banking_data:
        sec_title = sec.get("section", "")
        for r in sec.get("rows", []):
            bank_rows.append({
                "Section": sec_title,
                "Code": r.get("code"),
                "Service / Tariff Line": r.get("name"),
                "CBZ Bank": r.get("cbz"),
                "Stanbic Bank": r.get("stanbic"),
                "CABS": r.get("cabs"),
                "Steward Bank": r.get("steward"),
                "FBC Bank": r.get("fbc"),
                "BancABC": r.get("bancabc"),
                "First Capital": r.get("firstcapital"),
                "NMB Bank": r.get("nmb"),
                "POSB": r.get("posb"),
                "ZB Bank": r.get("zb"),
                "NBS": r.get("nbs"),
                "Nedbank": r.get("nedbank"),
                "Ecobank": r.get("ecobank"),
            })
    df_banking = pd.DataFrame(bank_rows)

    # ── Sector 5: Transport ────────────────────────────────────────
    transport_rows = [
        {"Code": "TR-01", "Category": "Urban Commuter (Short)", "Route": "City Centre - Suburbs (0-10km)", "ZUPCO / Municipal": "$0.50 (ZiG 14.00)", "Private Kombi": "$0.50 - $0.75", "Intercity Coach": "N/A", "Domestic Air": "N/A"},
        {"Code": "TR-02", "Category": "Urban Commuter (Long)", "Route": "Chitungwiza / Norton - Harare CBD", "ZUPCO / Municipal": "$1.00 - $1.50", "Private Kombi": "$1.50 - $2.00", "Intercity Coach": "N/A", "Domestic Air": "N/A"},
        {"Code": "TR-03", "Category": "Intercity Main", "Route": "Harare - Bulawayo (440km)", "ZUPCO / Municipal": "$10.00", "Private Kombi": "N/A", "Intercity Coach": "$15.00 - $20.00", "Domestic Air": "$95.00 - $140.00"},
        {"Code": "TR-04", "Category": "Intercity Tourism", "Route": "Harare - Victoria Falls (880km)", "ZUPCO / Municipal": "N/A", "Private Kombi": "N/A", "Intercity Coach": "$30.00 - $35.00", "Domestic Air": "$115.00 - $185.00"},
        {"Code": "TR-05", "Category": "Cross-Border", "Route": "Harare - Johannesburg", "ZUPCO / Municipal": "N/A", "Private Kombi": "N/A", "Intercity Coach": "$40.00 - $60.00", "Domestic Air": "$160.00 - $280.00"},
    ]
    df_transport = pd.DataFrame(transport_rows)

    # ── Sector 6: Food & Dining ────────────────────────────────────
    food_rows = [
        {"Code": "FD-01", "Meal Category": "Standard Solo Meal", "Chicken Inn": "2-Piecer & Chips: $3.50", "Pizza Inn": "Small Classic Pizza: $4.00", "Nandos": "1/4 Chicken + Side: $5.50", "Steers_Wimpy": "Classic Burger & Chips: $4.50"},
        {"Code": "FD-02", "Meal Category": "Combo Meal with Soda", "Chicken Inn": "3-Piecer Combo: $5.50", "Pizza Inn": "Medium Pizza Combo: $7.50", "Nandos": "1/2 Chicken & Drink: $9.50", "Steers_Wimpy": "King Burger Combo: $7.00"},
        {"Code": "FD-03", "Meal Category": "Family / Group Sharing", "Chicken Inn": "Mega Meal (8pc): $15.00", "Pizza Inn": "Mega Feast (2 Large): $20.00", "Nandos": "Full Platter: $22.00", "Steers_Wimpy": "Family Sharing Pack: $18.00"},
    ]
    df_food = pd.DataFrame(food_rows)

    # ── Sector 7: Hotels ───────────────────────────────────────────
    hotel_rows = [
        {"Code": "HTL-01", "Room Tier": "Standard Deluxe Room", "Meikles Hotel (5★)": "$190/night (B&B)", "Rainbow Towers (4★)": "$120/night (B&B)", "Cresta Lodge (3★)": "$85/night (B&B)", "Victoria Falls Hotel (5★)": "$350/night (B&B)"},
        {"Code": "HTL-02", "Room Tier": "Executive / Club Suite", "Meikles Hotel (5★)": "$320/night", "Rainbow Towers (4★)": "$220/night", "Cresta Lodge (3★)": "$145/night", "Victoria Falls Hotel (5★)": "$580/night"},
        {"Code": "HTL-03", "Room Tier": "Presidential Suite", "Meikles Hotel (5★)": "$850/night", "Rainbow Towers (4★)": "$650/night", "Cresta Lodge (3★)": "N/A", "Victoria Falls Hotel (5★)": "$1,200/night"},
    ]
    df_hotels = pd.DataFrame(hotel_rows)

    # ── Sector 8: Education ────────────────────────────────────────
    edu_rows = [
        {"Code": "EDU-01", "Level & Programme": "Undergraduate / Term Tuition", "University of Zimbabwe": "$450/sem (Humanities)", "NUST Bulawayo": "$550/sem (Commerce)", "St George's College": "$1,800/term (Day)", "Chisipite Senior School": "$1,950/term (Day)"},
        {"Code": "EDU-02", "Level & Programme": "STEM / Medicine / Boarding", "University of Zimbabwe": "$650/sem (STEM/Med)", "NUST Bulawayo": "$700/sem (Engineering)", "St George's College": "$3,200/term (Boarding)", "Chisipite Senior School": "$3,400/term (Boarding)"},
    ]
    df_edu = pd.DataFrame(edu_rows)

    # ── MASTER SHEET (165+ rows across all sectors) ────────────────
    master_rows = []
    # 1. Retail (78 items)
    for r in retail_rows:
        master_rows.append({
            "Main Sector": "Retail & Supermarkets",
            "Sub-Category": r.get("Department"),
            "Item Code": r.get("Code"),
            "Service / Product Description": f"{r.get('Commodity / Product Name')} ({r.get('Unit Size')})",
            "Provider 1": f"OK: {r.get('OK Zimbabwe')}",
            "Provider 2": f"Spar: {r.get('Spar Zimbabwe')}",
            "Provider 3": f"Pick n Pay: {r.get('TM Pick n Pay')}",
            "Provider 4": f"Gain/Choppies: {r.get('Gain / Choppies Wholesalers')}",
            "Other Institutions": r.get("Category")
        })
    # 2. Banking (58 items)
    for r in bank_rows:
        master_rows.append({
            "Main Sector": "Banking & Finance",
            "Sub-Category": r.get("Section"),
            "Item Code": r.get("Code"),
            "Service / Product Description": r.get("Service / Tariff Line"),
            "Provider 1": f"CBZ: {r.get('CBZ Bank')}",
            "Provider 2": f"Stanbic: {r.get('Stanbic Bank')}",
            "Provider 3": f"CABS: {r.get('CABS')}",
            "Provider 4": f"Steward: {r.get('Steward Bank')}",
            "Other Institutions": f"FBC: {r.get('FBC Bank')} | BancABC: {r.get('BancABC')} | FirstCap: {r.get('First Capital')} | NMB: {r.get('NMB Bank')} | POSB: {r.get('POSB')} | ZB: {r.get('ZB Bank')} | NBS: {r.get('NBS')} | Nedbank: {r.get('Nedbank')} | Ecobank: {r.get('Ecobank')}"
        })
    # 3. Telecom (14 items)
    for r in telecom_rows:
        master_rows.append({
            "Main Sector": "Telecommunications",
            "Sub-Category": r.get("Sector"),
            "Item Code": r.get("Code"),
            "Service / Product Description": r.get("Service Line / Plan"),
            "Provider 1": f"Econet: {r.get('Econet')}",
            "Provider 2": f"NetOne: {r.get('NetOne')}",
            "Provider 3": f"Telecel: {r.get('Telecel')}",
            "Provider 4": f"TelOne: {r.get('TelOne / Africom')}",
            "Other Institutions": r.get("Notes / Details")
        })
    # 4. ISPs (6 items)
    for r in isp_rows:
        master_rows.append({
            "Main Sector": "Broadband & ISPs",
            "Sub-Category": "Fixed Internet",
            "Item Code": r.get("Code"),
            "Service / Product Description": r.get("Service Tier"),
            "Provider 1": f"Liquid: {r.get('Liquid Home (Fibroniks/Wibronix)')}",
            "Provider 2": f"TelOne: {r.get('TelOne (Blaze LTE / Speed Fibre)')}",
            "Provider 3": f"Starlink: {r.get('Starlink Zimbabwe (Satellite)')}",
            "Provider 4": f"Africom: {r.get('Africom')}",
            "Other Institutions": f"Powertel: {r.get('Powertel (ZESA)')} | Utande: {r.get('Utande (Dandemutande)')}"
        })
    # 5. Transport (5 items)
    for r in transport_rows:
        master_rows.append({
            "Main Sector": "Transport",
            "Sub-Category": r.get("Category"),
            "Item Code": r.get("Code"),
            "Service / Product Description": r.get("Route"),
            "Provider 1": f"ZUPCO: {r.get('ZUPCO / Municipal')}",
            "Provider 2": f"Kombi: {r.get('Private Kombi')}",
            "Provider 3": f"Coach: {r.get('Intercity Coach')}",
            "Provider 4": f"Air: {r.get('Domestic Air')}",
            "Other Institutions": "Public & Private Transit"
        })
    # 6. Food (3 items)
    for r in food_rows:
        master_rows.append({
            "Main Sector": "Food & Dining",
            "Sub-Category": "Fast Food",
            "Item Code": r.get("Code"),
            "Service / Product Description": r.get("Meal Category"),
            "Provider 1": f"Chicken Inn: {r.get('Chicken Inn')}",
            "Provider 2": f"Pizza Inn: {r.get('Pizza Inn')}",
            "Provider 3": f"Nandos: {r.get('Nandos')}",
            "Provider 4": f"Steers/Wimpy: {r.get('Steers_Wimpy')}",
            "Other Institutions": "Quick Service Restaurants"
        })
    # 7. Hotels (3 items)
    for r in hotel_rows:
        master_rows.append({
            "Main Sector": "Hospitality",
            "Sub-Category": "Hotels & Lodges",
            "Item Code": r.get("Code"),
            "Service / Product Description": r.get("Room Tier"),
            "Provider 1": f"Meikles: {r.get('Meikles Hotel (5★)')}",
            "Provider 2": f"Rainbow: {r.get('Rainbow Towers (4★)')}",
            "Provider 3": f"Cresta: {r.get('Cresta Lodge (3★)')}",
            "Provider 4": f"Vic Falls Hotel: {r.get('Victoria Falls Hotel (5★)')}",
            "Other Institutions": "Accommodation"
        })
    # 8. Education (2 items)
    for r in edu_rows:
        master_rows.append({
            "Main Sector": "Education",
            "Sub-Category": "Tuition Fees",
            "Item Code": r.get("Code"),
            "Service / Product Description": r.get("Level & Programme"),
            "Provider 1": f"UZ: {r.get('University of Zimbabwe')}",
            "Provider 2": f"NUST: {r.get('NUST Bulawayo')}",
            "Provider 3": f"St George's: {r.get('St George\'s College')}",
            "Provider 4": f"Chisipite: {r.get('Chisipite Senior School')}",
            "Other Institutions": "Academic Fees"
        })
    df_master = pd.DataFrame(master_rows)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Master All Sectors (165+ comprehensive rows)
        df_master.to_excel(writer, index=False, sheet_name="Master Price Matrix")
        # Sheet 2: Retail Commodities (78 items)
        df_retail.to_excel(writer, index=False, sheet_name="Retail & Groceries (78 Items)")
        # Sheet 3: Banking All 13 Institutions & Transfers (58 rows)
        df_banking.to_excel(writer, index=False, sheet_name="Banking (13 Institutions)")
        # Sheet 4: Telecom MNOs (14 rows)
        df_telecom.to_excel(writer, index=False, sheet_name="Telecom MNOs (Voice & Data)")
        # Sheet 5: Broadband & ISPs (6 rows)
        df_isp.to_excel(writer, index=False, sheet_name="Broadband & ISPs")
        # Sheet 6: Transport
        df_transport.to_excel(writer, index=False, sheet_name="Transport Fares")
        # Sheet 7: Food & Dining
        df_food.to_excel(writer, index=False, sheet_name="Food & Dining")
        # Sheet 8: Hotels
        df_hotels.to_excel(writer, index=False, sheet_name="Hotels & Stays")
        # Sheet 9: Education
        df_edu.to_excel(writer, index=False, sheet_name="Education & Tuition")

    output.seek(0)
    return output
