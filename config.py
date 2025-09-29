import os

# یک کلید مخفی بسیار قوی و تصادفی در اینجا قرار دهید
# می‌توانید از سایت‌هایی مثل https://randomkeygen.com/ برای ساخت کلید استفاده کنید
SECRET_KEY = 'your-super-secret-and-long-random-string-here'

# آدرس دیتابیس
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'blog.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# رمز عبور ادمین که از متغیرهای محیطی خوانده می‌شود
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'a-default-fallback-password')