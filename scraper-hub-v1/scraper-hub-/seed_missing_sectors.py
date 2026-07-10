from app.db.session import SessionLocal
from app.db.models.organization import Organization
from datetime import datetime

def seed_hospitals():
    db = SessionLocal()
    
    hospitals = [
        {
            "name": "The Avenues Clinic",
            "slug": "the-avenues-clinic",
            "category": "hospitals",
            "website": "https://www.avenuesclinic.co.zw",
            "description": "Premium private hospital in Harare providing comprehensive medical services."
        },
        {
            "name": "Parirenyatwa Group of Hospitals",
            "slug": "parirenyatwa-group",
            "category": "hospitals",
            "website": "http://www.pari.org.zw",
            "description": "The largest referral hospital in Zimbabwe."
        },
        {
            "name": "West End Hospital",
            "slug": "west-end-hospital",
            "category": "hospitals",
            "website": "https://www.psmi.co.zw/west-end-hospital",
            "description": "A leading private medical facility in Harare."
        },
        {
            "name": "Corporate 24 Hospital Group",
            "slug": "corporate-24-hospital",
            "category": "hospitals",
            "website": "https://www.corp24med.com",
            "description": "24-hour private emergency and general hospital."
        }
    ]
    
    for h_data in hospitals:
        existing = db.query(Organization).filter(Organization.slug == h_data["slug"]).first()
        if not existing:
            h = Organization(**h_data)
            db.add(h)
            print(f"Added hospital: {h_data['name']}")
    
    # Ensure Universities are categorized correctly (some might be under 'colleges')
    # Actually, let's just make sure we have the big ones
    universities = [
        {"name": "University of Zimbabwe", "slug": "uz", "category": "universities", "website": "https://www.uz.ac.zw"},
        {"name": "National University of Science and Technology", "slug": "nust", "category": "universities", "website": "https://www.nust.ac.zw"},
        {"name": "Midlands State University", "slug": "msu", "category": "universities", "website": "https://www.msu.ac.zw"}
    ]
    for u_data in universities:
        existing = db.query(Organization).filter(Organization.slug == u_data["slug"]).first()
        if not existing:
            u = Organization(**u_data)
            db.add(u)
            print(f"Added university: {u_data['name']}")
            
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_hospitals()
