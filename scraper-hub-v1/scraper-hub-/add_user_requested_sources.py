
import sys
import os
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.db.models import Source

data = {
    "banking": [
        "Reserve Bank of Zimbabwe", "First Capital Bank Zimbabwe", "POSB Zimbabwe", "CBZ Bank", "Steward Bank",
        "Stanbic Bank Zimbabwe", "NMB Bank", "FBC Bank", "BancABC Zimbabwe", "Ecobank Zimbabwe", "CABS",
        "ZB Bank", "AFC Commercial Bank", "Infrastructure Development Bank of Zimbabwe (IDBZ)", "MetBank",
        "Nedbank Zimbabwe", "Agribank", "TN Bank", "Time Bank", "Allied Bank Zimbabwe", "Trust Bank",
        "Kingdom Bank", "Interfin Bank", "Renaissance Merchant Bank", "Tetrad Investment Bank", "Homelink Finance",
        "GetBucks Microfinance Bank", "EmpowerBank", "Women's Microfinance Bank", "ZB Building Society",
        "National Building Society (NBS)"
    ],
    "hotels": [
        "The Victoria Falls Hotel", "Hyatt Regency Harare The Meikles", "Monomotapa Hotel", "Rainbow Towers Hotel",
        "Elephant Hills Resort", "Palm River Hotel", "Cresta Lodge Harare", "Cresta Jameson Hotel", "Holiday Inn Harare",
        "Bronte Hotel", "Amanzi Lodge", "Troutbeck Resort", "Leopard Rock Hotel", "Great Zimbabwe Hotel", "Ilala Lodge Hotel",
        "Bayete Guest Lodge", "Victoria Falls Safari Lodge", "Mbano Manor Hotel", "Shearwater Explorers Village", "N1 Hotel",
        "New Ambassador Hotel", "Bulawayo Rainbow Hotel"
    ],
    "transport": [
        "Vaya Africa", "Hwindi", "InDrive Zimbabwe", "ZUPCO", "Mushikashika operators", "Rimbi Mobility", "Tap and Go Zimbabwe",
        "Strauss Logistics Zimbabwe", "Whelson Transport", "Unifreight Africa", "Swift Transport Services", "Bakers Inn Logistics",
        "National Railways of Zimbabwe", "Zimpost", "DHL Zimbabwe", "FedEx Zimbabwe", "Cargo Carriers", "Cross Country Transport",
        "Pioneer Transport", "Pathfinder Luxury Coaches", "Eagle Liner Zimbabwe", "Inter Africa Bus Services", "Blue Arrow Bus Services",
        "Stallion Cruise Coaches"
    ],
    "telecom": [
        "Econet Wireless Zimbabwe", "Telecel Zimbabwe", "NetOne", "TelOne", "Liquid Intelligent Technologies Zimbabwe",
        "Powertel Communications", "Africom", "Dandemutande", "YoAfrica", "Utande Internet Services", "Microcom Technologies - Zimbabwe",
        "Dolphin Telecoms", "ZOL Zimbabwe", "Paratus Zimbabwe", "Zarnet", "Brodacom"
    ],
    "education": [
        "University of Zimbabwe", "National University of Science and Technology, Zimbabwe", "Lupane State University.",
        "Midlands State University", "Chinhoyi University of Technology", "Harare Institute of Technology", "Zimbabwe Open University",
        "Africa University", "Great Zimbabwe University", "Bindura University of Science Education", "Manicaland State University of Applied Sciences",
        "Marondera University of Agricultural Sciences and Technology", "Catholic University in Zimbabwe", "Reformed Church University",
        "Solusi University", "Women's University in Africa", "Zimbabwe Ezekiel Guti University", "Pan African Christian University",
        "Arrupe Jesuit University", "Gwanda State University", "Speciss College", "Trust Academy", "Success Tutorial College", "Herentals College",
        "Morgan Zintec Teachers College", "Belvedere Technical Teachers College", "Harare Polytechnic", "Bulawayo Polytechnic",
        "Kwekwe Polytechnic", "Mutare Polytechnic", "Masvingo Polytechnic", "Hillside Teachers College", "Mkoba Teachers College",
        "Seke Teachers College", "United College of Education", "Joshua Mqabuko Nkomo Polytechnic", "Zimbabwe School of Mines",
        "Southern Africa Methodist University", "Zimbabwe Institute of Management"
    ],
    "schools": [
        "Prince Edward School", "St George's College", "Peterhouse Boys' School", "Peterhouse Girls' School", "Arundel School",
        "Falcon College", "Lomagundi College", "Gateway High School", "Dominican Convent High School", "Allan Wilson High School",
        "Churchill School", "Heritage School", "Watershed College", "Wise Owl High School", "Hillcrest College", "Eaglesvale Senior School",
        "Kyle College", "Westridge High School", "Chisipite Senior School", "Hellenic Academy", "Kutama College", "St Ignatius College",
        "St John's College", "Ellis Robins School", "David Livingstone Primary School"
    ],
    "insurance": [
        "Zimnat", "Zimbabwe Insurance Brokers Limited", "Old Mutual Zimbabwe", "First Mutual Holdings", "NicozDiamond",
        "Fidelity Life Assurance", "Cell Insurance", "CBZ Insurance", "Alliance Insurance", "ZB Life Assurance", "Econet Insurance (EcoSure)",
        "Moonlight Funeral Assurance", "Doves Funeral Assurance", "Nyaradzo Group", "Heritage Insurance", "General Accident Insurance",
        "Global Alliance Insurance", "Charter Insurance", "Credsure Insurance", "Swan Insurance", "Marsh Zimbabwe"
    ],
    "utilities": [
        "Mwenje Solar", "Sona Solar Zimbabwe", "Distributed Power Africa", "Solar Shack", "Clamore Solar", "Azimuth Solar", "Vital Energy",
        "Powermaster Solar", "Samansco Solar", "Zonful Energy", "Solarpro Zimbabwe", "Frecon Solar", "Must Energy Zimbabwe", "Red Sphere Finance Solar",
        "Sunny Yi Feng Zimbabwe", "ZESA Holdings", "Zimbabwe Electricity Transmission and Distribution Company (ZETDC)", "Zimbabwe Power Company (ZPC)",
        "Rural Electrification Agency Zimbabwe", "Zimbabwe National Water Authority (ZINWA)", "City of Harare Water Department", "City of Bulawayo Water Services",
        "Petrotrade", "National Oil Infrastructure Company of Zimbabwe (NOIC)", "Zimbabwe Energy Regulatory Authority (ZERA)", "Environmental Management Agency (EMA)"
    ]
}

def seed_sources():
    db: Session = SessionLocal()
    added_count = 0
    skipped_count = 0
    
    try:
        for category, names in data.items():
            for name in names:
                name = name.strip()
                if not name:
                    continue
                    
                # Check if it exists
                existing = db.query(Source).filter(Source.name == name).first()
                if existing:
                    skipped_count += 1
                    continue
                
                # Create a placeholder URL slug
                slug = name.lower().replace(" ", "-").replace("'", "").replace("(", "").replace(")", "").replace(",", "")
                base_url = f"https://internal.local/{category}/{slug}"
                
                new_source = Source(
                    name=name,
                    category=category,
                    market="local",
                    base_url=base_url
                )
                db.add(new_source)
                added_count += 1
                
        db.commit()
        print(f"Successfully added {added_count} new sources.")
        print(f"Skipped {skipped_count} existing sources.")
        
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sources()
