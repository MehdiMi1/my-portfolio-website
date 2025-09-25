import os
import json
import datetime
import click
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response, flash
from flask_sqlalchemy import SQLAlchemy
from markdown import markdown
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
# --- NEW IMPORTS FOR SECURITY ---
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
# --- Import API Key from config.py ---
try:
    from config import API_KEY
    GOOGLE_API_KEY = API_KEY
except ImportError:
    print("WARNING: config.py not found or API_KEY not defined in it. AI Assistant will not work.")
    GOOGLE_API_KEY = None

# --- Import Seed Data from separate file ---
# محتوای پست‌ها از فایل جداگانه خوانده می‌شود تا این فایل تمیز بماند
from seed_data import (
    blog_content_fa, blog_content_en, blog_content_ar, blog_content_de,
    project_content_fa, project_content_en,
    new_post_content_fa, new_post_content_en
)


# --- Setup ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# --- Load Translations ---
try:
    with open(os.path.join(basedir, 'translations.json'), 'r', encoding='utf-8') as f:
        translations = json.load(f)
except FileNotFoundError:
    print("FATAL ERROR: translations.json not found. Please create it.")
    translations = {}

# --- Jinja Filter ---
@app.template_filter('markdown')
def render_markdown(text):
    if text:
        return markdown(text, extensions=['fenced_code', 'tables'])
    return ''

# --- Config ---
app.config['SECRET_KEY'] = 'a-very-secret-key-that-you-should-change-for-sessions'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- NEW: FLASK-LOGIN SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # آدرس صفحه لاگین
login_manager.login_message = "لطفاً برای دسترسی به این صفحه وارد شوید."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database Models ---

# --- NEW: User Model for Admin ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(100), nullable=True)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    title_fa = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(100), nullable=False)
    title_ar = db.Column(db.String(100), nullable=False)
    title_de = db.Column(db.String(100), nullable=False)
    category_fa = db.Column(db.String(50), nullable=False)
    category_en = db.Column(db.String(50), nullable=False)
    category_ar = db.Column(db.String(50), nullable=False)
    category_de = db.Column(db.String(50), nullable=False)
    content_fa = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    content_ar = db.Column(db.Text, nullable=False)
    content_de = db.Column(db.Text, nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(100), nullable=False)
    project_url = db.Column(db.String(200), nullable=True)
    display_order = db.Column(db.Integer, default=100)
    title_fa = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(100), nullable=False)
    title_ar = db.Column(db.String(100), nullable=False)
    title_de = db.Column(db.String(100), nullable=False)
    description_fa = db.Column(db.Text, nullable=True)
    description_en = db.Column(db.Text, nullable=True)
    description_ar = db.Column(db.Text, nullable=True)
    description_de = db.Column(db.Text, nullable=True)
    content_fa = db.Column(db.Text, nullable=True)
    content_en = db.Column(db.Text, nullable=True)
    content_ar = db.Column(db.Text, nullable=True)
    content_de = db.Column(db.Text, nullable=True)
    tags_fa = db.Column(db.String(200), nullable=True)
    tags_en = db.Column(db.String(200), nullable=True)
    tags_ar = db.Column(db.String(200), nullable=True)
    tags_de = db.Column(db.String(200), nullable=True)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(100), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    display_order = db.Column(db.Integer, default=100)

# --- UPDATED: SECURE ADMIN VIEW ---
class AdminView(ModelView):
    def is_accessible(self):
        # از سیستم لاگین فلسک برای بررسی احراز هویت استفاده می‌کنیم
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # اگر کاربر لاگین نکرده بود، به صفحه لاگین هدایت می‌شود
        return redirect(url_for('login'))

# --- DB Initialization Command ---
@app.cli.command('init-db')
def init_db_command():
    db.drop_all()
    db.create_all()
    print("Seeding data...")

    # --- NEW: Create Admin User ---
    admin_user = User(username='admin')
    # یک رمز عبور قوی انتخاب کنید
    admin_user.set_password('your-very-strong-and-secret-password')
    db.session.add(admin_user)
    print("Admin user created with username: admin")

    post1 = Post(
        slug='landing-page-design-principles',
        image_file='post-image-1.jpg',
        title_fa='۵ اصل کلیدی در طراحی لندینگ پیج موفق',
        title_en='5 Key Principles for Successful Landing Page Design',
        title_ar='5 مبادئ أساسية لتصميم صفحة هبوط ناجحة',
        title_de='5 Schlüsselprinzipien für erfolgreiches Landing-Page-Design',
        category_fa='طراحی', category_en='Design', category_ar='تصميم', category_de='Design',
        content_fa=blog_content_fa['landing-page-design-principles'],
        content_en=blog_content_en['landing-page-design-principles'],
        content_ar=blog_content_ar['landing-page-design-principles'],
        content_de=blog_content_de['landing-page-design-principles']
    )
    post2 = Post(
        slug='website-speed-and-seo',
        image_file='post-image-2.jpg',
        title_fa='چرا سرعت وب‌سایت برای سئو اهمیت دارد؟',
        title_en='Why is Website Speed Important for SEO?',
        title_ar='لماذا تعتبر سرعة الموقع مهمة لتحسين محركات البحث؟',
        title_de='Warum ist die Website-Geschwindigkeit für SEO wichtig?',
        category_fa='تکنولوژی', category_en='Technology', category_ar='تكنولوجيا', category_de='Technologie',
        content_fa=blog_content_fa['website-speed-and-seo'],
        content_en=blog_content_en['website-speed-and-seo'],
        content_ar=blog_content_ar['website-speed-and-seo'],
        content_de=blog_content_de['website-speed-and-seo']
    )
    post3 = Post(
        slug='how-i-built-this-website-with-flask',
        image_file='post-image-3.jpg',
        title_fa='چطور این سایت را با Flask ساختم؟',
        title_en='How I Built This Website with Flask',
        title_ar='كيف قمت ببناء هذا الموقع باستخدام Flask',
        title_de='Wie ich diese Website mit Flask erstellt habe',
        category_fa='توسعه', category_en='Development', category_ar='تطوير', category_de='Entwicklung',
        content_fa=blog_content_fa['how-i-built-this-website-with-flask'],
        content_en=blog_content_en['how-i-built-this-website-with-flask'],
        content_ar=blog_content_ar['how-i-built-this-website-with-flask'],
        content_de=blog_content_de['how-i-built-this-website-with-flask']
    )
    post4 = Post(
        slug='how-i-optimized-this-site-for-seo',
        image_file='seo-case-study.jpg',
        title_fa='چگونه این سایت را برای سئو بهینه کردم: یک نمونه کار عملی',
        title_en='How I Optimized This Site for SEO: A Practical Case Study',
        title_ar='كيف قمت بتحسين هذا الموقع للسيو: دراسة حالة عملية',
        title_de='Wie ich diese Seite für SEO optimiert habe: Eine praktische Fallstudie',
        category_fa='سئو',
        category_en='SEO',
        category_ar='سيو',
        category_de='SEO',
        content_fa=new_post_content_fa,
        content_en=new_post_content_en,
        content_ar=new_post_content_en, # Assuming arabic and german content is english for this new post
        content_de=new_post_content_en
    )
    project1 = Project(
        slug='personal-portfolio-website',
        title_fa='وب‌سایت شخصی و نمونه کارها',
        title_en='Personal Portfolio Website',
        title_ar='موقع المحفظة الشخصية',
        title_de='Persönliche Portfolio-Website',
        description_fa='یک وب‌سایت کامل و دینامیک برای نمایش مهارت‌ها و نمونه کارها.',
        description_en='A complete and dynamic website to showcase skills and portfolio.',
        image_file='project-portfolio-main.jpg',
        project_url='https://mehdimi2.pythonanywhere.com/',
        tags_fa='فلسک, SQLAlchemy, جاوااسکریپت',
        tags_en='Flask, SQLAlchemy, JavaScript',
        display_order=1
    )
    project2 = Project(
        slug='online-resume-landing-page',
        title_fa='لندینگ پیج رزومه آنلاین',
        title_en='Online Resume Landing Page',
        title_ar='صفحة هبوط للسيرة الذاتية',
        title_de='Online-Lebenslauf-Landingpage',
        description_fa='یک صفحه تک صفحه‌ای جذاب برای نمایش رزومه با انیمیشن‌های زیبا.',
        description_en='An attractive single-page site to display a resume with beautiful animations.',
        image_file='project-resume-landing.jpg',
        project_url='/fa/resume',
        tags_fa='HTML, CSS, GSAP',
        tags_en='HTML, CSS, GSAP',
        display_order=2
    )
    project3 = Project(
        slug='bi-dashboard',
        title_fa='پلتفرم هوش تجاری: داشبورد تحلیل فروش و KPI',
        title_en='BI Platform: Sales & KPI Analytics Dashboard',
        title_ar='منصة ذكاء الأعمال: لوحة تحكم تحليلات المبيعات و KPI',
        title_de='BI-Plattform: Dashboard für Vertriebs- & KPI-Analysen',
        description_fa='یک راهکار جامع هوش تجاری (BI) برای تبدیل داده‌های پیچیده فروش به داشبوردهای بصری و قابل درک.',
        description_en='A comprehensive BI solution for transforming complex sales data into visual, intuitive dashboards.',
        content_fa=project_content_fa['bi-dashboard'],
        content_en=project_content_en['bi-dashboard'],
        content_ar=project_content_en['bi-dashboard'], # Assuming english content
        content_de=project_content_en['bi-dashboard'], # Assuming english content
        image_file='project-dashboard-mockup.jpg',
        tags_fa='هوش تجاری, تحلیل داده, SaaS, پایتون, Flask, Chart.js',
        tags_en='Business Intelligence, Data Analysis, SaaS, Python, Flask, Chart.js',
        tags_ar='ذكاء الأعمال, تحليل البيانات, SaaS, بايثون, فلاسك, Chart.js',
        tags_de='Business Intelligence, Datenanalyse, SaaS, Python, Flask, Chart.js',
        display_order=3
    )
    story1 = Story(title='بازآفرینی یک برند', slug='reimagining-a-brand', excerpt='چگونه یک برند قدیمی را برای نسل جدید بازطراحی کردیم؟', content='متن کامل داستان...', image_file='story-brand-reimagined.jpg', display_order=1)
    story2 = Story(title='مصاحبه با یک مینیمالیست', slug='interview-with-a-minimalist', excerpt='گفتگویی با «سارا اکبری»، طراح UI.', content='متن کامل داستان...', image_file='story-minimalist-designer.jpg', display_order=2)

    db.session.add_all([post1, post2, post3, post4, project1, project2, project3, story1, story2])
    db.session.commit()
    print("Database has been initialized and seeded successfully with the new SEO post.")

# --- ADMIN PANEL SETUP ---
admin = Admin(app, name='MiGallery Admin v2', template_mode='bootstrap3')
admin.add_view(AdminView(User, db.session)) # قابلیت مدیریت کاربران در ادمین
admin.add_view(AdminView(Post, db.session))
admin.add_view(AdminView(Project, db.session))
admin.add_view(AdminView(Story, db.session))

# --- Context Processor ---
@app.context_processor
def inject_shared_data():
    lang = request.view_args.get('lang', 'fa') if request.view_args else 'fa'
    session['lang'] = lang
    try:
        latest_posts = []
        if db.engine.dialect.has_table(db.engine.connect(), "post"):
            latest_posts = Post.query.order_by(Post.pub_date.desc()).limit(3).all()
        return dict(
            latest_footer_posts=latest_posts,
            translations=translations,
            lang=lang
        )
    except Exception:
        return dict(latest_footer_posts=[], translations=translations, lang=lang)

# --- Routes ---
@app.route('/')
def index():
    return redirect(url_for('home', lang='fa'))

@app.route('/sitemap.xml')
def sitemap():
    pages = []
    static_pages = ['home', 'about', 'projects', 'blog', 'stories', 'ai_assistant', 'contact', 'resume_pro']
    for lang in ['fa', 'en', 'ar', 'de']:
        for page in static_pages:
            pages.append(url_for(page, lang=lang, _external=True))
    posts = Post.query.order_by(Post.pub_date.desc()).all()
    for lang in ['fa', 'en', 'ar', 'de']:
        for post in posts:
            pages.append(url_for('post_detail', lang=lang, slug=post.slug, _external=True))
    projects_with_details = Project.query.filter(Project.project_url == None).all()
    for lang in ['fa', 'en', 'ar', 'de']:
        for project in projects_with_details:
            pages.append(url_for('project_detail', lang=lang, slug=project.slug, _external=True))
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response

# --- All public routes remain the same ---
@app.route('/<lang>/')
def home(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    try:
        latest_posts = Post.query.order_by(Post.pub_date.desc()).limit(2).all()
    except:
        latest_posts = []
    return render_template('index.html', latest_posts=latest_posts)

@app.route('/<lang>/about')
def about(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    return render_template('about.html')

@app.route('/<lang>/projects')
def projects(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    try:
        all_projects = Project.query.order_by(Project.display_order).all()
    except:
        all_projects = []
    return render_template('projects.html', projects=all_projects)

@app.route('/<lang>/project/<string:slug>')
def project_detail(lang, slug):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    project = Project.query.filter_by(slug=slug).first_or_404()
    if not project.content_fa and not project.content_en:
        if project.project_url:
            return redirect(project.project_url)
        else:
            return redirect(url_for('projects', lang=lang))
    return render_template('project_detail.html', project=project)

@app.route('/<lang>/resume-pro')
def resume_pro(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    return render_template('resume_pro.html')

@app.route('/<lang>/blog')
def blog(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    try:
        category_lang_field = getattr(Post, f'category_{lang}')
        categories_query = db.session.query(category_lang_field).distinct().all()
        unique_categories = [c[0] for c in categories_query]
        posts = Post.query.order_by(Post.pub_date.desc()).all()
    except Exception as e:
        print(e)
        unique_categories, posts = [], []
    return render_template('blog.html', posts=posts, categories=unique_categories)

@app.route('/<lang>/stories')
def stories(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    try:
        all_stories = Story.query.order_by(Story.display_order).all()
    except:
        all_stories = []
    return render_template('stories.html', stories=all_stories)

@app.route('/<lang>/blog/<string:slug>')
def post_detail(lang, slug):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('post_detail.html', post=post)

@app.route('/<lang>/story/<string:slug>')
def story_detail(lang, slug):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    story = Story.query.filter_by(slug=slug).first_or_404()
    return render_template('story_detail.html', story=story)

@app.route('/<lang>/resume')
def resume(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    return render_template('landing_resume.html')

@app.route('/<lang>/contact')
def contact(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    return render_template('contact.html')

@app.route('/<lang>/ai-assistant')
def ai_assistant(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    session.pop('chat_history', None)
    return render_template('ai_assistant.html')

@app.route('/api/ask', methods=['POST'])
def ask_api():
    if not GOOGLE_API_KEY:
        error_lang = session.get('lang', 'fa')
        error_message = translations.get(error_lang, {}).get('js_ai_error', 'An API error occurred.')
        return jsonify({'text': 'خطا: کلید API گوگل تنظیم نشده است. لطفاً با مدیر سایت تماس بگیرید.'}), 500

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    user_message = data['message']
    chat_history = session.get('chat_history', [])

    gemini_history_format = []
    for entry in chat_history:
        role = 'user' if entry['sender'] == 'user' else 'model'
        gemini_history_format.append({'role': role, 'parts': [entry['text']]})

    chat = model.start_chat(history=gemini_history_format)

    try:
        response = chat.send_message(user_message)
        ai_response_text = response.text

        chat_history.append({'sender': 'user', 'text': user_message})
        chat_history.append({'sender': 'ai', 'text': ai_response_text})

        session['chat_history'] = chat_history

        return jsonify({'text': ai_response_text})

    except Exception as e:
        print(f"An error occurred: {e}")
        error_lang = session.get('lang', 'fa')
        error_message = translations.get(error_lang, {}).get('js_ai_error', 'An API error occurred.')
        return jsonify({'text': error_message}), 500

# --- UPDATED: Login/Logout for Admin using Flask-Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/admin')

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect('/admin')
        else:
            flash('نام کاربری یا رمز عبور اشتباه است.', 'danger')

    # برای این بخش بهتر است یک فایل login.html در پوشه templates بسازید
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)