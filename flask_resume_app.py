"""
Flask Resume Generator - Project Structure and Implementation

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
└── requirements.txt
"""

# app.py
from flask import Flask, render_template
import markdown
import yaml
import re
import sys

app = Flask(__name__)

def parse_resume_markdown(file_path):
    """Parse markdown file with YAML frontmatter"""
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
    # Split by company sections
    companies = []
    company_sections = re.split(r'\n## ([^#\n]+)\n', content)
    
    for i in range(1, len(company_sections), 2):
        company_name = company_sections[i].strip()
        company_content = company_sections[i + 1].strip()
        # Extract position and duration
        lines = company_content.split('\n')
        position = lines[0].replace('**Position:** ', '')
        duration = lines[1].replace('**Duration:** ', '')
        
        # Extract achievements
        achievements = []
        current_main = None
        
        for line in lines[2:]:
            line = line

            if line.startswith('- **') and line.endswith(':**'):
                # Main achievement category
                current_main = {
                    'category': line[4:-3],  # Remove "- **" and ":**"
                    'item_list': []
                }
                achievements.append(current_main)
            elif line.startswith('  - ') and current_main:
                # Sub-achievement
                current_main['item_list'].append(line[4:])  # Remove "  - "
            elif line.startswith('- '):
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
        elif line.startswith('- '):
            if current_category:
                skills[current_category].append(line[2:])  # Remove "- "
    
    return skills

@app.route('/')
def resume():
    # Parse the markdown resume
    metadata, content = parse_resume_markdown('resume_data.md')
    
    # Split content into sections
    sections = content.split('\n# ')
    
    # Parse each section
    work_experience = []
    skills = {}
    
    for section in sections[1:]:  # Skip first empty section
        if section.startswith('Work Experience'):
            work_content = section.replace('Work Experience\n', '')
            work_experience = parse_work_experience(work_content)
        elif section.startswith('Technical Skills'):
            skills_content = section.replace('Technical Skills\n', '')
            skills = parse_skills(skills_content)
    
    return render_template('resume.html',
                         metadata=metadata,
                         work_experience=work_experience,
                         skills=skills)

if __name__ == '__main__':
    app.run(debug=True)

# requirements.txt content:
"""
Flask==2.3.3
PyYAML==6.0.1
Markdown==3.5.1
"""
