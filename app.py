import os
import json
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, make_response, Response, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from markdown import markdown
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from flask_ckeditor import CKEditor, CKEditorField
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import Markup
from sqlalchemy import desc, func
from flask_compress import Compress
from flask_caching import Cache

# --- 1. INITIALIZE EXTENSIONS ---
db = SQLAlchemy()
login_manager = LoginManager()
compress = Compress()
cache = Cache(config={'CACHE_TYPE': 'simple'})
ckeditor = CKEditor()

class MyAdminIndexView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')
    def is_accessible(self):
        return current_user.is_authenticated

admin = Admin(name='MiGallery Admin', template_mode='bootstrap3', index_view=MyAdminIndexView(url='/admin'))

# --- 2. DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SiteContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

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
    slug = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(100), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    display_order = db.Column(db.Integer, default=100)
    title_fa = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(100), nullable=False)
    title_ar = db.Column(db.String(100), nullable=False)
    title_de = db.Column(db.String(100), nullable=False)
    excerpt_fa = db.Column(db.Text, nullable=False)
    excerpt_en = db.Column(db.Text, nullable=False)
    excerpt_ar = db.Column(db.Text, nullable=False)
    excerpt_de = db.Column(db.Text, nullable=False)
    content_fa = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    content_ar = db.Column(db.Text, nullable=False)
    content_de = db.Column(db.Text, nullable=False)
    category_fa = db.Column(db.String(50), nullable=True)
    category_en = db.Column(db.String(50), nullable=True)
    category_ar = db.Column(db.String(50), nullable=True)
    category_de = db.Column(db.String(50), nullable=True)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(250), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    content_fa = db.Column(db.String(250), nullable=False)
    content_en = db.Column(db.String(250), nullable=False)
    content_ar = db.Column(db.String(250), nullable=False)
    content_de = db.Column(db.String(250), nullable=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    icon = db.Column(db.String(100), nullable=True, comment="e.g., fa-solid fa-code")
    display_order = db.Column(db.Integer, default=100)
    title_fa = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(100), nullable=False)
    title_ar = db.Column(db.String(100), nullable=False)
    title_de = db.Column(db.String(100), nullable=False)
    description_fa = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    description_ar = db.Column(db.Text, nullable=False)
    description_de = db.Column(db.Text, nullable=False)
    plans = db.relationship('PricingPlan', backref='service', lazy=True, cascade="all, delete-orphan")

class PricingPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=100)
    title_fa = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(100), nullable=False)
    title_ar = db.Column(db.String(100), nullable=False)
    title_de = db.Column(db.String(100), nullable=False)
    price_fa = db.Column(db.String(100), nullable=False)
    price_en = db.Column(db.String(100), nullable=False)
    price_ar = db.Column(db.String(100), nullable=False)
    price_de = db.Column(db.String(100), nullable=False)
    features_fa = db.Column(db.Text, nullable=False, comment="Use '|' to separate features")
    features_en = db.Column(db.Text, nullable=False)
    features_ar = db.Column(db.Text, nullable=False)
    features_de = db.Column(db.Text, nullable=False)

# --- 3. ADMIN & LOGIN ---
basedir = os.path.abspath(os.path.dirname(__file__))

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class PostAdminView(AdminModelView):
    form_overrides = {
        'content_fa': CKEditorField,
        'content_en': CKEditorField,
        'content_ar': CKEditorField,
        'content_de': CKEditorField,
    }
    form_extra_fields = {
        'image_file': ImageUploadField('Image',
                                      base_path=os.path.join(basedir, 'static/images/blog'),
                                      url_relative_path='images/blog/',
                                      thumbnail_size=(100, 100, True))
    }
    
class ProjectAdminView(AdminModelView):
    form_overrides = {
        'content_fa': CKEditorField,
        'content_en': CKEditorField,
        'content_ar': CKEditorField,
        'content_de': CKEditorField,
    }
    form_extra_fields = {
        'image_file': ImageUploadField('Image',
                                      base_path=os.path.join(basedir, 'static/images/projects'),
                                      url_relative_path='images/projects/',
                                      thumbnail_size=(100, 100, True))
    }

class StoryAdminView(AdminModelView):
    form_overrides = {
        'content_fa': CKEditorField,
        'content_en': CKEditorField,
        'content_ar': CKEditorField,
        'content_de': CKEditorField,
    }
    form_extra_fields = {
        'image_file': ImageUploadField('Image',
                                      base_path=os.path.join(basedir, 'static/images/stories'),
                                      url_relative_path='images/stories/',
                                      thumbnail_size=(100, 100, True))
    }

class SiteContentView(AdminModelView):
    form_columns = ['key', 'value']
    column_list = ['key', 'value']
    column_searchable_list = ['key', 'value']
    column_editable_list = ['value']
    can_create = False
    can_delete = False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- 4. APP FACTORY ---
def create_app():
    app = Flask(__name__)
    
    # Load configuration from config.py for better security
    app.config.from_pyfile('config.py')
    app.config.update(
        FLASK_ADMIN_SWATCH='cerulean',
        CKEDITOR_PKG_TYPE='standard'
    )
    
    db.init_app(app)
    admin.init_app(app)
    login_manager.init_app(app)
    compress.init_app(app)
    cache.init_app(app)
    ckeditor.init_app(app)
    login_manager.login_view = 'login'

    app.jinja_env.globals.update(getattr=getattr)
    app.jinja_env.globals.update(str=str)

    with app.app_context():
        admin.add_view(AdminModelView(User, db.session, name='کاربران'))
        admin.add_view(PostAdminView(Post, db.session, name='پست‌های بلاگ'))
        admin.add_view(ProjectAdminView(Project, db.session, name='پروژه‌ها'))
        admin.add_view(StoryAdminView(Story, db.session, name='داستان‌ها'))
        admin.add_view(AdminModelView(News, db.session, name='اخبار روز'))
        admin.add_view(SiteContentView(SiteContent, db.session, name='مدیریت محتوای ثابت'))
        admin.add_view(AdminModelView(Service, db.session, name='خدمات اصلی'))
        admin.add_view(AdminModelView(PricingPlan, db.session, name='پلن‌های قیمت‌گذاری'))

        with open(os.path.join(basedir, 'translations.json'), 'r', encoding='utf-8') as f:
            translations = json.load(f)

        @app.context_processor
        @cache.cached(timeout=300)
        def inject_shared_data():
            lang = request.view_args.get('lang', 'fa') if request.view_args else 'fa'
            latest_posts = Post.query.order_by(Post.pub_date.desc()).limit(3).all()
            active_news = News.query.filter_by(is_active=True).order_by(desc(News.pub_date)).all()
            site_content_values = {item.key: item.value for item in SiteContent.query.all()}
            return dict(lang=lang, latest_footer_posts=latest_posts, translations=translations, active_news=active_news, site_content_data=site_content_values)

        def create_seo_data(title, description, image_filename=None, keywords=[]):
            return {"meta_title": title, "meta_description": description, "og_title": title, "og_description": description, "og_url": request.url, "og_image": url_for('static', filename=f'images/{image_filename}' if image_filename else 'images/hero-collaborative-tech-team.jpg', _external=True), "keywords": keywords}

        def generate_hreflang_tags(endpoint, **kwargs):
            tags = {}
            if 'slug' not in kwargs and request.view_args and 'slug' in request.view_args:
                kwargs['slug'] = request.view_args['slug']
            for lang_code in ['fa', 'en', 'ar', 'de']:
                kwargs['lang'] = lang_code
                tags[lang_code] = url_for(endpoint, _external=True, **kwargs)
            return tags

        @app.template_filter('markdown')
        def render_markdown(text):
            if text is None: return ''
            return Markup(markdown(text, extensions=['fenced_code', 'tables']))

        @app.template_filter('striptags')
        def striptags_filter(text):
            return Markup(text).striptags()

        # --- ROUTES (WITH SEO ENHANCEMENTS) ---
        @app.route('/')
        def index():
            return redirect(url_for('home', lang='fa'))

        @app.route('/robots.txt')
        def robots_txt():
            sitemap_url = url_for('sitemap', _external=True)
            return Response(f"User-agent: *\nDisallow: /admin\nDisallow: /login\n\nSitemap: {sitemap_url}", mimetype='text/plain')

        @app.route('/sitemap.xml')
        def sitemap():
            pages, static_pages, langs = [], ['home', 'about', 'projects', 'blog', 'stories', 'ai_assistant', 'contact', 'resume_pro', 'seo_tool', 'services'], ['fa', 'en', 'ar', 'de']
            for lang in langs:
                for page in static_pages: pages.append(url_for(page, lang=lang, _external=True))
            for lang in langs:
                for post in Post.query.all(): pages.append(url_for('post_detail', lang=lang, slug=post.slug, _external=True))
            for lang in langs:
                for project in Project.query.filter(Project.content_fa != None).all(): pages.append(url_for('project_detail', lang=lang, slug=project.slug, _external=True))
            for lang in ['fa', 'en', 'ar', 'de']:
                for story in Story.query.all(): pages.append(url_for('story_detail', lang=lang, slug=story.slug, _external=True))
            for lang in langs:
                for service in Service.query.all(): pages.append(url_for('service_detail', lang=lang, slug=service.slug, _external=True))
            sitemap_xml = render_template('sitemap.xml', pages=pages)
            response = make_response(sitemap_xml)
            response.headers["Content-Type"] = "application/xml"
            return response

        @app.route('/<lang>/')
        def home(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            t = translations[lang]
            seo_data = create_seo_data(f"{t['nav_home']} | {t['default_title_tag']}", t['meta_desc_home'])
            latest_posts = Post.query.order_by(Post.pub_date.desc()).limit(2).all()
            featured_project = Project.query.order_by(Project.display_order).first()
            hreflang_tags = generate_hreflang_tags('home')
            return render_template('index.html', latest_posts=latest_posts, featured_project=featured_project, hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/services')
        def services(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            t = translations[lang]
            all_services = Service.query.order_by(Service.display_order).all()
            seo_data = create_seo_data(t.get('services_page_title', 'Services'), t.get('services_header_subtitle', 'Our service offerings'))
            hreflang_tags = generate_hreflang_tags('services')
            return render_template('services.html', services=all_services, hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/service/<string:slug>')
        def service_detail(lang, slug):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            t = translations[lang]
            service = Service.query.filter_by(slug=slug).first_or_404()
            title = getattr(service, f'title_{lang}')
            description = getattr(service, f'description_{lang}')
            seo_data = create_seo_data(f"{title} | {t.get('services_page_title', 'Services')}", description)
            hreflang_tags = generate_hreflang_tags('service_detail', slug=slug)
            return render_template('service_detail.html', service=service, hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/seo-tag-generator')
        def seo_tool(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            t = translations[lang]
            title, description = ("ابزار رایگان تولید تگ سئو", "با ابزار رایگان ما، تگ‌های عنوان و توضیحات متای بهینه برای سایت خود بسازید.") if lang == 'fa' else ("Free SEO Meta Tag Generator", "Create optimized meta title and description tags for your site.")
            seo_data = create_seo_data(f"{title} | {t['default_title_tag']}", description)
            hreflang_tags = generate_hreflang_tags('seo_tool')
            return render_template('seo_tool.html', hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/about')
        def about(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            t = translations[lang]
            page_content = {item.key.replace('about_', '', 1).replace(f'_{lang}', ''): item.value for item in SiteContent.query.filter(SiteContent.key.like(f"about_%_{lang}")).all()}
            seo_data = create_seo_data(f"{t['about_page_title']} | {t['default_title_tag']}", t['meta_desc_about'], 'about-creative-brainstorm-session.jpg')
            hreflang_tags = generate_hreflang_tags('about')
            return render_template('about.html', page_content=page_content, hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/blog')
        def blog(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            t = translations[lang]
            posts, category_lang_field = Post.query.order_by(desc(Post.pub_date)).all(), getattr(Post, f'category_{lang}')
            categories_query = db.session.query(category_lang_field).distinct().all()
            unique_categories = [c[0] for c in categories_query if c[0]]
            seo_data = create_seo_data(f"{t['blog_page_title']} | {t['default_title_tag']}", t['blog_header_subtitle'])
            hreflang_tags = generate_hreflang_tags('blog')
            return render_template('blog.html', posts=posts, categories=unique_categories, hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/blog/<string:slug>')
        def post_detail(lang, slug):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            post = Post.query.filter_by(slug=slug).first_or_404()
            t = translations[lang]
            title, content_md = getattr(post, f'title_{lang}'), getattr(post, f'content_{lang}')
            plain_content = ' '.join(Markup(markdown(content_md or "")).striptags().split())
            seo_data = create_seo_data(f"{title} | {t['blog_page_title']}", plain_content[:160], f'blog/{post.image_file}', keywords=[getattr(post, f'category_{lang}'), t['nav_blog']] + title.split())
            json_ld_data = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": title, "description": seo_data['meta_description'], "image": seo_data['og_image'], "datePublished": post.pub_date.isoformat(), "author": {"@type": "Person", "name": t['blog_author_name']}}
            related_posts = Post.query.filter(getattr(Post, f'category_{lang}') == getattr(post, f'category_{lang}'), Post.id != post.id).order_by(desc(Post.pub_date)).limit(2).all()
            if len(related_posts) < 2:
                related_posts.extend(Post.query.filter(Post.id != post.id).order_by(desc(Post.pub_date)).limit(2 - len(related_posts)).all())
            hreflang_tags = generate_hreflang_tags('post_detail', slug=slug)
            return render_template('post_detail.html', post=post, related_posts=related_posts, json_ld_data=json.dumps(json_ld_data, indent=4), hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/projects')
        def projects(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            t = translations[lang]
            all_projects = Project.query.order_by(Project.display_order).all()
            seo_data = create_seo_data(f"{t['projects_page_title']} | {t['default_title_tag']}", t['projects_header_subtitle'])
            hreflang_tags = generate_hreflang_tags('projects')
            return render_template('projects.html', projects=all_projects, hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/project/<string:slug>')
        def project_detail(lang, slug):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            project = Project.query.filter_by(slug=slug).first_or_404()
            t = translations[lang]
            title = getattr(project, f'title_{lang}')
            description = getattr(project, f'description_{lang}', '')
            tags_str = getattr(project, f'tags_{lang}', '')
            tags = tags_str.split(',') if tags_str else []
            seo_data = create_seo_data(f"{title} | {t['projects_page_title']}", description[:160], f'projects/{project.image_file}', keywords=[t['nav_projects']] + tags)
            hreflang_tags = generate_hreflang_tags('project_detail', slug=slug)
            return render_template('project_detail.html', project=project, hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/stories')
        def stories(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            t = translations[lang]
            all_stories, category_lang_field = Story.query.order_by(Story.display_order).all(), getattr(Story, f'category_{lang}')
            categories_query = db.session.query(category_lang_field).distinct().all()
            unique_categories = [c[0] for c in categories_query if c[0]]
            seo_data = create_seo_data(f"{t['stories_page_title']} | {t['default_title_tag']}", t['stories_header_subtitle'])
            hreflang_tags = generate_hreflang_tags('stories')
            return render_template('stories.html', stories=all_stories, categories=unique_categories, hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/story/<string:slug>')
        def story_detail(lang, slug):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            story = Story.query.filter_by(slug=slug).first_or_404()
            t = translations[lang]
            title = getattr(story, f'title_{lang}')
            excerpt = getattr(story, f'excerpt_{lang}')
            seo_data = create_seo_data(f"{title} | {t['stories_page_title']}", excerpt[:160], f'stories/{story.image_file}', keywords=[t['nav_stories'], getattr(story, f'category_{lang}')])
            json_ld_data = {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": seo_data['meta_description'], "image": seo_data['og_image'], "datePublished": story.pub_date.isoformat(), "author": {"@type": "Person", "name": t['blog_author_name']}}
            hreflang_tags = generate_hreflang_tags('story_detail', slug=slug)
            return render_template('story_detail.html', story=story, json_ld_data=json.dumps(json_ld_data, indent=4), hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/contact')
        def contact(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            t = translations[lang]
            seo_data = create_seo_data(f"{t['contact_page_title']} | {t['default_title_tag']}", t['contact_header_subtitle'])
            hreflang_tags = generate_hreflang_tags('contact')
            return render_template('contact.html', hreflang_tags=hreflang_tags, **seo_data)

        @app.route('/<lang>/resume-pro')
        def resume_pro(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            t = translations[lang]
            title = t.get('resume_page_title', 'Professional Resume')
            description = t.get('resume_about_me_desc', 'A creative and detail-oriented developer...')
            seo_data = create_seo_data(title, description)
            return render_template('resume_pro.html', **seo_data)
            
        @app.route('/<lang>/resume')
        def resume(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            return render_template('landing_resume.html')

        @app.route('/<lang>/ai-assistant')
        def ai_assistant(lang):
            if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
            session.pop('chat_history', None)
            return render_template('ai_assistant.html')

        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if current_user.is_authenticated: return redirect(url_for('admin.index'))
            if request.method == 'POST':
                user = User.query.filter_by(username=request.form.get('username')).first()
                if user and user.check_password(request.form.get('password')):
                    login_user(user)
                    return redirect(url_for('admin.index'))
                else: flash('نام کاربری یا رمز عبور اشتباه است.')
            return render_template('login.html')

        @app.route('/logout')
        @login_required
        def logout():
            logout_user()
            return redirect(url_for('home', lang='fa'))

        # --- ERROR HANDLERS (BUG FIX APPLIED) ---
        @app.errorhandler(404)
        def page_not_found(e):
            lang = request.path.split('/')[1] if request.path.startswith(('/', 'en', 'ar', 'de')) else 'fa'
            context = inject_shared_data()
            context['lang'] = lang
            
            # Add default SEO data for the 404 page
            t = translations.get(lang, translations['en']) # Fallback to English
            meta_title = f"404 Not Found | {t.get('default_title_tag', 'Mi Design')}"
            meta_description = t.get('meta_desc_404', "The page you are looking for does not exist.")
            
            # Add SEO data to the context
            context['meta_title'] = meta_title
            context['meta_description'] = meta_description

            return render_template('404.html', **context), 404

        @app.errorhandler(500)
        def internal_server_error(e):
            lang = request.path.split('/')[1] if request.path.startswith(('/', 'en', 'ar', 'de')) else 'fa'
            context = inject_shared_data()
            context['lang'] = lang
            return render_template('500.html', **context), 500

        @app.cli.command('init-db')
        def init_db_command():
            db.drop_all()
            db.create_all()
            print("Database cleared and tables created.")
            from seed_data import site_content_data, blog_posts_data, projects_data, stories_data, news_data, services_data, plans_data
            admin_user = User(username='admin')
            admin_user.set_password(current_app.config['ADMIN_PASSWORD'])
            db.session.add(admin_user)
            print("Admin user created.")
            for item in site_content_data: db.session.add(SiteContent(**item))
            print(f"Seeded {len(site_content_data)} site content entries.")
            for data in blog_posts_data: db.session.add(Post(**data))
            print(f"Seeded {len(blog_posts_data)} blog posts.")
            for data in projects_data: db.session.add(Project(**data))
            print(f"Seeded {len(projects_data)} projects.")
            for data in stories_data: db.session.add(Story(**data))
            print(f"Seeded {len(stories_data)} stories.")
            for data in news_data: db.session.add(News(**data))
            print(f"Seeded {len(news_data)} news entries.")
            for data in services_data: db.session.add(Service(**data))
            print(f"Seeded {len(services_data)} services.")
            for data in plans_data: db.session.add(PricingPlan(**data))
            print(f"Seeded {len(plans_data)} pricing plans.")
            db.session.commit()
            print("Database has been initialized and seeded successfully.")
            
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)