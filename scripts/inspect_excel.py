import pandas as pd
import os

xlsx_path = os.path.join('data', 'DTP_Database.xlsx')

if os.path.exists(xlsx_path):
    print(f"Inspecting {xlsx_path}...")
    try:
        xls = pd.ExcelFile(xlsx_path)
        print(f"Sheet names: {xls.sheet_names}")
        
        for sheet in xls.sheet_names:
            df = pd.read_excel(xlsx_path, sheet_name=sheet, nrows=5)
            print(f"\n--- Sheet: {sheet} ---")
            print(f"Columns: {list(df.columns)}")
            print(df.head(2))
            
    except Exception as e:
        print(f"Error reading Excel: {e}")
else:
    print("File not found.")
