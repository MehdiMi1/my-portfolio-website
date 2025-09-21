import os
import json
import datetime
import click
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from markdown import markdown

# --- Import API Key from config.py ---
try:
    from config import API_KEY
    GOOGLE_API_KEY = API_KEY
except ImportError:
    print("WARNING: config.py not found or API_KEY not defined in it. AI Assistant will not work.")
    GOOGLE_API_KEY = None

# --- Blog Post Content & Project Content ---
blog_content_fa = {
    'landing-page-design-principles': """
### مقدمه: دروازه ورود به دنیای شما

لندینگ پیج (Landing Page) یا صفحه فرود، اولین نقطه تماس بسیاری از کاربران با کسب‌وکار شماست. این صفحه یک هدف مشخص دارد: تبدیل بازدیدکننده به مشتری یا سرنخ (Lead). یک طراحی موفق می‌تواند تفاوت بین یک بازدیدکننده گذری و یک مشتری وفادار را رقم بزند. در این مقاله، ۵ اصل کلیدی را بررسی می‌کنیم که به شما کمک می‌کند لندینگ پیج‌هایی با نرخ تبدیل بالا طراحی کنید.

### اصل اول: وضوح و سادگی پیام (Clarity is King)

کاربر باید در کمتر از ۵ ثانیه متوجه شود که صفحه شما درباره چیست و چه ارزشی برای او دارد.

* **عنوان اصلی (Headline):** باید جذاب، کوتاه و کاملاً مرتبط با نیاز کاربر باشد.
* **زیرعنوان (Sub-headline):** عنوان اصلی را با جزئیات بیشتری توضیح می‌دهد.
* **حذف موارد اضافی:** منوهای ناوبری غیرضروری و هر چیزی که حواس کاربر را پرت می‌کند، حذف کنید.

### اصل دوم: پیشنهاد ارزش منحصربه‌فرد (Unique Value Proposition - UVP)

چرا کاربر باید شما را به رقبا ترجیح دهد؟ UVP شما باید به وضوح به این سوال پاسخ دهد.

### اصل سوم: فراخوان به اقدام (Call to Action - CTA) قدرتمند

دکمه CTA مهم‌ترین عنصر در لندینگ پیج شماست. این دکمه باید قابل مشاهده، واضح و در جای مناسب باشد.

### اصل چهارم: استفاده هوشمندانه از عناصر بصری

مغز انسان تصاویر را بسیار سریع‌تر از متن پردازش می‌کند. از تصاویر با کیفیت، فضای سفید و طراحی واکنش‌گرا استفاده کنید.

### اصل پنجم: اعتبار و اعتماد اجتماعی (Social Proof)

کاربران به کسب‌و-کارهایی اعتماد می‌کنند که دیگران آن‌ها را تأیید کرده‌اند. از نظرات مشتریان و لوگوی همکاران استفاده کنید.

### نتیجه‌گیری

طراحی یک لندینگ پیج موفق یک فرآیند تکرارشونده است. با رعایت این پنج اصل و تحلیل مداوم، می‌توانید نرخ تبدیل خود را به طور چشمگیری افزایش دهید.
""",
    'website-speed-and-seo': """
### مقدمه: زمان طلاست، به خصوص در وب!

در دنیای دیجیتال امروز، صبر کاربران بسیار کم شده است. اهمیت سرعت فقط به تجربه کاربری (UX) محدود نمی‌شود؛ این فاکتور یکی از مهم‌ترین عوامل در رتبه‌-بندی نتایج جستجو (SEO) نیز هست.

### ۱. سرعت به عنوان یک فاکتور رتبه‌-بندی مستقیم

گوگل به طور رسمی تأیید کرده است که سرعت سایت یکی از سیگنال‌هایی است که برای رتبه‌بندی صفحات استفاده می‌کند، به خصوص با معرفی معیارهای **Core Web Vitals**.

### ۲. Core Web Vitals چیست؟

این معیارها تجربه کاربری واقعی را می‌سنجند: LCP (سرعت بارگذاری بزرگترین محتوا)، FID (پاسخگویی به اولین تعامل) و CLS (پایداری بصری). سایت کند در این معیارها نمره ضعیفی می‌گیرد.

### ۳. تأثیر سرعت بر نرخ پرش (Bounce Rate)

هر ثانیه تأخیر در بارگذاری، نرخ پرش را به شدت افزایش می‌دهد. نرخ پرش بالا یک سیگنال منفی قوی برای گوگل است.

### ۴. تأثیر بر نرخ خزش (Crawl Budget)

ربات‌های گوگل زمان محدودی برای بررسی سایت شما دارند. اگر سایت شما کند باشد، تعداد صفحات کمتری ایندکس می‌شوند.

### چگونه سرعت سایت خود را بهبود دهیم؟

* **بهینه‌سازی تصاویر:** فشرده‌سازی و استفاده از فرمت‌های مدرن.
* **استفاده از CDN:** توزیع محتوا در سرورهای جهانی.
* **کاهش کدهای CSS و JavaScript:** فشرده‌سازی (Minify) فایل‌ها.
* **فعال‌سازی کش مرورگر.**
* **انتخاب هاستینگ مناسب.**

### نتیجه‌گیری

سرعت وب‌-سایت دیگر یک مزیت نیست، بلکه یک ضرورت است که مستقیماً بر رتبه شما در گوگل و موفقیت کسب‌-و-کارتان تأثیر می‌گذارد.
""",
    'how-i-built-this-website-with-flask': """
### مقدمه: چرا فلسک؟

برای ساخت این وب‌-سایت، به دنبال ابزاری بودم که هم **انعطاف‌پذیری** کامل و هم **سادگی** داشته باشد. **فلسک (Flask)**، این میکروفریم‌-ورک محبوب پایتون، بهترین انتخاب بود.

### معماری و تکنولوژی‌های اصلی

1.  **Backend: Python و Flask**
    * **Flask:** برای مدیریت روت‌ها و منطق برنامه.
    * **SQLAlchemy:** برای مدیریت پایگاه داده به صورت شیءگرا (ORM) و کار با SQLite.
    * **Jinja2:** برای ساخت صفحات HTML داینامیک.

2.  **Frontend: HTML, CSS, و JavaScript**
    * **JavaScript (Vanilla):** برای تعاملات و انیمیشن‌های سفارشی.
    * **GSAP (GreenSock):** برای انیمیشن‌های پیچیده‌تر مانند لودینگ سایت.

3.  **پایگاه داده: SQLite**
    - ساده، سریع و مبتنی بر فایل، ایده‌آل برای این پروژه.

### ویژگی‌های کلیدی سایت

- **چندزبانگی:** با استفاده از یک فایل `translations.json` و `context_processor` در فلسک.
- **محتوای داینامیک:** تمام پست‌ها و پروژه‌ها از پایگاه داده خوانده می‌شوند.
- **پشتیبانی از Markdown:** مقالات با فرمت Markdown نوشته شده و به صورت پویا به HTML تبدیل می‌شوند.
- **انیمیشن‌های اسکرول:** با استفاده از `IntersectionObserver` API.

### نتیجه‌گیری

فلسک به من اجازه داد تا بدون پیچیدگی‌های غیرضروری، یک وب‌-سایت کاملاً سفارشی، سریع و مدرن بسازم.
"""
}
blog_content_en = {
    'landing-page-design-principles': """
### Introduction: The Gateway to Your World
A landing page is the first point of contact for many users with your business. It has one specific goal: to convert a visitor into a customer or lead. This article explores 5 key principles for designing high-converting landing pages.
### Principle 1: Clarity is King
A user must understand your page's purpose and value within 5 seconds.
- **Headline:** Must be engaging, short, and relevant.
- **Sub-headline:** Elaborates on the headline.
- **Remove Distractions:** Eliminate unnecessary navigation and links.
### Principle 2: Unique Value Proposition (UVP)
Clearly answer: why should a user choose you over competitors?
### Principle 3: A Strong Call to Action (CTA)
The CTA is your most critical element. It must be visible, clear, and well-placed.
### Principle 4: Smart Use of Visuals
Use high-quality images, white space, and ensure a responsive design. The brain processes visuals faster than text.
### Principle 5: Social Proof
Users trust businesses endorsed by others. Use testimonials and partner logos.
### Conclusion
Designing a successful landing page is an iterative process. Following these principles and continuously testing will significantly boost your conversion rates.
""",
    'website-speed-and-seo': """
### Introduction: Time is Money, Especially on the Web!
In today's digital world, user patience is low. Website speed is crucial not only for user experience (UX) but also as a major factor in search engine optimization (SEO).
### 1. Speed as a Direct Ranking Factor
Google has officially confirmed that site speed is a ranking signal, especially with the introduction of **Core Web Vitals**.
### 2. What are Core Web Vitals?
These metrics measure real-world user experience: LCP (loading speed), FID (interactivity), and CLS (visual stability). A slow site scores poorly.
### 3. Impact on Bounce Rate
Every second of loading delay dramatically increases the bounce rate. A high bounce rate is a strong negative signal to Google.
### 4. Effect on Crawl Budget
Googlebots have a limited time to crawl your site. A slow site means fewer pages get indexed.
### How to Improve Your Site Speed
- **Optimize Images:** Compress and use modern formats.
- **Use a CDN:** Distribute content globally.
- **Minimize CSS and JavaScript:** Minify your files.
- **Enable Browser Caching.**
- **Choose a Good Host.**
### Conclusion
Website speed is a necessity. It directly impacts your Google ranking and business success.
""",
    'how-i-built-this-website-with-flask': """
### Introduction: Why Flask?
To build this website, I needed a tool that offered both **flexibility** and **simplicity**. **Flask**, the popular Python micro-framework, was the perfect choice.
### Architecture and Core Technologies
1.  **Backend: Python and Flask**
    - **Flask:** For handling routes and application logic.
    - **SQLAlchemy:** As an ORM for object-oriented database management with SQLite.
    - **Jinja2:** For building dynamic HTML pages.
2.  **Frontend: HTML, CSS, and JavaScript**
    - **Vanilla JavaScript:** For custom interactions and animations.
    - **GSAP (GreenSock):** For more complex animations like the preloader.
3.  **Database: SQLite**
    - Simple, fast, and file-based, making it ideal for this project.
### Key Features
- **Multilingual:** Implemented using a `translations.json` file and a Flask `context_processor`.
- **Dynamic Content:** All posts and projects are fetched from the database.
- **Markdown Support:** Articles are written in Markdown and dynamically converted to HTML.
- **Scroll Animations:** Created using the `IntersectionObserver` API.
### Conclusion
Flask allowed me to build a fully custom, fast, and modern website without unnecessary complexity.
"""
}
blog_content_ar = {
    'landing-page-design-principles': """
### مقدمة: بوابتك إلى عالمك
صفحة الهبوط هي نقطة الاتصال الأولى للعديد من المستخدمين مع عملك. هدفها المحدد هو تحويل الزائر إلى عميل. يستكشف هذا المقال 5 مبادئ أساسية لتصميم صفحات هبوط عالية التحويل.
### المبدأ الأول: الوضوح هو الملك
يجب أن يفهم المستخدم غرض صفحتك وقيمتها في غضون 5 ثوانٍ.
- **العنوان الرئيسي:** يجب أن يكون جذابًا وقصيرًا وذا صلة.
- **العنوان الفرعي:** يشرح العنوان الرئيسي.
- **إزالة المشتتات:** تخلص من قوائم التنقل والروابط غير الضرورية.
### المبدأ الثاني: عرض القيمة الفريدة (UVP)
أجب بوضوح: لماذا يجب على المستخدم اختيارك بدلاً من المنافسين؟
### المبدأ الثالث: دعوة قوية لاتخاذ إجراء (CTA)
يعد زر CTA العنصر الأكثر أهمية. يجب أن يكون مرئيًا وواضحًا وفي مكان جيد.
### المبدأ الرابع: الاستخدام الذكي للعناصر المرئية
استخدم صورًا عالية الجودة ومساحة بيضاء وتأكد من وجود تصميم سريع الاستجابة. يعالج الدماغ المرئيات أسرع من النصوص.
### المبدأ الخامس: الدليل الاجتماعي
يثق المستخدمون في الشركات التي يؤيدها الآخرون. استخدم شهادات العملاء وشعارات الشركاء.
### خاتمة
يعد تصميم صفحة هبوط ناجحة عملية متكررة. اتباع هذه المبادئ والاختبار المستمر سيعزز بشكل كبير معدلات التحويل لديك.
""",
    'website-speed-and-seo': """
### مقدمة: الوقت من ذهب، خاصة على الويب!
في عالم اليوم الرقمي، صبر المستخدمين قليل. سرعة الموقع حاسمة ليس فقط لتجربة المستخدم (UX) ولكن أيضًا كعامل رئيسي في تحسين محركات البحث (SEO).
### 1. السرعة كعامل تصنيف مباشر
أكدت جوجل رسميًا أن سرعة الموقع هي إشارة تصنيف، خاصة مع إدخال **Core Web Vitals**.
### 2. ما هي Core Web Vitals؟
تقيس هذه المقاييس تجربة المستخدم الحقيقية: LCP (سرعة التحميل)، FID (التفاعلية)، و CLS (الاستقرار البصري). يحصل الموقع البطيء على درجة سيئة.
### 3. التأثیر على معدل الارتداد
كل ثانية من تأخير التحميل تزيد بشكل كبير من معدل الارتداد. معدل الارتداد المرتفع هو إشارة سلبية قوية لجوجل.
### 4. التأثير على ميزانية الزحف
لدى روبوتات جوجل وقت محدود للزحف إلى موقعك. يعني الموقع البطيء فهرسة عدد أقل من الصفحات.
### كيف تحسن سرعة موقعك؟
- **تحسين الصور:** ضغط واستخدام التنسيقات الحديثة.
- **استخدام CDN:** توزيع المحتوى عالميًا.
- **تقليل CSS و JavaScript:** تصغير ملفاتك.
- **تمكين التخزين المؤقت للمتصفح.**
- **اختیار استضافة جيدة.**
### خاتمة
سرعة الموقع ضرورة. إنها تؤثر بشكل مباشر على تصنيفك في جوجل ونجاح عملك.
""",
    'how-i-built-this-website-with-flask': """
### مقدمة: لماذا فلاسك؟
لبناء هذا الموقع، كنت بحاجة إلى أداة توفر **المرونة** و **البساطة**. كان **فلاسك (Flask)**، إطار العمل المصغر الشهير في بايثون، هو الخيار الأمثل.
### الهيكلية والتقنيات الأساسية
1.  **الواجهة الخلفية: بايثون وفلاسك**
    - **فلاسك:** للتعامل مع المسارات ومنطق التطبيق.
    - **SQLAlchemy:** كـ ORM لإدارة قواعد البياناتเชิง الكائنات مع SQLite.
    - **Jinja2:** لبناء صفحات HTML ديناميكية.
2.  **الواجهة الأمامية: HTML, CSS, و JavaScript**
    - **JavaScript (Vanilla):** للتفاعلات والرسوم المتحركة المخصصة.
    - **GSAP (GreenSock):** للرسوم المتحركة الأكثر تعقيدًا مثل أداة التحميل المسبق.
3.  **قاعدة البيانات: SQLite**
    - بسيطة وسريعة وتعتمد على الملفات، مما يجعلها مثالية لهذا المشروع.
### الميزات الرئيسية
- **متعدد اللغات:** تم تنفيذه باستخدام ملف `translations.json` و `context_processor` في فلاسك.
- **محتوى ديناميكي:** يتم جلب جميع المشاركات والمشاريع من قاعدة البيانات.
- **دعم Markdown:** تُكتب المقالات بـ Markdown ويتم تحويلها ديناميكيًا إلى HTML.
- **رسوم متحركة عند التمرير:** تم إنشاؤها باستخدام `IntersectionObserver` API.
### خاتمة
سمح لي فلاسك ببناء موقع ويب مخصص بالكامل وسريع وحديث دون تعقيدات غير ضرورية.
"""
}
blog_content_de = {
    'landing-page-design-principles': """
### Einführung: Das Tor zu Ihrer Welt
Eine Landing Page ist der erste Kontaktpunkt für viele Nutzer mit Ihrem Unternehmen. Sie hat ein spezifisches Ziel: einen Besucher in einen Kunden oder Lead zu konvertieren. Dieser Artikel untersucht 5 Schlüsselprinzipien für die Gestaltung von Landing Pages mit hoher Konversionsrate.
### Prinzip 1: Klarheit ist entscheidend
Ein Benutzer muss den Zweck und den Wert Ihrer Seite innerhalb von 5 Sekunden verstehen.
- **Überschrift:** Muss ansprechend, kurz und relevant sein.
- **Unterüberschrift:** Erläutert die Überschrift.
- **Ablenkungen entfernen:** Beseitigen Sie unnötige Navigation und Links.
### Prinzip 2: Einzigartiges Wertversprechen (UVP)
Beantworten Sie klar: Warum sollte ein Benutzer Sie gegenüber der Konkurrenz wählen?
### Prinzip 3: Ein starker Call to Action (CTA)
Der CTA-Button ist Ihr wichtigstes Element. Er muss sichtbar, klar und gut platziert sein.
### Prinzip 4: Intelligenter Einsatz von visuellen Elementen
Verwenden Sie hochwertige Bilder, Leerraum und stellen Sie ein responsives Design sicher. Das Gehirn verarbeitet visuelle Reize schneller als Text.
### Prinzip 5: Soziale Beweise (Social Proof)
Benutzer vertrauen Unternehmen, die von anderen empfohlen werden. Verwenden Sie Testimonials und Partnerlogos.
### Fazit
Die Gestaltung einer erfolgreichen Landing Page ist ein iterativer Prozess. Die Befolgung dieser Prinzipien und kontinuierliches Testen werden Ihre Konversionsraten erheblich steigern.
""",
    'website-speed-and-seo': """
### Einführung: Zeit ist Geld, besonders im Web!
In der heutigen digitalen Welt ist die Geduld der Nutzer gering. Die Geschwindigkeit der Website ist nicht nur für die Benutzererfahrung (UX) entscheidend, sondern auch ein wichtiger Faktor für die Suchmaschinenoptimierung (SEO).
### 1. Geschwindigkeit als direkter Rankingfaktor
Google hat offiziell bestätigt, dass die Seitengeschwindigkeit ein Ranking-Signal ist, insbesondere mit der Einführung der **Core Web Vitals**.
### 2. Was sind Core Web Vitals?
Diese Metriken messen die reale Benutzererfahrung: LCP (Ladegeschwindigkeit), FID (Interaktivität) und CLS (visuelle Stabilität). Eine langsame Seite schneidet schlecht ab.
### 3. Auswirkungen auf die Absprungrate
Jede Sekunde Ladeverzögerung erhöht die Absprungrate drastisch. Eine hohe Absprungrate ist ein starkes negatives Signal für Google.
### 4. Auswirkungen auf das Crawl-Budget
Googlebots haben eine begrenzte Zeit, um Ihre Website zu crawlen. Eine langsame Website bedeutet, dass weniger Seiten indiziert werden.
### Wie Sie Ihre Seitengeschwindigkeit verbessern
- **Bilder optimieren:** Komprimieren Sie und verwenden Sie moderne Formate.
- **Verwenden Sie ein CDN:** Verteilen Sie Inhalte global.
- **Minimieren Sie CSS und JavaScript:** Minifizieren Sie Ihre Dateien.
- **Aktivieren Sie das Browser-Caching.**
- **Wählen Sie einen guten Hoster.**
### Fazit
Die Geschwindigkeit der Website ist eine Notwendigkeit. Sie wirkt sich direkt auf Ihr Google-Ranking und Ihren Geschäftserfolg aus.
""",
    'how-i-built-this-website-with-flask': """
### Einführung: Warum Flask?
Für den Bau dieser Website benötigte ich ein Werkzeug, das sowohl **Flexibilität** als auch **Einfachheit** bot. **Flask**, das beliebte Python-Micro-Framework, war die perfekte Wahl.
### Architektur und Kerntechnologien
1.  **Backend: Python und Flask**
    - **Flask:** Zur Handhabung von Routen und Anwendungslogik.
    - **SQLAlchemy:** Als ORM für objektorientierte Datenbankverwaltung mit SQLite.
    - **Jinja2:** Zum Erstellen dynamischer HTML-Seiten.
2.  **Frontend: HTML, CSS und JavaScript**
    - **Vanilla JavaScript:** Für benutzerdefinierte Interaktionen und Animationen.
    - **GSAP (GreenSock):** Für komplexere Animationen wie den Preloader.
3.  **Datenbank: SQLite**
    - Einfach, schnell und dateibasiert, was es ideal für dieses Projekt macht.
### Hauptmerkmale
- **Mehrsprachigkeit:** Implementiert mit einer `translations.json`-Datei und einem Flask-`context_processor`.
- **Dynamischer Inhalt:** Alle Beiträge und Projekte werden aus der Datenbank abgerufen.
- **Markdown-Unterstützung:** Artikel werden in Markdown geschrieben und dynamisch in HTML umgewandelt.
- **Scroll-Animationen:** Erstellt mit der `IntersectionObserver` API.
### Fazit
Flask ermöglichte es mir, eine vollständig benutzerdefinierte, schnelle und moderne Website ohne unnötige Komplexität zu erstellen.
"""
}
project_content_fa = {
    'bi-dashboard': """
یک راهکار جامع هوش تجاری (BI) که داده‌های فروش شما را به بینش‌های استراتژیک و قابل درک تبدیل می‌کند. در این پروژه، ما با چالش تبدیل داده‌های خام و پراکنده به یک داشبورد مدیریتی یکپارچه روبرو بودیم.

### چالش اصلی
شرکت مشتری با حجم عظیمی از داده‌های فروش مواجه بود که تحلیل آن‌ها زمان‌بر و نیازمند تخصص فنی بود. مدیران نمی‌توانستند به سرعت شاخص‌های کلیدی عملکرد (KPI) را ارزیابی کرده و تصمیمات به‌موقع بگیرند.

### راهکار ما
ما یک پلتفرم SaaS با معماری مدرن طراحی و توسعه دادیم که به صورت لحظه‌ای داده‌ها را از منابع مختلف دریافت کرده و در قالب نمودارها و گزارش‌های بصری جذاب نمایش می‌دهد. این داشبورد به مدیران اجازه می‌دهد تا معیارهایی مانند نرخ تبدیل، هزینه جذب مشتری (CAC) و ارزش طول عمر مشتری (LTV) را به سادگی رصد کنند.

### تکنولوژی‌های کلیدی
* **Backend:** Python, Flask-RESTX برای ساخت APIهای قدرتمند.
* **Data Processing:** کتابخانه Pandas برای پاک‌سازی و تحلیل داده‌ها.
* **Frontend:** فریم‌ورک Chart.js برای ایجاد نمودارهای تعاملی و زیبا.
* **Database:** PostgreSQL برای مدیریت بهینه حجم بالای داده‌ها.

### نتایج
کاهش ۵۰ درصدی زمان لازم برای تهیه گزارش‌های ماهانه و افزایش ۲۰ درصدی دقت در پیش‌بینی فروش سه ماهه، از دستاوردهای اصلی این پروژه بود.
"""
}
project_content_en = {
    'bi-dashboard': """
A comprehensive Business Intelligence (BI) solution that transforms your sales data into strategic, understandable insights. In this project, we faced the challenge of converting raw, scattered data into a unified management dashboard.

### The Main Challenge
The client company was dealing with a massive volume of sales data, the analysis of which was time-consuming and required technical expertise. Managers couldn't quickly assess Key Performance Indicators (KPIs) and make timely decisions.

### Our Solution
We designed and developed a SaaS platform with a modern architecture that receives data from various sources in real-time and displays it in the form of attractive visual charts and reports. This dashboard allows managers to easily monitor metrics such as conversion rate, Customer Acquisition Cost (CAC), and Customer Lifetime Value (LTV).

### Key Technologies
* **Backend:** Python, Flask-RESTX for building powerful APIs.
* **Data Processing:** The Pandas library for data cleaning and analysis.
* **Frontend:** The Chart.js framework for creating beautiful, interactive charts.
* **Database:** PostgreSQL for efficiently managing large volumes of data.

### The Results
A 50% reduction in the time required to prepare monthly reports and a 20% increase in the accuracy of quarterly sales forecasting were the main achievements of this project.
"""
}

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

# --- Database Models (UPDATED) ---
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

# --- DB Initialization Command (UPDATED) ---
@app.cli.command('init-db')
def init_db_command():
    db.drop_all()
    db.create_all()
    print("Seeding data...")

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
        content_ar=project_content_en['bi-dashboard'],
        content_de=project_content_en['bi-dashboard'],
        image_file='project-dashboard-mockup.jpg',
        tags_fa='هوش تجاری, تحلیل داده, SaaS, پایتون, Flask, Chart.js',
        tags_en='Business Intelligence, Data Analysis, SaaS, Python, Flask, Chart.js',
        tags_ar='ذكاء الأعمال, تحليل البيانات, SaaS, بايثون, فلاسك, Chart.js',
        tags_de='Business Intelligence, Datenanalyse, SaaS, Python, Flask, Chart.js',
        display_order=3
    )


    story1 = Story(title='بازآفرینی یک برند', slug='reimagining-a-brand', excerpt='چگونه یک برند قدیمی را برای نسل جدید بازطراحی کردیم؟', content='متن کامل داستان...', image_file='story-brand-reimagined.jpg', display_order=1)
    story2 = Story(title='مصاحبه با یک مینیمالیست', slug='interview-with-a-minimalist', excerpt='گفتگویی با «سارا اکبری»، طراح UI.', content='متن کامل داستان...', image_file='story-minimalist-designer.jpg', display_order=2)

    db.session.add_all([post1, post2, post3, project1, project2, project3, story1, story2])
    db.session.commit()
    print("Database has been initialized and seeded successfully.")

# --- Context Processor ---
@app.context_processor
def inject_shared_data():
    lang = request.view_args.get('lang', 'fa') if request.view_args else 'fa'
    session['lang'] = lang # Store lang in session for API routes
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

# --- Routes (UPDATED) ---
@app.route('/')
def index():
    return redirect(url_for('home', lang='fa'))

@app.route('/<lang>/')
def home(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    try: latest_posts = Post.query.order_by(Post.pub_date.desc()).limit(2).all()
    except: latest_posts = []
    return render_template('index.html', latest_posts=latest_posts)

@app.route('/<lang>/about')
def about(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    return render_template('about.html')

@app.route('/<lang>/projects')
def projects(lang):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    try: all_projects = Project.query.order_by(Project.display_order).all()
    except: all_projects = []
    return render_template('projects.html', projects=all_projects)

@app.route('/<lang>/project/<string:slug>')
def project_detail(lang, slug):
    if lang not in ['fa', 'en', 'ar', 'de']: return "Language not supported", 404
    project = Project.query.filter_by(slug=slug).first_or_404()
    # This check prevents the error for projects without detailed content
    if not project.content_fa and not project.content_en:
        if project.project_url:
            return redirect(project.project_url)
        else:
            return redirect(url_for('projects', lang=lang))
    return render_template('project_detail.html', project=project)

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
    try: all_stories = Story.query.order_by(Story.display_order).all()
    except: all_stories = []
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
        error_message = translations.get(error_lang, {}).get('js_ai_error', 'An error occurred.')
        return jsonify({'text': error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)