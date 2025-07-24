python -m venv venv
. venv/bin/activate
python -m pip install --upgrade pip
pip install Flask==2.3.3 PyYAML==6.0.1 Markdown==3.5.1 Frozen-Flask==1.0.0
python flask_resume_app.py --static
