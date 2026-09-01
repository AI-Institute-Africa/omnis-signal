import io
import pandas as pd
from app.services.email_reporter import EmailReporterService

def generate_comprehensive_matrix_excel() -> io.BytesIO:
    """
    Generates a beautifully structured Excel workbook containing:
    1. Master Full Matrix (All Sectors in One Unified Sheet)
    2. Telecom & Mobile Data
    3. Fixed Broadband & ISPs
    4. Banking & Transfers (13 Financial Institutions)
    5. Transport & Transit
    6. Retail & Supermarket
    7. Fast Food & Dining
    8. Hospitality & Hotels
    9. Education & Tuition
    """
    telecom_data = EmailReporterService.get_structured_telecom_data()
    banking_data = EmailReporterService.get_structured_banking_data()
    
    # ── Sector 1 & 2: Telecom ──────────────────────────────────────
    telecom_rows = []
    # Voice OOB
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
    # Voice Bundles
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
    # Data Bundles
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

    # ── Sector 6: Retail ───────────────────────────────────────────
    retail_rows = [
        {"Code": "RET-01", "Commodity": "Pure Cooking Oil", "Unit Size": "2 Litres", "OK Zimbabwe": "$3.20", "Spar Zimbabwe": "$3.35", "Pick n Pay ZW": "$3.15", "TM Supermarkets": "$3.20"},
        {"Code": "RET-02", "Commodity": "Roller Mealie Meal", "Unit Size": "10 kg", "OK Zimbabwe": "$6.50", "Spar Zimbabwe": "$6.80", "Pick n Pay ZW": "$6.40", "TM Supermarkets": "$6.50"},
        {"Code": "RET-03", "Commodity": "White Sugar (Sunsweet)", "Unit Size": "2 kg", "OK Zimbabwe": "$2.40", "Spar Zimbabwe": "$2.50", "Pick n Pay ZW": "$2.35", "TM Supermarkets": "$2.40"},
        {"Code": "RET-04", "Commodity": "Standard White Bread", "Unit Size": "700g Loaf", "OK Zimbabwe": "$1.00", "Spar Zimbabwe": "$1.00", "Pick n Pay ZW": "$1.00", "TM Supermarkets": "$1.00"},
        {"Code": "RET-05", "Commodity": "Self Raising Flour (Gloria)", "Unit Size": "2 kg", "OK Zimbabwe": "$2.10", "Spar Zimbabwe": "$2.25", "Pick n Pay ZW": "$2.05", "TM Supermarkets": "$2.10"},
        {"Code": "RET-06", "Commodity": "Fresh Milk (Dairibord)", "Unit Size": "500 ml", "OK Zimbabwe": "$0.85", "Spar Zimbabwe": "$0.90", "Pick n Pay ZW": "$0.80", "TM Supermarkets": "$0.85"},
    ]
    df_retail = pd.DataFrame(retail_rows)

    # ── Sector 7: Food & Dining ────────────────────────────────────
    food_rows = [
        {"Code": "FD-01", "Meal Category": "Standard Solo Meal", "Chicken Inn": "2-Piecer & Chips: $3.50", "Pizza Inn": "Small Classic Pizza: $4.00", "Nando's": "1/4 Chicken + Side: $5.50", "Steers / Wimpy": "Classic Burger & Chips: $4.50"},
        {"Code": "FD-02", "Meal Category": "Combo Meal with Soda", "Chicken Inn": "3-Piecer Combo: $5.50", "Pizza Inn": "Medium Pizza Combo: $7.50", "Nando's": "1/2 Chicken & Drink: $9.50", "Steers / Wimpy": "King Burger Combo: $7.00"},
        {"Code": "FD-03", "Meal Category": "Family / Group Sharing", "Chicken Inn": "Mega Meal (8pc): $15.00", "Pizza Inn": "Mega Feast (2 Large): $20.00", "Nando's": "Full Platter: $22.00", "Steers / Wimpy": "Family Sharing Pack: $18.00"},
    ]
    df_food = pd.DataFrame(food_rows)

    # ── Sector 8: Hotels ───────────────────────────────────────────
    hotel_rows = [
        {"Code": "HTL-01", "Room Tier": "Standard Deluxe Room", "Meikles Hotel (5★)": "$190/night (B&B)", "Rainbow Towers (4★)": "$120/night (B&B)", "Cresta Lodge (3★)": "$85/night (B&B)", "Victoria Falls Hotel (5★)": "$350/night (B&B)"},
        {"Code": "HTL-02", "Room Tier": "Executive / Club Suite", "Meikles Hotel (5★)": "$320/night", "Rainbow Towers (4★)": "$220/night", "Cresta Lodge (3★)": "$145/night", "Victoria Falls Hotel (5★)": "$580/night"},
        {"Code": "HTL-03", "Room Tier": "Presidential Suite", "Meikles Hotel (5★)": "$850/night", "Rainbow Towers (4★)": "$650/night", "Cresta Lodge (3★)": "N/A", "Victoria Falls Hotel (5★)": "$1,200/night"},
    ]
    df_hotels = pd.DataFrame(hotel_rows)

    # ── Sector 9: Education ────────────────────────────────────────
    edu_rows = [
        {"Code": "EDU-01", "Level & Programme": "Undergraduate / Term Tuition", "University of Zimbabwe": "$450/sem (Humanities)", "NUST Bulawayo": "$550/sem (Commerce)", "St George's College": "$1,800/term (Day)", "Chisipite Senior School": "$1,950/term (Day)"},
        {"Code": "EDU-02", "Level & Programme": "STEM / Medicine / Boarding", "University of Zimbabwe": "$650/sem (STEM/Med)", "NUST Bulawayo": "$700/sem (Engineering)", "St George's College": "$3,200/term (Boarding)", "Chisipite Senior School": "$3,400/term (Boarding)"},
    ]
    df_edu = pd.DataFrame(edu_rows)

    # ── MASTER SHEET (All 95+ rows across all sectors) ─────────────
    master_rows = []
    for r in bank_rows:
        master_rows.append({
            "Main Sector": "Banking & Finance",
            "Sub-Category": r["Section"],
            "Item Code": r["Code"],
            "Service / Product Description": r["Service / Tariff Line"],
            "Provider 1": f"CBZ: {r['CBZ Bank']}",
            "Provider 2": f"Stanbic: {r['Stanbic Bank']}",
            "Provider 3": f"CABS: {r['CABS']}",
            "Provider 4": f"Steward: {r['Steward Bank']}",
            "Other Institutions": f"FBC: {r['FBC Bank']} | BancABC: {r['BancABC']} | FirstCap: {r['First Capital']} | NMB: {r['NMB Bank']} | POSB: {r['POSB']} | ZB: {r['ZB Bank']} | NBS: {r['NBS']} | Nedbank: {r['Nedbank']} | Ecobank: {r['Ecobank']}"
        })
    for r in telecom_rows:
        master_rows.append({
            "Main Sector": "Telecommunications",
            "Sub-Category": r["Sector"],
            "Item Code": r["Code"],
            "Service / Product Description": r["Service Line / Plan"],
            "Provider 1": f"Econet: {r['Econet']}",
            "Provider 2": f"NetOne: {r['NetOne']}",
            "Provider 3": f"Telecel: {r['Telecel']}",
            "Provider 4": f"TelOne: {r['TelOne / Africom']}",
            "Other Institutions": r["Notes / Details"]
        })
    for r in isp_rows:
        master_rows.append({
            "Main Sector": "Broadband & ISPs",
            "Sub-Category": "Fixed Internet",
            "Item Code": r["Code"],
            "Service / Product Description": r["Service Tier"],
            "Provider 1": f"Liquid: {r['Liquid Home (Fibroniks/Wibronix)']}",
            "Provider 2": f"TelOne: {r['TelOne (Blaze LTE / Speed Fibre)']}",
            "Provider 3": f"Starlink: {r['Starlink Zimbabwe (Satellite)']}",
            "Provider 4": f"Africom: {r['Africom']}",
            "Other Institutions": f"Powertel: {r['Powertel (ZESA)']} | Utande: {r['Utande (Dandemutande)']}"
        })
    for r in transport_rows:
        master_rows.append({
            "Main Sector": "Transport",
            "Sub-Category": r["Category"],
            "Item Code": r["Code"],
            "Service / Product Description": r["Route"],
            "Provider 1": f"ZUPCO: {r['ZUPCO / Municipal']}",
            "Provider 2": f"Kombi: {r['Private Kombi']}",
            "Provider 3": f"Coach: {r['Intercity Coach']}",
            "Provider 4": f"Air: {r['Domestic Air']}",
            "Other Institutions": "Public & Private Transit"
        })
    for r in retail_rows:
        master_rows.append({
            "Main Sector": "Retail",
            "Sub-Category": "Supermarket Basket",
            "Item Code": r["Code"],
            "Service / Product Description": f"{r['Commodity']} ({r['Unit Size']})",
            "Provider 1": f"OK: {r['OK Zimbabwe']}",
            "Provider 2": f"Spar: {r['Spar Zimbabwe']}",
            "Provider 3": f"Pick n Pay: {r['Pick n Pay ZW']}",
            "Provider 4": f"TM: {r['TM Supermarkets']}",
            "Other Institutions": "Retail Grocery Basket"
        })
    for r in food_rows:
        master_rows.append({
            "Main Sector": "Food & Dining",
            "Sub-Category": "Fast Food",
            "Item Code": r["Code"],
            "Service / Product Description": r["Meal Category"],
            "Provider 1": f"Chicken Inn: {r['Chicken Inn']}",
            "Provider 2": f"Pizza Inn: {r['Pizza Inn']}",
            "Provider 3": f"Nando's: {r['Nando\'s']}",
            "Provider 4": f"Steers/Wimpy: {r['Steers / Wimpy']}",
            "Other Institutions": "Quick Service Restaurants"
        })
    for r in hotel_rows:
        master_rows.append({
            "Main Sector": "Hospitality",
            "Sub-Category": "Hotels & Lodges",
            "Item Code": r["Code"],
            "Service / Product Description": r["Room Tier"],
            "Provider 1": f"Meikles: {r['Meikles Hotel (5★)']}",
            "Provider 2": f"Rainbow: {r['Rainbow Towers (4★)']}",
            "Provider 3": f"Cresta: {r['Cresta Lodge (3★)']}",
            "Provider 4": f"Vic Falls Hotel: {r['Victoria Falls Hotel (5★)']}",
            "Other Institutions": "Accommodation"
        })
    for r in edu_rows:
        master_rows.append({
            "Main Sector": "Education",
            "Sub-Category": "Tuition Fees",
            "Item Code": r["Code"],
            "Service / Product Description": r["Level & Programme"],
            "Provider 1": f"UZ: {r['University of Zimbabwe']}",
            "Provider 2": f"NUST: {r['NUST Bulawayo']}",
            "Provider 3": f"St George's: {r['St George\'s College']}",
            "Provider 4": f"Chisipite: {r['Chisipite Senior School']}",
            "Other Institutions": "Academic Fees"
        })
    df_master = pd.DataFrame(master_rows)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Master All Sectors (100+ comprehensive rows)
        df_master.to_excel(writer, index=False, sheet_name="Master Price Matrix")
        # Sheet 2: Banking All 13 Institutions & Transfers (58 rows)
        df_banking.to_excel(writer, index=False, sheet_name="Banking (13 Institutions)")
        # Sheet 3: Telecom MNOs (14 rows)
        df_telecom.to_excel(writer, index=False, sheet_name="Telecom MNOs (Voice & Data)")
        # Sheet 4: Broadband & ISPs (6 rows)
        df_isp.to_excel(writer, index=False, sheet_name="Broadband & ISPs")
        # Sheet 5: Transport
        df_transport.to_excel(writer, index=False, sheet_name="Transport Fares")
        # Sheet 6: Retail
        df_retail.to_excel(writer, index=False, sheet_name="Retail & Groceries")
        # Sheet 7: Food & Dining
        df_food.to_excel(writer, index=False, sheet_name="Food & Dining")
        # Sheet 8: Hotels
        df_hotels.to_excel(writer, index=False, sheet_name="Hotels & Stays")
        # Sheet 9: Education
        df_edu.to_excel(writer, index=False, sheet_name="Education & Tuition")

    output.seek(0)
    return output
