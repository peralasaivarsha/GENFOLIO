import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, send_file ,url_for
import random
import tempfile
from glob import glob
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import time
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import redirect, flash


app = Flask(__name__)
load_dotenv()
# Configure Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-pro")

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration - make these absolute paths
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 2MB limit

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    portfolios = db.relationship('Portfolio', backref='author', lazy=True)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_default_avatar():
    return url_for('static', filename='uploads/default-avatar.png', _external=True)

def validate_url(url, default_domain=None):
    if not url:
        return "#"
        
    parsed = urlparse(url)
    if not parsed.scheme:
        url = 'https://' + url
        
    if default_domain and default_domain not in url:
        return "#"
        
    return url
def get_available_templates():
    """Scan template directory and return available options"""
    templates = {
        'business': {},
        'education': {}
    }
    
    portfolio_types = ['business', 'education']
    styles = ['creative', 'minimalist', 'professional']
    themes = ['dark', 'light']
    
    for portfolio_type in portfolio_types:
        templates[portfolio_type] = {}
        for style in styles:
            templates[portfolio_type][style] = {}
            for theme in themes:
                # Path pattern: templates/{portfolio_type}/{style}/{theme}/*.html
                template_path = os.path.join('templates', portfolio_type, style, theme, '*.html')
                template_paths = glob(template_path)
                if template_paths:
                    templates[portfolio_type][style][theme] = [
                        os.path.splitext(os.path.basename(path))[0] 
                        for path in template_paths
                    ]
    
    return templates

def extract_between(text, start_marker, end_marker):
    """Helper function to extract content between markers"""
    start = text.find(start_marker) + len(start_marker)
    end = text.find(end_marker)
    return text[start:end].strip()

def generate_business_content(user_data):
    """Generate personalized business portfolio content using Gemini AI"""
    # Convert lists to formatted strings
    experience_str = "\n- ".join(user_data['experience'])
    skills_str = "\n- ".join(user_data['skills'])
    achievements_str = "\n- ".join(user_data['achievements'])

    prompt = f"""
    Generate personalized business portfolio content for a professional named {user_data['name']} with the following information:
    
    Company: {user_data['company']}
    Position: {user_data['position']}
    
    Experience:
    - {experience_str}
    
    Skills:
    - {skills_str}
    
    Achievements:
    - {achievements_str}
    
    Provide output in this exact format:
    
    PROFILE_START
    [Professional profile section - 3-5 sentences describing the professional]
    PROFILE_END
    
    EXPERIENCE_DESCRIPTION_START
    [Professional experience description - elaborate on the experience]
    EXPERIENCE_DESCRIPTION_END
    
    ACHIEVEMENTS_DETAILS_START
    [Detailed achievements descriptions - 3-5 sentences each]
    ACHIEVEMENTS_DETAILS_END
    
    SKILLS_DESCRIPTION_START
    [Skills description showing how skills were applied professionally]
    SKILLS_DESCRIPTION_END
    """
    
    response = model.generate_content(prompt)
    return response.text

def generate_education_content(user_data):
    """Generate personalized education portfolio content using Gemini AI"""
    # Convert lists to formatted strings
    education_str = "\n- ".join(user_data['education'])
    skills_str = "\n- ".join(user_data['skills'])
    projects_str = "\n- ".join(user_data['projects'])
    achievements_str = "\n- ".join(user_data['achievements'])
    prompt = f"""
    Generate personalized education portfolio content for a student/researcher named {user_data['name']} with the following information:
    
    Education:
    - {education_str}
    
    Skills:
    - {skills_str}
    
    Projects:
    - {projects_str}
    
    achievements:
    - {achievements_str}
    
    Provide output in this exact format:
    
    ABOUT_START
    [About me section - 3-5 sentences describing the academic background and research interests.
    Highlight key academic achievements and career aspirations.]
    ABOUT_END
    
    EDUCATION_DETAILS_START
    [Detailed education description - For each degree/institution:
    - Institution name and duration
    - Key coursework/specializations
    - Academic honors/awards
    - Thesis/dissertation topic if applicable]
    EDUCATION_DETAILS_END
    
    PROJECTS_DETAILS_START
    [For each project:
    - Project Title: [Brief description - 3-5 sentences]
      • Technologies/Methods Used: [List]
      • Key Contributions: [2-3 points]
      • Outcomes/Achievements: [1-2 points]]
    PROJECTS_DETAILS_END
    
    SKILLS_APPLICATION_START
    [Skills description organized by category:
    Technical Skills:
    - How each technical skill was applied in academic projects/research
    
    Research Skills:
    - Specific research methodologies mastered
    - Applications in projects/publications
    
    Soft Skills:
    - Demonstrated leadership/teamwork examples
    - Communication skills development]
    SKILLS_APPLICATION_END
    
    ACHIEVEMENTS_DETAILS_START
    [If achievements exist:
    - Citation format for each publication
    - Brief context/contribution (1 sentence each)
    Otherwise: "No formal achievements yet"]
    ACHIEVEMENTS_DETAILS_END
    
    """
    
    response = model.generate_content(prompt)
    return response.text

# Add these routes before the if __name__ == '__main__' block
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('landing'))


@app.route('/')
def landing():
    """Landing page that all users see first"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('landing.html')
@app.route('/check_auth')
def check_auth():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'username': current_user.username
        })
    return jsonify({'authenticated': False})

@app.route('/index')
@login_required
def index():
    """Main portfolio generator page - protected by login"""
    templates = get_available_templates()
    return render_template('index.html', templates=templates)

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    try:
       # Handle file upload
        profile_pic_path = None
        if 'profilePic' in request.files:
            file = request.files['profilePic']
            # print("File received:", file.filename)  # Debug filename
            
            if file and file.filename != '' and allowed_file(file.filename):
                # Create upload directory if it doesn't exist
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Generate secure filename
                timestamp = str(int(time.time()))
                filename = secure_filename(f"{timestamp}_{file.filename}")
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # print("Attempting to save to:", save_path)  # Debug save path
                file.save(save_path)
                # print("File saved successfully")
                
                # Generate URL
                profile_pic_path = url_for('static', filename=f'uploads/{filename}', _external=True)
                # print("Generated profile pic URL:", profile_pic_path)
        

        user_data = {
            'portfolio_type': request.form.get('portfolioType'),
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'style': request.form.get('style'),
            'theme': request.form.get('theme'),
            'profile_pic': profile_pic_path,
            'social_links': {
                'linkedin': validate_url(request.form.get('linkedin')),
                'github': validate_url(request.form.get('github'), 'github.com'),
                'resume': validate_url(request.form.get('resume'))
        }
        }
        
        # Get data specific to portfolio type
        if user_data['portfolio_type'] == 'business':
            experiences = request.form.getlist('experience')
            skills = request.form.getlist('skills')
            achievements = request.form.getlist('achievements')
            user_data['social_links']['twitter'] = validate_url(request.form.get('twitter'))
            user_data.update({
                'company': request.form.get('company'),
                'position': request.form.get('position'),
                'experience': [exp for exp in experiences if exp.strip()],
                'skills': [skill for skill in skills if skill.strip()],
                'achievements': [ach for ach in achievements if ach.strip()],
            })
            generated_content = generate_business_content(user_data)
        else:  # education
            education = request.form.getlist('education')
            skills = request.form.getlist('skills')
            projects = request.form.getlist('projects')
            achievements = request.form.getlist('achievements')
            user_data.update({
                'education': [edu for edu in education if edu.strip()],
                'skills': [skill for skill in skills if skill.strip()],
                'projects': [proj for proj in projects if proj.strip()],
                'achievements': [ach for ach in achievements if ach.strip()],
            })
            generated_content = generate_education_content(user_data)
        
        # Get available templates for selected portfolio type, style and theme
        templates = get_available_templates()
        available_templates = templates.get(user_data['portfolio_type'], {}).get(user_data['style'], {}).get(user_data['theme'], [])
        
        if not available_templates:
            return jsonify({'success': False, 'error': 'No templates available for selected style/theme'})
        
        # Randomly select a template
        selected_template = random.choice(available_templates)
        
        # Extract content based on portfolio type
        if user_data['portfolio_type'] == 'business':
            profile_content = extract_between(generated_content, "PROFILE_START", "PROFILE_END")
            experience_desc = extract_between(generated_content, "EXPERIENCE_DESCRIPTION_START", "EXPERIENCE_DESCRIPTION_END")
            achievements_desc = extract_between(generated_content, "ACHIEVEMENTS_DETAILS_START", "ACHIEVEMENTS_DETAILS_END")
            skills_desc = extract_between(generated_content, "SKILLS_DESCRIPTION_START", "SKILLS_DESCRIPTION_END")
            
            # Prepare data for template
            skills_list = [skill.strip() for skill in user_data['skills'] if skill.strip()]
            achievements_list = [ach.strip() for ach in user_data['achievements'] if ach.strip()]
            experience_list = [exp.strip() for exp in user_data['experience'] if exp.strip()]
    
            
            # Render template
            template_path = os.path.join(
                user_data['portfolio_type'],
                user_data['style'],
                user_data['theme'],
                f"{selected_template}.html"
            )
            
            
            portfolio_html = render_template(
        template_path.replace('\\', '/'),
        user_data=user_data,
        social_links=user_data['social_links'],
        profile_content=profile_content,
        skills_list=skills_list,
        skills_desc=skills_desc,
        achievements_list=achievements_list,
        experience_list=experience_list,
        experience_desc=experience_desc,
        achievements_desc=achievements_desc,
        portfolio_type='business'
    )
        else:  # education
            about_content = extract_between(generated_content, "ABOUT_START", "ABOUT_END")
            education_desc = extract_between(generated_content, "EDUCATION_DETAILS_START", "EDUCATION_DETAILS_END")
            projects_desc = extract_between(generated_content, "PROJECTS_DETAILS_START", "PROJECTS_DETAILS_END")
            skills_desc = extract_between(generated_content, "SKILLS_APPLICATION_START", "SKILLS_APPLICATION_END")
            achievements_desc = extract_between(generated_content, "ACHIEVEMENTS_DETAILS_START", "ACHIEVEMENTS_DETAILS_END")
            
            # Prepare data for template
            skills_list = [skill.strip() for skill in user_data['skills'] if skill.strip()]
            projects_list = [proj.strip() for proj in user_data['projects'] if proj.strip()]
            education_list = [edu.strip() for edu in user_data['education'] if edu.strip()]
            achievements_list = [pub.strip() for pub in user_data['achievements'] if pub.strip()]
            # Render template
            template_path = os.path.join(
                user_data['portfolio_type'],
                user_data['style'],
                user_data['theme'],
                f"{selected_template}.html"
            )

            portfolio_html = render_template(
                template_path.replace('\\', '/'),
                user_data=user_data,
                about_content=about_content,
                skills_list=skills_list,
                skills_desc=skills_desc,
                projects_list=projects_list,
                projects_desc=projects_desc,
                education_list=education_list,
                education_desc=education_desc,
                achievements_list=achievements_list,
                social_links=user_data['social_links'],
                portfolio_type='education'
            )
        
        # Create a temporary file for download
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        temp_file.write(portfolio_html.encode('utf-8'))
        temp_file.close()
        
        return jsonify({
            'success': True,
            'preview': portfolio_html,
            'download_path': temp_file.name,
            'template_used': f"{user_data['portfolio_type']}/{user_data['style']}/{user_data['theme']}/{selected_template}",
            'style': user_data['style'],
            'theme': user_data['theme']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download')
def download():
    file_path = request.args.get('path')
    return send_file(
        file_path,
        as_attachment=True,
        download_name='portfolio.html',
        mimetype='text/html'
    )
    
def initialize_database():
    """Initialize the database and create tables if they don't exist"""
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)