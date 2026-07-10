import os
import pandas as pd
print('ROOT=', os.getcwd())
print('\n--- view_zimbabwe_data.py output ---\n')
import view_zimbabwe_data
print('\n--- CSV file info ---\n')
path = 'zimbabwe_telecom_intelligence.csv'
print('csv exists=', os.path.exists(path))
if os.path.exists(path):
    print('csv size=', os.path.getsize(path))
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for _ in range(5):
            print(f.readline().rstrip())
