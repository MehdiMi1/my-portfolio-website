document.addEventListener('DOMContentLoaded', function() {

    // Helper function to get translated text from the global object set in base.html
    const t = (key) => {
        return window.translations?.[window.currentLang]?.[key] || key;
    };

    // =============================================
    // ===         Preloader Logic (Updated)     ===
    // =============================================
    const preloader = document.getElementById('preloader');
    if (preloader) {
        document.body.style.overflow = 'hidden';
        window.addEventListener('load', () => {
            setTimeout(() => {
                if (preloader) {
                    preloader.classList.add('hidden');
                }
                preloader.addEventListener('transitionend', function handleTransitionEnd() {
                    if (preloader.parentNode) {
                        preloader.parentNode.removeChild(preloader);
                    }
                    document.body.style.overflow = '';
                    preloader.removeEventListener('transitionend', handleTransitionEnd);
                });
            }, 1500);
        });
    }

    // =============================================
    // ===         Header Scroll Effect          ===
    // =============================================
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            header.classList.toggle('scrolled', window.scrollY > 50);
        });
    }

    // =============================================
    // ===         Back to Top Button            ===
    // =============================================
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            backToTopBtn.classList.toggle('visible', window.scrollY > 300);
        });
        backToTopBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // =============================================
    // ===         Mobile Navigation Toggle      ===
    // =============================================
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const mobileNav = document.getElementById('mobile-nav');
    if (hamburgerBtn && mobileNav) {
        const toggleNav = (forceClose = false) => {
            const isActive = mobileNav.classList.contains('active');
            if (forceClose || isActive) {
                hamburgerBtn.classList.remove('active');
                mobileNav.classList.remove('active');
                document.body.style.overflow = '';
            } else {
                hamburgerBtn.classList.add('active');
                mobileNav.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        };
        hamburgerBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleNav();
        });
        mobileNav.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                toggleNav(true);
            }
        });
    }

    // =============================================
    // ===         Multi-language Switcher       ===
    // =============================================
    const langSelectorBtn = document.getElementById('lang-selector-btn');
    const langDropdown = document.getElementById('lang-dropdown');
    if (langSelectorBtn && langDropdown) {
        langSelectorBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            langDropdown.classList.toggle('show');
        });
        document.addEventListener('click', () => {
            if (langDropdown.classList.contains('show')) {
                langDropdown.classList.remove('show');
            }
        });
    }

    // =============================================
    // ===  Page Transition Script (REMOVED)     ===
    // =============================================
    // The problematic page transition script has been completely removed to ensure all links work reliably.
    // window.addEventListener('pageshow', ...); is also removed as it was part of this feature.

    // =============================================
    // ===         Reveal on Scroll Animation    ===
    // =============================================
    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    if (revealElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        revealElements.forEach(element => observer.observe(element));
    }

    // =============================================
    // ===         Form Submission (Formspree)   ===
    // =============================================
    async function handleFormSubmit(form, statusDiv, successMessageKey) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            statusDiv.textContent = t('js_form_pending');
            statusDiv.className = '';
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'Accept': 'application/json' }
                });
                if (response.ok) {
                    statusDiv.textContent = t(successMessageKey);
                    statusDiv.classList.add('success');
                    form.reset();
                } else {
                    const data = await response.json();
                    statusDiv.textContent = data.error || t('js_form_error');
                    statusDiv.classList.add('error');
                }
            } catch (error) {
                statusDiv.textContent = t('js_form_error');
                statusDiv.classList.add('error');
            }
        });
    }

    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        handleFormSubmit(contactForm, document.getElementById('form-status'), 'js_form_success');
    }
    
    // =============================================
    // ===         Generic Filtering Logic       ===
    // =============================================
    function initializeFilter(filterContainerId, itemSelector) {
        const filterContainer = document.getElementById(filterContainerId);
        if (!filterContainer) return;
        const items = document.querySelectorAll(itemSelector);
        if (items.length === 0) return;
        filterContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-btn')) {
                filterContainer.querySelector('.active').classList.remove('active');
                e.target.classList.add('active');
                const filterValue = e.target.dataset.filter;
                items.forEach(item => {
                    const itemCategory = item.dataset.category;
                    if (filterValue === 'all' || itemCategory === filterValue) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
            }
        });
    }
    
    initializeFilter('blog-filters', '.blog-grid .post-card');
    initializeFilter('story-filters', '.stories-container .story-parallax-item');

    // =============================================
    // ===         AI Chat Functionality         ===
    // =============================================
    // The AI chat logic from your original file should be here
    
    // =============================================
    // ===         Skill Card 3D Hover Effect    ===
    // =============================================
    // The 3D hover logic from your original file should be here

    // =============================================
    // ===      NEW: Animated Counters           ===
    // =============================================
    function animateCounters() {
        const counters = document.querySelectorAll('.stat-number');
        if (counters.length === 0) return;
        const speed = 200;
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const updateCount = () => {
                        const target = +counter.getAttribute('data-target');
                        const count = +counter.innerText.replace(/,/g, '');
                        const increment = target / speed;
                        if (count < target) {
                            counter.innerText = Math.ceil(count + increment).toLocaleString();
                            setTimeout(updateCount, 15);
                        } else {
                            counter.innerText = target.toLocaleString();
                        }
                    };
                    updateCount();
                    observer.unobserve(counter);
                }
            });
        }, { threshold: 0.5 });
        counters.forEach(counter => {
            observer.observe(counter);
        });
    }
    animateCounters();

    // =============================================
    // ===   NEW: SEO Meta Tag Generator Tool    ===
    // =============================================
    function initializeSeoTool() {
        const seoTitleInput = document.getElementById('seo-title');
        const seoDescInput = document.getElementById('seo-desc');
        const previewTitle = document.getElementById('preview-title');
        const previewDesc = document.getElementById('preview-desc');
        const titleCounter = document.getElementById('title-counter');
        const descCounter = document.getElementById('desc-counter');
        if (!seoTitleInput) return;
        const lang = window.currentLang || 'fa';
        const defaultTitle = lang === 'fa' ? "عنوان شما در اینجا نمایش داده می‌شود" : "Your Title Will Be Displayed Here";
        const defaultDesc = lang === 'fa' ? "توضیحات متای شما پس از وارد کردن در کادر مربوطه، در این قسمت نمایش داده خواهد شد..." : "Your meta description will be shown in this area after you type it in the box above...";
        function updatePreview() {
            const titleValue = seoTitleInput.value;
            previewTitle.textContent = titleValue || defaultTitle;
            const titleLength = titleValue.length;
            titleCounter.textContent = `${titleLength} / 60`;
            titleCounter.style.color = titleLength > 60 ? '#ff6b6b' : '';
            titleCounter.style.fontWeight = titleLength > 60 ? 'bold' : 'normal';
            const descValue = seoDescInput.value;
            previewDesc.textContent = descValue || defaultDesc;
            const descLength = descValue.length;
            descCounter.textContent = `${descLength} / 160`;
            descCounter.style.color = descLength > 160 ? '#ff6b6b' : '';
            descCounter.style.fontWeight = descLength > 160 ? 'bold' : 'normal';
        }
        seoTitleInput.addEventListener('input', updatePreview);
        seoDescInput.addEventListener('input', updatePreview);
    }
    initializeSeoTool();

}); // End of DOMContentLoaded listener