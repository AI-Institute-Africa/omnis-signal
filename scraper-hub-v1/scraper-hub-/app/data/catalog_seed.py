import uuid
from app.db.session import SessionLocal
from app.db.models.catalog import (
    SectorConfig, Category, AttributeSchemaField,
    SectorStatus, CategoryLevel, AttributeDataType, QualityAxis
)

def _uid(): return str(uuid.uuid4())

SECTORS = [
    {
        'name': 'Banking', 'slug': 'banking', 'icon': 'building-2',
        'blurb': 'Compare bank fees, charges, accounts and loan rates',
        'categories': [
            {'name': 'Current Accounts', 'slug': 'current_accounts', 'synonyms': ['cheque account', 'transactional account'], 'fields': [
                {'key': 'monthly_fee', 'label': 'Monthly Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'minimum_balance', 'label': 'Minimum Balance', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'overdraft_limit', 'label': 'Overdraft Limit', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 3, 'quality_axis': QualityAxis.VALUE},
                {'key': 'atm_withdrawal_fee', 'label': 'ATM Withdrawal Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 4, 'quality_axis': QualityAxis.VALUE},
                {'key': 'internet_banking_fee', 'label': 'Internet Banking Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 5, 'quality_axis': QualityAxis.VALUE},
                {'key': 'mobile_banking_fee', 'label': 'Mobile Banking Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 6, 'quality_axis': QualityAxis.VALUE},
                {'key': 'bank_type', 'label': 'Bank Type', 'data_type': AttributeDataType.ENUM, 'sort_order': 7, 'is_comparable': False},
            ]},
            {'name': 'Savings Accounts', 'slug': 'savings_accounts', 'synonyms': ['deposit account', 'savings'], 'fields': [
                {'key': 'interest_rate', 'label': 'Interest Rate', 'data_type': AttributeDataType.NUMBER, 'unit': '% p.a.', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'monthly_fee', 'label': 'Monthly Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'minimum_balance', 'label': 'Minimum Balance', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 3, 'quality_axis': QualityAxis.VALUE},
                {'key': 'withdrawal_limit', 'label': 'Monthly Withdrawal Limit', 'data_type': AttributeDataType.NUMBER, 'sort_order': 4, 'quality_axis': QualityAxis.AVAILABILITY},
            ]},
            {'name': 'Cash Withdrawals', 'slug': 'cash_withdrawals', 'synonyms': ['ATM withdrawal', 'cash out'], 'fields': [
                {'key': 'atm_own_bank_fee', 'label': 'ATM Own Bank Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'atm_other_bank_fee', 'label': 'ATM Other Bank Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'branch_fee', 'label': 'Branch Withdrawal Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 3, 'quality_axis': QualityAxis.VALUE},
                {'key': 'max_daily_limit', 'label': 'Daily Limit', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 4, 'quality_axis': QualityAxis.AVAILABILITY},
            ]},
            {'name': 'Transfers & Payments', 'slug': 'transfers', 'synonyms': ['RTGS', 'EFT', 'ZIPIT'], 'fields': [
                {'key': 'rtgs_fee', 'label': 'RTGS Transfer Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'eft_fee', 'label': 'EFT / ZIPIT Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'swift_fee', 'label': 'SWIFT / International Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 3, 'quality_axis': QualityAxis.VALUE},
            ]},
            {'name': 'Mobile Banking', 'slug': 'mobile_banking', 'synonyms': ['mobile money', 'USSD'], 'channel': 'mobile_banking', 'fields': [
                {'key': 'monthly_fee', 'label': 'Monthly Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'transaction_fee', 'label': 'Transaction Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'daily_limit', 'label': 'Daily Limit', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 3, 'quality_axis': QualityAxis.AVAILABILITY},
            ]},
            {'name': 'Loans & Credit', 'slug': 'loans', 'synonyms': ['loan', 'credit', 'mortgage'], 'fields': [
                {'key': 'interest_rate', 'label': 'Interest Rate', 'data_type': AttributeDataType.NUMBER, 'unit': '% p.a.', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'max_loan_amount', 'label': 'Maximum Loan Amount', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 2, 'quality_axis': QualityAxis.AVAILABILITY},
                {'key': 'processing_fee', 'label': 'Processing Fee', 'data_type': AttributeDataType.NUMBER, 'unit': '%', 'sort_order': 3, 'quality_axis': QualityAxis.VALUE},
            ]},
            {'name': 'Card Services', 'slug': 'card_services', 'synonyms': ['debit card', 'credit card', 'visa'], 'fields': [
                {'key': 'annual_fee', 'label': 'Annual Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'card_type', 'label': 'Card Type', 'data_type': AttributeDataType.ENUM, 'sort_order': 2, 'is_comparable': False},
                {'key': 'atm_fee', 'label': 'ATM Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 3, 'quality_axis': QualityAxis.VALUE},
            ]}
        ]
    },
    {
        'name': 'Hotels', 'slug': 'hotels', 'icon': 'hotel',
        'blurb': 'Compare hotel room rates, lodges, conference packages and amenities',
        'categories': [
            {'name': 'Standard Rooms', 'slug': 'standard_rooms', 'synonyms': ['single room', 'double room'], 'fields': [
                {'key': 'room_rate', 'label': 'Room Rate per Night', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'breakfast_included', 'label': 'Breakfast Included', 'data_type': AttributeDataType.BOOLEAN, 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'wifi_included', 'label': 'WiFi Included', 'data_type': AttributeDataType.BOOLEAN, 'sort_order': 3, 'quality_axis': QualityAxis.AVAILABILITY},
                {'key': 'star_rating', 'label': 'Star Rating', 'data_type': AttributeDataType.NUMBER, 'unit': 'stars', 'sort_order': 4, 'quality_axis': QualityAxis.TRUST},
            ]},
            {'name': 'Deluxe Rooms', 'slug': 'deluxe_rooms', 'synonyms': ['luxury room', 'superior room'], 'fields': [
                {'key': 'room_rate', 'label': 'Room Rate per Night', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'breakfast_included', 'label': 'Breakfast Included', 'data_type': AttributeDataType.BOOLEAN, 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'pool_access', 'label': 'Pool Access', 'data_type': AttributeDataType.BOOLEAN, 'sort_order': 3, 'quality_axis': QualityAxis.AVAILABILITY},
            ]},
            {'name': 'Conference & Events', 'slug': 'conference_packages', 'synonyms': ['meeting room', 'banquet'], 'fields': [
                {'key': 'day_delegate_rate', 'label': 'Day Delegate Rate', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD/person', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'capacity', 'label': 'Max Capacity', 'data_type': AttributeDataType.NUMBER, 'unit': 'delegates', 'sort_order': 2},
            ]}
        ]
    },
    {
        'name': 'Education', 'slug': 'education', 'icon': 'graduation-cap',
        'blurb': 'Compare school fees, university tuition, boarding and academic programmes',
        'categories': [
            {'name': 'Primary Schools', 'slug': 'primary_schools', 'synonyms': ['prep school', 'grade 1-7'], 'fields': [
                {'key': 'annual_tuition', 'label': 'Annual Tuition Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'curriculum', 'label': 'Curriculum', 'data_type': AttributeDataType.ENUM, 'sort_order': 2, 'quality_axis': QualityAxis.TRUST, 'is_comparable': False},
                {'key': 'boarding_fee', 'label': 'Boarding Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD/term', 'sort_order': 3, 'quality_axis': QualityAxis.VALUE},
            ]},
            {'name': 'Secondary Schools', 'slug': 'secondary_schools', 'synonyms': ['high school', 'form 1-6'], 'fields': [
                {'key': 'annual_tuition', 'label': 'Annual Tuition Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'boarding_fee', 'label': 'Boarding Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD/term', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'curriculum', 'label': 'Curriculum', 'data_type': AttributeDataType.ENUM, 'sort_order': 3, 'quality_axis': QualityAxis.TRUST, 'is_comparable': False},
            ]},
            {'name': 'Tertiary & University', 'slug': 'tertiary_fees', 'synonyms': ['degree', 'diploma', 'undergraduate'], 'fields': [
                {'key': 'annual_tuition', 'label': 'Annual Tuition', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'programme_type', 'label': 'Programme Type', 'data_type': AttributeDataType.ENUM, 'sort_order': 2, 'is_comparable': False},
                {'key': 'accreditation', 'label': 'Accredited', 'data_type': AttributeDataType.BOOLEAN, 'sort_order': 3, 'quality_axis': QualityAxis.TRUST},
            ]}
        ]
    },
    {
        'name': 'Transport', 'slug': 'transport', 'icon': 'bus',
        'blurb': 'Compare bus fares, fuel prices, taxi rates, car rentals and logistics',
        'categories': [
            {'name': 'Bus & Coach Fares', 'slug': 'bus_fares', 'synonyms': ['coach ticket', 'intercity bus'], 'fields': [
                {'key': 'base_fare', 'label': 'Base Fare', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'route', 'label': 'Route', 'data_type': AttributeDataType.STRING, 'sort_order': 2, 'is_comparable': False},
                {'key': 'air_conditioned', 'label': 'Air Conditioned', 'data_type': AttributeDataType.BOOLEAN, 'sort_order': 3, 'quality_axis': QualityAxis.PERFORMANCE},
            ]},
            {'name': 'Fuel Prices', 'slug': 'fuel_prices', 'synonyms': ['petrol', 'diesel', 'zera fuel'], 'fields': [
                {'key': 'price_per_litre', 'label': 'Price per Litre', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD/L', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'fuel_type', 'label': 'Fuel Type', 'data_type': AttributeDataType.ENUM, 'sort_order': 2, 'is_comparable': False},
            ]},
            {'name': 'Taxi & Ride Rates', 'slug': 'taxi_rates', 'synonyms': ['inDrive', 'cab fare'], 'fields': [
                {'key': 'base_fare', 'label': 'Base Fare', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'per_km_rate', 'label': 'Rate per km', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD/km', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
            ]}
        ]
    },
    {
        'name': 'Retail', 'slug': 'retail', 'icon': 'shopping-cart',
        'blurb': 'Compare supermarket prices, electronics, clothing and groceries',
        'categories': [
            {'name': 'Groceries & Supermarkets', 'slug': 'groceries', 'synonyms': ['supermarket', 'cooking oil', 'sugar', 'mealie meal'], 'fields': [
                {'key': 'unit_price', 'label': 'Unit Price', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'brand', 'label': 'Brand', 'data_type': AttributeDataType.STRING, 'sort_order': 2, 'is_comparable': False},
                {'key': 'local_or_import', 'label': 'Local or Imported', 'data_type': AttributeDataType.ENUM, 'sort_order': 3, 'is_comparable': False},
                {'key': 'in_stock', 'label': 'In Stock', 'data_type': AttributeDataType.BOOLEAN, 'sort_order': 4, 'quality_axis': QualityAxis.AVAILABILITY},
            ]},
            {'name': 'Electronics & Appliances', 'slug': 'electronics', 'synonyms': ['laptops', 'smartphones', 'solar batteries'], 'fields': [
                {'key': 'unit_price', 'label': 'Unit Price', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'brand', 'label': 'Brand', 'data_type': AttributeDataType.STRING, 'sort_order': 2, 'is_comparable': False},
                {'key': 'warranty_months', 'label': 'Warranty (months)', 'data_type': AttributeDataType.NUMBER, 'unit': 'months', 'sort_order': 3, 'quality_axis': QualityAxis.TRUST},
            ]}
        ]
    },
    {
        'name': 'Food & Dining', 'slug': 'food', 'icon': 'utensils',
        'blurb': 'Compare restaurant meals, fast food menus, delivery fees and catering',
        'categories': [
            {'name': 'Fast Food & Takeaways', 'slug': 'fast_food', 'synonyms': ['fried chicken', 'burger', 'pizza'], 'fields': [
                {'key': 'meal_price', 'label': 'Meal Price', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'cuisine_type', 'label': 'Cuisine Type', 'data_type': AttributeDataType.ENUM, 'sort_order': 2, 'is_comparable': False},
                {'key': 'delivery_fee', 'label': 'Delivery Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 3, 'quality_axis': QualityAxis.VALUE},
            ]},
            {'name': 'Restaurants & Dining', 'slug': 'restaurants', 'synonyms': ['fine dining', 'buffet'], 'fields': [
                {'key': 'meal_price', 'label': 'Main Dish Price', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'hygiene_rating', 'label': 'Hygiene Rating', 'data_type': AttributeDataType.NUMBER, 'unit': 'stars', 'sort_order': 2, 'quality_axis': QualityAxis.TRUST},
            ]}
        ]
    },
    {
        'name': 'Telecoms', 'slug': 'telecom', 'icon': 'wifi',
        'blurb': 'Compare mobile data bundles, voice tariffs, SMS, fibre internet and LTE plans',
        'categories': [
            {'name': 'Data Bundles', 'slug': 'data_bundles', 'synonyms': ['daily bundle', 'monthly data', 'gigabytes'], 'fields': [
                {'key': 'data_mb', 'label': 'Data (MB)', 'data_type': AttributeDataType.NUMBER, 'unit': 'MB', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'price', 'label': 'Price', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'validity_days', 'label': 'Validity (days)', 'data_type': AttributeDataType.NUMBER, 'unit': 'days', 'sort_order': 3},
                {'key': 'night_only', 'label': 'Night Bundle', 'data_type': AttributeDataType.BOOLEAN, 'sort_order': 4},
                {'key': 'network', 'label': 'Network', 'data_type': AttributeDataType.ENUM, 'sort_order': 5, 'is_comparable': False},
            ]},
            {'name': 'Voice Calls', 'slug': 'voice_calls', 'synonyms': ['call rates', 'voice tariff'], 'fields': [
                {'key': 'rate_per_min', 'label': 'Rate per Minute', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD/min', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'on_net_rate', 'label': 'On-Net Rate', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD/min', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'off_net_rate', 'label': 'Off-Net Rate', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD/min', 'sort_order': 3, 'quality_axis': QualityAxis.VALUE},
                {'key': 'network', 'label': 'Network', 'data_type': AttributeDataType.ENUM, 'sort_order': 4, 'is_comparable': False},
            ]},
            {'name': 'SMS', 'slug': 'sms', 'synonyms': ['text message', 'bulk sms'], 'fields': [
                {'key': 'rate_per_sms', 'label': 'Rate per SMS', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 1, 'quality_axis': QualityAxis.VALUE},
                {'key': 'network', 'label': 'Network', 'data_type': AttributeDataType.ENUM, 'sort_order': 2, 'is_comparable': False},
            ]},
            {'name': 'Fibre Internet', 'slug': 'fibre_internet', 'synonyms': ['FTTH', 'liquid fibre', 'telone fibre'], 'fields': [
                {'key': 'speed_mbps', 'label': 'Speed (Mbps)', 'data_type': AttributeDataType.NUMBER, 'unit': 'Mbps', 'sort_order': 1, 'quality_axis': QualityAxis.PERFORMANCE},
                {'key': 'monthly_price', 'label': 'Monthly Price', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
                {'key': 'data_cap_gb', 'label': 'Data Cap (GB)', 'data_type': AttributeDataType.NUMBER, 'unit': 'GB', 'sort_order': 3, 'quality_axis': QualityAxis.AVAILABILITY},
                {'key': 'installation_fee', 'label': 'Installation Fee', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 4, 'quality_axis': QualityAxis.VALUE},
            ]},
            {'name': 'Wireless / LTE Internet', 'slug': 'wireless_internet', 'synonyms': ['MiFi', 'LTE router', 'starlink'], 'fields': [
                {'key': 'speed_mbps', 'label': 'Speed (Mbps)', 'data_type': AttributeDataType.NUMBER, 'unit': 'Mbps', 'sort_order': 1, 'quality_axis': QualityAxis.PERFORMANCE},
                {'key': 'monthly_price', 'label': 'Monthly Price', 'data_type': AttributeDataType.NUMBER, 'unit': 'USD', 'sort_order': 2, 'quality_axis': QualityAxis.VALUE},
            ]}
        ]
    }
]

def seed_catalog(db=None):
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        print('[Catalog Seed] Starting seed...')
        for sec in SECTORS:
            s = db.query(SectorConfig).filter(SectorConfig.slug == sec['slug']).first()
            if not s:
                s = SectorConfig(id=_uid(), name=sec['name'], slug=sec['slug'], status=SectorStatus.LIVE, icon=sec.get('icon'), blurb=sec.get('blurb'))
                db.add(s)
                db.flush()
                print(f'  [+] Sector: {s.name}')
            else:
                s.status = SectorStatus.LIVE
                s.icon = sec.get('icon')
                s.blurb = sec.get('blurb')

            for cat in sec.get('categories', []):
                c = db.query(Category).filter(Category.sector_id == s.id, Category.slug == cat['slug']).first()
                if not c:
                    c = Category(id=_uid(), sector_id=s.id, name=cat['name'], slug=cat['slug'], level=cat.get('level', CategoryLevel.STANDARD), channel=cat.get('channel'))
                    c.synonyms = cat.get('synonyms', [])
                    db.add(c)
                    db.flush()
                    print(f'    [+] Category: {c.name}')
                else:
                    c.synonyms = cat.get('synonyms', [])
                    c.channel = cat.get('channel')

                for f in cat.get('fields', []):
                    attr = db.query(AttributeSchemaField).filter(AttributeSchemaField.category_id == c.id, AttributeSchemaField.key == f['key']).first()
                    if not attr:
                        attr = AttributeSchemaField(
                            id=_uid(), category_id=c.id, key=f['key'], label=f['label'],
                            consumer_label=f.get('consumer_label'), data_type=f.get('data_type', AttributeDataType.STRING),
                            unit=f.get('unit'), sort_order=f.get('sort_order', 0), quality_axis=f.get('quality_axis'),
                            is_comparable=f.get('is_comparable', True)
                        )
                        db.add(attr)
        db.commit()
        print('[Catalog Seed] All 7 sectors, categories, and attributes seeded successfully!')
    except Exception as e:
        db.rollback()
        print(f'[Catalog Seed] ERROR: {e}')
        raise
    finally:
        if own_session:
            db.close()

if __name__ == '__main__':
    seed_catalog()
