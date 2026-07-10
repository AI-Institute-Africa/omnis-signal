
import re
from bs4 import BeautifulSoup

content = """
Title: ZIMSEC A Level Results 2026 November - Top 100 Schools
Description: Zimbabwe School Examinations Council (ZIMSEC) will release A Level Results 2026 November examination with top 100 Schools list in the month of December 2026.
The number of school candidates was 32 764 and for private candidates, it was 8 889. The number of candidates who sat for two or more subjects was 33 579, which is 80, 6% of the total candidature of 41 653.
The total number of candidates who sat for the November ‘A’ level 2015 examination was 41 653 as compared 39 133 in November 2014. The candidature increased by 2 520, an increase of 6, 4 %. The number of candidates who obtained Grade E or better in one or more subjects was 38 873. This gives a percentage of 93, 3%.
"""

soup = BeautifulSoup(content, 'html.parser')
page_text = content.lower()

def debug_extract():
    records = []
    # Match percentages: e.g., 93.3%, 93, 3%
    # Using the same logic as in EducationExtractor
    for p in [content]: # Simulating paragraph search
        text = p.strip()
        
        print(f"Checking text: {text[:100]}...")
        
        # Pass rate match
        matches = re.finditer(r'(\d{1,3}(?:[.,]\s*\d+)?)\s*%', text)
        for pass_rate_match in matches:
            val_str = pass_rate_match.group(1).replace(' ', '').replace(',', '.')
            print(f"Found percentage match: {pass_rate_match.group(0)} -> {val_str}")
            try:
                val = float(val_str)
                if 0 <= val <= 100:
                    title = "Overall Pass Rate"
                    if 'candidates' in text.lower():
                        title = "Candidate Pass Rate"
                    records.append({"title": title, "value": val, "currency": "%"})
            except Exception as e:
                print(f"Float conversion error: {e}")

        # Candidate count match
        c_matches = re.finditer(r'(?:total\s+)?(?:number\s+of\s+)?candidates\s+(?:was|is|sat)\s+([\d\s,]+)', text, re.I)
        for candidate_match in c_matches:
            val_str = candidate_match.group(1).replace(' ', '').replace(',', '')
            print(f"Found candidate match: {candidate_match.group(0)} -> {val_str}")
            try:
                val = float(val_str)
                records.append({"title": "Total Candidates", "value": val, "currency": "count"})
            except Exception as e:
                print(f"Float conversion error: {e}")

    return records

results = debug_extract()
print("\nFinal Results:")
for r in results:
    print(r)
