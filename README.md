# MicroRidge Technology Resume Site

A Flask-based static site generator for Joel Vandergriendt's professional resume and portfolio.

## Quick Start

Run the build script to generate the static site:

```bash
./build.sh
```

This will:
- Set up a Python virtual environment
- Install dependencies (Flask, PyYAML, Markdown, Frozen-Flask)
- Generate static HTML files from the resume data

## Structure

- `resume_data.md` - Resume content in Markdown format
- `flask_resume_app.py` - Flask application for static generation
- `templates/resume.html` - HTML template
- `static/` - CSS styles and images
- `docs/` - Generated static site files

## Deployment

The site is automatically deployed to GitHub Pages through GitHub Actions whenever changes are pushed to the main branch.