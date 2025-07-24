"""
Flask Resume Generator - Static Site Generation

Project Structure:
resume_app/
├── app.py
├── resume_data.md
├── templates/
│   └── resume.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
│       └── logo.png
├── build/          # Generated static files
└── requirements.txt
"""

# app.py
from flask import Flask, render_template
import markdown
import yaml
import re
import os
from flask_frozen import Freezer

app = Flask(__name__)

# Configuration for static generation
app.config['FREEZER_DESTINATION'] = 'build'
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_IGNORE_MIMETYPE_WARNINGS'] = True

def parse_resume_markdown(file_path):
    """Parse markdown file with YAML frontmatter"""
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found. Using default data.")
        return {}, "# No resume data found"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split frontmatter and content
    if content.startswith('---'):
        try:
            _, frontmatter, markdown_content = content.split('---', 2)
            metadata = yaml.safe_load(frontmatter)
        except ValueError:
            metadata = {}
            markdown_content = content
    else:
        metadata = {}
        markdown_content = content
    
    return metadata, markdown_content

def parse_work_experience(content):
    """Parse work experience section into structured data"""
    companies = []
    company_sections = re.split(r'\n## ([^#\n]+)\n', content)
    
    for i in range(1, len(company_sections), 2):
        company_name = company_sections[i].strip()
        company_content = company_sections[i + 1].strip()
        
        # Extract position and duration
        lines = company_content.split('\n')
        position = ""
        duration = ""
        
        # Find position and duration lines
        for line in lines:
            if line.startswith('**Position:**'):
                position = line.replace('**Position:** ', '').strip()
            elif line.startswith('**Duration:**'):
                duration = line.replace('**Duration:** ', '').strip()
        
        # Extract achievements
        achievements = []
        current_main = None
        
        for line in lines:
            if line.startswith('- **') and line.endswith('**'):
                # Main achievement category
                line = line.strip("-: *")
                current_main = {
                    'category': line,  # Remove "- **" and ":**"
                    'item_list': []
                }
                achievements.append(current_main)
            elif line.startswith('  - ') and current_main:
                # Sub-achievement
                current_main['item_list'].append(line[4:])  # Remove "  - "
            elif line.startswith('- ') and not line.startswith('- **'):
                # Simple achievement
                achievements.append({'item': line[2:]})  # Remove "- "
        
        companies.append({
            'name': company_name,
            'position': position,
            'duration': duration,
            'achievements': achievements
        })
    
    return companies

def parse_skills(content):
    """Parse skills section into categories"""
    skills = {}
    current_category = None
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('### '):
            current_category = line[4:]  # Remove "### "
            skills[current_category] = []
        elif line.startswith('- ') and current_category:
            skills[current_category].append(line[2:])  # Remove "- "
    
    return skills

@app.route('/')
def resume():
    """Main resume route"""
    # Parse the markdown resume
    metadata, content = parse_resume_markdown('resume_data.md')
    
    # Default metadata if not provided
    default_metadata = {
        'name': 'John Doe',
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'phone': '+1 (555) 123-4567',
        'email': 'john.doe@email.com',
        'location': 'San Francisco, CA',
        'summary': 'Experienced software engineer with expertise in web development.',
        'education': {
            'degree': 'Bachelor of Computer Science',
            'university': 'University of Technology',
            'year': '2020'
        }
    }
    
    # Merge default with actual metadata
    for key, value in default_metadata.items():
        if key not in metadata:
            metadata[key] = value
    
    # Split content into sections
    sections = content.split('\n# ')
    
    # Parse each section
    work_experience = []
    skills = {}
    
    for section in sections:
        if section.startswith('Work Experience'):
            work_content = section.replace('Work Experience\n', '', 1)
            work_experience = parse_work_experience(work_content)
        elif section.startswith('Technical Skills'):
            skills_content = section.replace('Technical Skills\n', '', 1)
            skills = parse_skills(skills_content)
    
    return render_template('resume.html',
                         metadata=metadata,
                         work_experience=work_experience,
                         skills=skills)

def generate_static_site():
    """Generate static version of the site"""
    
    # Initialize Freezer
    freezer = Freezer(app)
    
    # Create build directory if it doesn't exist
    os.makedirs(app.config['FREEZER_DESTINATION'], exist_ok=True)
    
    try:
        # Generate static files
        freezer.freeze()
        print(f"Static site generated successfully in '{app.config['FREEZER_DESTINATION']}' directory!")
        print("\nGenerated files:")
        
        # List generated files
        for root, dirs, files in os.walk(app.config['FREEZER_DESTINATION']):
            for file in files:
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, app.config['FREEZER_DESTINATION'])
                print(f"{relative_path}")
                
    except Exception as e:
        print(f"Error generating static site: {e}")
        return False
    
    return True

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--static':
        # Generate static site
        generate_static_site()
    elif len(sys.argv) > 1 and sys.argv[1] == '--dev':
        # Run development server
        print("🚀 Starting development server...")
        print("📱 Visit http://localhost:5000 to view your resume")
        app.run(debug=True, port=5000)
    else:
        # Default: generate static site
        print("Flask Resume Generator")
        print("Usage:")
        print("  python app.py           # Generate static site (default)")
        print("  python app.py --static  # Generate static site")
        print("  python app.py --dev     # Run development server")
        print()
        generate_static_site()

# requirements.txt content:
"""
Flask==2.3.3
PyYAML==6.0.1
Markdown==3.5.1
Frozen-Flask==1.0.0
"""
