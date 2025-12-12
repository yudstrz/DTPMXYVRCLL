import pandas as pd
import json
import os

DATA_DIR = os.path.join(os.getcwd(), 'data')
XLSX_PATH = os.path.join(DATA_DIR, 'DTP_Database.xlsx')
OUTPUT_PATH = os.path.join(DATA_DIR, 'courses.json')

def extract_courses():
    if not os.path.exists(XLSX_PATH):
        print(f"File not found: {XLSX_PATH}")
        return

    print(f"Extracting courses from {XLSX_PATH}...")
    try:
        df = pd.read_excel(XLSX_PATH, sheet_name='Course_Maxy')
        df = df.fillna("")
        
        courses = []
        for _, row in df.iterrows():
            courses.append({
                "title": row.get('Nama_Course', 'Unknown'),
                "provider": "Maxy Academy",
                "level": row.get('Level', 'All Levels'),
                "duration": row.get('Duration', 'Self-paced'),
                "image": row.get('Image_URL', 'https://placehold.co/600x400/orange/white?text=Maxy+Course'),
                "url": row.get('URL', '#')
            })
            
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(courses, f, indent=2)
            
        print(f"Successfully saved {len(courses)} courses to {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_courses()
