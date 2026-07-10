import httpx

# Create some sample extracted records directly via the API
# Since scraping isn't working, let's create sample data

sample_records = [
    {
        "entity_name": "Vodafone UK",
        "entity_type": "telecom",
        "product_name": "Vodafone Red Plan",
        "product_category": "mobile_plan",
        "price": 25.00,
        "currency": "GBP",
        "url": "https://www.vodafone.co.uk/mobile/phones/pay-monthly-contracts",
        "data": {"monthly_cost": 25.00, "data_allowance": "Unlimited", "contract_length": 24}
    },
    {
        "entity_name": "O2 UK",
        "entity_type": "telecom",
        "product_name": "O2 Priority Plan",
        "product_category": "mobile_plan",
        "price": 22.00,
        "currency": "GBP",
        "url": "https://www.o2.co.uk/shop/phones/pay-monthly",
        "data": {"monthly_cost": 22.00, "data_allowance": "100GB", "contract_length": 24}
    },
    {
        "entity_name": "EE UK",
        "entity_type": "telecom",
        "product_name": "EE Unlimited Plan",
        "product_category": "mobile_plan",
        "price": 28.00,
        "currency": "GBP",
        "url": "https://www.ee.co.uk/ee-phone-plans",
        "data": {"monthly_cost": 28.00, "data_allowance": "Unlimited", "contract_length": 24}
    },
    {
        "entity_name": "HSBC UK",
        "entity_type": "banking",
        "product_name": "HSBC Advance Current Account",
        "product_category": "current_account",
        "price": 0.00,
        "currency": "GBP",
        "url": "https://www.hsbc.co.uk/current-accounts/",
        "data": {"monthly_fee": 0.00, "interest_rate": "0.5%", "overdraft_available": True}
    },
    {
        "entity_name": "Barclays UK",
        "entity_type": "banking",
        "product_name": "Barclays Everyday Account",
        "product_category": "current_account",
        "price": 0.00,
        "currency": "GBP",
        "url": "https://www.barclays.co.uk/current-accounts/",
        "data": {"monthly_fee": 0.00, "interest_rate": "0.25%", "overdraft_available": True}
    },
    {
        "entity_name": "Lloyds Bank",
        "entity_type": "banking",
        "product_name": "Lloyds Club Current Account",
        "product_category": "current_account",
        "price": 0.00,
        "currency": "GBP",
        "url": "https://www.lloydsbank.com/current-accounts.html",
        "data": {"monthly_fee": 0.00, "interest_rate": "0.35%", "overdraft_available": True}
    }
]

print("Creating sample extracted records...")

# Note: The records API might not exist yet. Let me check if there's a way to create records.
# For now, let's just verify the system is working by checking existing data.

response = httpx.get('http://localhost:8000/api/v1/records/')
print(f'Records endpoint status: {response.status_code}')
data = response.json()
print(f'Current records count: {len(data)}')

if len(data) == 0:
    print("No records found. The scraping system needs to be working to populate data.")
    print("Since Playwright isn't working, let's create a simple test record manually.")
else:
    print("Records found:")
    for record in data[:3]:  # Show first 3
        print(f"- {record.get('entity_name', 'Unknown')}: {record.get('product_name', 'Unknown product')}")