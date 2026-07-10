#!/usr/bin/env python3
"""
Quick Setup Script for Zimbabwe Telecom Scraper
Installs dependencies and runs initial collection
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    packages = [
        'requests',
        'beautifulsoup4',
        'lxml',
        'pandas',
        'openpyxl',
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', package])
            print(f"  ✅ {package}")
        except subprocess.CalledProcessError:
            print(f"  ❌ Failed to install {package}")
            return False
    
    return True

def run_scraper():
    """Run the main scraper"""
    print("\n🌐 Running market intelligence scraper...")
    try:
        subprocess.check_call([sys.executable, 'advanced_telecom_scraper.py'])
        return True
    except subprocess.CalledProcessError:
        print("❌ Scraper failed")
        return False

def verify_outputs():
    """Verify that output files were created"""
    print("\n✅ Verifying outputs...")
    
    expected_files = [
        'zimbabwe_telecom_intelligence.csv',
        'zimbabwe_telecom_intelligence.json',
        'zimbabwe_telecom_intelligence.xlsx',
    ]
    
    all_exist = True
    for filename in expected_files:
        if os.path.exists(filename):
            size_kb = os.path.getsize(filename) / 1024
            print(f"  ✅ {filename} ({size_kb:.1f} KB)")
        else:
            print(f"  ❌ {filename} missing")
            all_exist = False
    
    return all_exist

def main():
    """Main setup flow"""
    print("=" * 60)
    print("🇿🇼 ZIMBABWE TELECOM MARKET INTELLIGENCE SCRAPER")
    print("=" * 60)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Step 1: Install dependencies
    print("\n[1/3] INSTALLING DEPENDENCIES")
    print("-" * 60)
    if not install_dependencies():
        print("\n❌ Installation failed. Please install manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 2: Run scraper
    print("\n[2/3] COLLECTING DATA")
    print("-" * 60)
    if not run_scraper():
        print("\n❌ Scraping failed")
        sys.exit(1)
    
    # Step 3: Verify outputs
    print("\n[3/3] VERIFYING OUTPUTS")
    print("-" * 60)
    if not verify_outputs():
        print("\n⚠️  Some output files missing")
        sys.exit(1)
    
    # Success
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\n📚 Documentation:")
    print("  • README.md - Overview and usage guide")
    print("  • SCHEMA.md - Data field definitions")
    print("  • MISSING_FIELDS_ANALYSIS.md - Field completion status")
    print("\n📊 Data Export Formats:")
    print("  • CSV: zimbabwe_telecom_intelligence.csv")
    print("  • JSON: zimbabwe_telecom_intelligence.json")
    print("  • Excel: zimbabwe_telecom_intelligence.xlsx")
    print("\n🚀 Next Steps:")
    print("  1. Review data: python -m pandas read_csv('zimbabwe_telecom_intelligence.csv')")
    print("  2. Open in Excel: zimbabwe_telecom_intelligence.xlsx")
    print("  3. Add new providers: Edit advanced_telecom_scraper.py")
    print("  4. Schedule updates: Use cron or Windows Task Scheduler")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
