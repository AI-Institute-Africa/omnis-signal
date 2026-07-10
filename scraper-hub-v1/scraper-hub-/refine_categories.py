import urllib.request
import json

# Current categories to new refined categories mapping
CATEGORY_MAPPING = {
    'education': ['schools', 'universities'],
    'energy': ['solar'],
    'transport': ['mobility', 'transport']
}

# New Zimbabwe sources based on refined categories
ADDITIONAL_ZIMBABWE_SOURCES = [
    # SCHOOLS (breaking down education)
    {
        "name": "Zimbabwe Schools Examination Council (ZIMSEC)",
        "category": "schools",
        "base_url": "https://www.zimsec.co.zw/",
        "schedule": "0 8 * * 1"  # Weekly on Monday
    },
    {
        "name": "Ministry of Primary and Secondary Education",
        "category": "schools",
        "base_url": "https://www.mopsce.gov.zw/",
        "schedule": "0 9 * * 1"  # Weekly on Monday
    },
    {
        "name": "Harare Institute of Technology",
        "category": "schools",
        "base_url": "https://www.hit.ac.zw/",
        "schedule": "0 10 * * 1"  # Weekly on Monday
    },

    # UNIVERSITIES (breaking down education)
    {
        "name": "University of Zimbabwe - Fees",
        "category": "universities",
        "base_url": "https://www.uz.ac.zw/fees-structure/",
        "schedule": "0 8 * * 2"  # Weekly on Tuesday
    },
    {
        "name": "National University of Science and Technology",
        "category": "universities",
        "base_url": "https://www.nust.ac.zw/",
        "schedule": "0 9 * * 2"  # Weekly on Tuesday
    },
    {
        "name": "Midlands State University",
        "category": "universities",
        "base_url": "https://www.msu.ac.zw/",
        "schedule": "0 10 * * 2"  # Weekly on Tuesday
    },
    {
        "name": "Chinhoyi University of Technology",
        "category": "universities",
        "base_url": "https://www.cut.ac.zw/",
        "schedule": "0 11 * * 2"  # Weekly on Tuesday
    },

    # SOLAR (refining energy)
    {
        "name": "Zimbabwe Energy Regulatory Authority - Solar",
        "category": "solar",
        "base_url": "https://www.zera.co.zw/renewable-energy/solar/",
        "schedule": "0 14 * * 3"  # Weekly on Wednesday
    },
    {
        "name": "Green Solar Solutions Zimbabwe",
        "category": "solar",
        "base_url": "https://www.greensolar.co.zw/",
        "schedule": "0 15 * * 3"  # Weekly on Wednesday
    },

    # MOBILITY (refining transport)
    {
        "name": "Zimbabwe Revenue Authority - Vehicle Registration",
        "category": "mobility",
        "base_url": "https://www.zimra.co.zw/vehicle-registration/",
        "schedule": "0 8 * * 4"  # Weekly on Thursday
    },
    {
        "name": "Driving Schools Association of Zimbabwe",
        "category": "mobility",
        "base_url": "https://www.dsaz.co.zw/",
        "schedule": "0 9 * * 4"  # Weekly on Thursday
    },
    {
        "name": "Auto Zimbabwe - Car Dealerships",
        "category": "mobility",
        "base_url": "https://www.autozimbabwe.com/",
        "schedule": "0 10 * * 4"  # Weekly on Thursday
    },
    {
        "name": "Zimbabwe Bus Services",
        "category": "mobility",
        "base_url": "https://www.zimbabwebus.com/",
        "schedule": "0 11 * * 4"  # Weekly on Thursday
    }
]

def update_existing_sources():
    """Update existing sources to use refined categories"""
    try:
        # Get all sources
        with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/sources/', timeout=10) as response:
            sources = json.loads(response.read().decode())

        print(f"Found {len(sources)} existing sources")

        # Update categories for existing sources
        updates_made = 0
        for source in sources:
            old_category = source['category'].lower()
            if old_category in CATEGORY_MAPPING:
                # For education -> split into schools/universities
                if old_category == 'education':
                    # Simple heuristic: if "university" in name, make it universities, else schools
                    if 'university' in source['name'].lower() or 'college' in source['name'].lower():
                        new_category = 'universities'
                    else:
                        new_category = 'schools'
                # For energy -> solar
                elif old_category == 'energy':
                    new_category = 'solar'
                # For transport -> split based on content
                elif old_category == 'transport':
                    if any(keyword in source['name'].lower() for keyword in ['bus', 'route', 'passenger']):
                        new_category = 'mobility'
                    else:
                        new_category = 'transport'

                if source['category'] != new_category:
                    # Update the source
                    update_data = {"category": new_category}
                    data = json.dumps(update_data).encode('utf-8')
                    req = urllib.request.Request(
                        f"http://127.0.0.1:8000/api/v1/sources/{source['id']}",
                        data=data,
                        headers={'Content-Type': 'application/json'},
                        method='PATCH'
                    )

                    try:
                        with urllib.request.urlopen(req, timeout=10) as response:
                            if response.getcode() == 200:
                                print(f"✅ Updated {source['name']}: {source['category']} → {new_category}")
                                updates_made += 1
                            else:
                                print(f"❌ Failed to update {source['name']}")
                    except Exception as e:
                        print(f"❌ Error updating {source['name']}: {e}")

        print(f"\nUpdated {updates_made} existing sources")

    except Exception as e:
        print(f"Error updating existing sources: {e}")

def add_new_sources():
    """Add new sources for refined categories"""
    print(f"\n=== Adding {len(ADDITIONAL_ZIMBABWE_SOURCES)} New Sources ===")

    added_count = 0
    for source in ADDITIONAL_ZIMBABWE_SOURCES:
        try:
            data = json.dumps(source).encode('utf-8')
            req = urllib.request.Request(
                'http://127.0.0.1:8000/api/v1/sources/',
                data=data,
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    result = json.loads(response.read().decode())
                    print(f"✅ Added: {source['name']} (ID: {result['id']}, Category: {source['category']})")
                    added_count += 1
                else:
                    print(f"❌ Failed to add: {source['name']}")

        except Exception as e:
            print(f"❌ Error adding {source['name']}: {e}")

    print(f"\nSuccessfully added {added_count}/{len(ADDITIONAL_ZIMBABWE_SOURCES)} new sources")

if __name__ == "__main__":
    print("🔄 Updating Scraper Hub Categories and Sources")
    print("=" * 50)

    update_existing_sources()
    add_new_sources()

    print("\n✅ Category refinement complete!")
    print("Run 'python show_dashboard.py' to see updated statistics")