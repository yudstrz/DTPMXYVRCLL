import json
import re

def url_to_title(url):
    """Extract and format course title from URL."""
    # Extract the last part of the URL
    parts = url.rstrip('/').split('/')
    slug = parts[-1]
    
    # Replace hyphens and percent-encoded spaces with spaces
    title = slug.replace('-', ' ').replace('%20', ' ')
    
    # Capitalize words properly
    title = title.title()
    
    # Fix common abbreviations
    replacements = {
        'Ui Ux': 'UI/UX',
        'Ui/Ux': 'UI/UX',
        'Html Css': 'HTML & CSS',
        'Php': 'PHP',
        'Ai': 'AI',
        'Api': 'API',
        'Sql': 'SQL',
        'Mbc': 'MBC',
        'React Js': 'React.js',
        'Flask Python React Js': 'Flask (Python) & React.js',
        'Jitc': 'JITC',
        'Ppsdm': 'PPSDM',
        'Bbpvp': 'BBPVP',
        'Bpsdmi': 'BPSDMI',
        'Uad': 'UAD',
    }
    
    for old, new in replacements.items():
        title = title.replace(old, new)
    
    # Add "Bootcamp" or "Course" suffix if not present
    if 'bootcamp' not in title.lower() and 'course' not in title.lower():
        if 'belajar' in title.lower() or 'introduction' in title.lower():
            title = f"{title}"
        else:
            title = f"{title} Bootcamp"
    
    return title

# Load courses
with open('data/courses.json', 'r', encoding='utf-8') as f:
    courses = json.load(f)

# Update titles
for course in courses:
    if course['title'] == 'Unknown Course':
        course['title'] = url_to_title(course['url'])

# Save updated courses
with open('data/courses.json', 'w', encoding='utf-8') as f:
    json.dump(courses, f, indent=2, ensure_ascii=False)

print(f"✅ Updated {len(courses)} course titles!")
print("\nSample titles:")
for i, course in enumerate(courses[:10]):
    print(f"{i+1}. {course['title']}")
