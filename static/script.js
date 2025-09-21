document.addEventListener('DOMContentLoaded', function() {

    // Helper function to get translated text from the global object set in base.html
    const t = (key) => {
        // Use optional chaining to prevent errors if keys don't exist
        return window.translations?.[window.currentLang]?.[key] || key;
    };

    // =============================================
    // ===  REFINED & FIXED Preloader Logic      ===
    // =============================================
    const preloader = document.getElementById('preloader');
    if (preloader) {
        // Prevent body scroll while preloader is active
        document.body.style.overflow = 'hidden';

        window.addEventListener('load', () => {
            // This timeout ensures the preloader is visible for a minimum duration,
            // allowing the animations to be appreciated.
            setTimeout(() => {
                // Add 'hidden' class to trigger the CSS fade-out transition
                if (preloader) {
                    preloader.classList.add('hidden');
                }

                // Listen for the end of the fade-out transition to remove the element
                // and restore scrolling. This synchronizes the logic with the animation.
                preloader.addEventListener('transitionend', function handleTransitionEnd() {
                    if (preloader.parentNode) {
                        preloader.parentNode.removeChild(preloader);
                    }
                    document.body.style.overflow = '';
                    // Clean up the event listener to prevent it from firing again
                    preloader.removeEventListener('transitionend', handleTransitionEnd);
                });

            }, 2500); // Minimum time the preloader will be visible in milliseconds.
        });
    }


    // =============================================
    // ===      Header Scroll Effect             ===
    // =============================================
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            // Adds the 'scrolled' class to the header when the user scrolls down more than 50px
            header.classList.toggle('scrolled', window.scrollY > 50);
        });
    }

    // =============================================
    // ===      Back to Top Button               ===
    // =============================================
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            // Makes the button visible when the user scrolls down more than 300px
            backToTopBtn.classList.toggle('visible', window.scrollY > 300);
        });
        backToTopBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // =============================================
    // ===      Mobile Navigation Toggle         ===
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

        // Close nav if a link is clicked
        mobileNav.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                toggleNav(true);
            }
        });
    }

    // =============================================
    // ===  FIXED Multi-language Switcher        ===
    // =============================================
    const langSelectorBtn = document.getElementById('lang-selector-btn');
    const langDropdown = document.getElementById('lang-dropdown');
    if (langSelectorBtn && langDropdown) {
        langSelectorBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevents the document click listener from firing immediately
            langDropdown.classList.toggle('show');
        });

        // Use the correct server-generated URLs from the href attributes
        langDropdown.addEventListener('click', function(e) {
            const targetLink = e.target.closest('a.lang-option');
            if (!targetLink) return;

            e.preventDefault();
            const destinationUrl = targetLink.href;
            const transitionOverlay = document.querySelector('.page-transition-overlay');

            if (transitionOverlay) {
                transitionOverlay.classList.add('active');
                setTimeout(() => {
                    window.location.href = destinationUrl;
                }, 600); // Duration should match the CSS transition
            } else {
                window.location.href = destinationUrl;
            }
        });

        // Close dropdown when clicking anywhere else on the page
        document.addEventListener('click', () => {
            if (langDropdown.classList.contains('show')) {
                langDropdown.classList.remove('show');
            }
        });
    }

    // =============================================
    // ===      Page Transition on Nav Links     ===
    // =============================================
    const transitionOverlay = document.querySelector('.page-transition-overlay');
    if (transitionOverlay) {
        document.querySelectorAll('a:not([target="_blank"]):not(.lang-option):not([href^="#"]):not([href^="mailto"]):not([href^="tel"])').forEach(link => {
            link.addEventListener('click', function(e) {
                const url = new URL(this.href);
                // Only apply transition for internal navigation
                if (url.origin === window.location.origin) {
                    e.preventDefault();
                    transitionOverlay.classList.add('active');
                    setTimeout(() => {
                        window.location = this.href;
                    }, 600); // Match CSS transition duration
                }
            });
        });
    }

    // Handle back/forward browser navigation
    window.addEventListener('pageshow', (event) => {
        if (event.persisted && transitionOverlay) {
            transitionOverlay.classList.remove('active');
        }
    });

    // =============================================
    // ===      Reveal on Scroll Animation       ===
    // =============================================
    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    if (revealElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target); // Stop observing once visible for performance
                }
            });
        }, {
            threshold: 0.1
        });
        revealElements.forEach(element => observer.observe(element));
    }

    // =============================================
    // ===  FIXED Form Submission (Formspree)    ===
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

    const leadMagnetForm = document.getElementById('lead-magnet-form');
    if (leadMagnetForm) {
        handleFormSubmit(leadMagnetForm, document.getElementById('lead-magnet-status'), 'js_checklist_success');
    }

    // =============================================
    // ===      Blog Post Filtering              ===
    // =============================================
    const filterContainer = document.getElementById('blog-filters');
    if (filterContainer) {
        const blogPosts = document.querySelectorAll('.blog-grid .post-card');
        filterContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-btn')) {
                filterContainer.querySelector('.active').classList.remove('active');
                e.target.classList.add('active');
                const filterValue = e.target.dataset.filter;

                blogPosts.forEach(post => {
                    const postCategory = post.dataset.category;
                    if (filterValue === 'all' || postCategory === filterValue) {
                        post.style.display = 'block';
                    } else {
                        post.style.display = 'none';
                    }
                });
            }
        });
    }

    // =============================================
    // ===  FIXED AI Chat Functionality          ===
    // =============================================
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        const userInput = document.getElementById('user-input');
        const chatBox = document.getElementById('chat-box');
        const typingIndicator = document.getElementById('typing-indicator');

        const addMessageToChat = (sender, htmlContent) => {
            const messageWrapper = document.createElement('div');
            messageWrapper.className = `chat-message ${sender}-message`;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.innerHTML = sender === 'user' ? '👤' : '✨';
            
            const content = document.createElement('div');
            content.className = 'message-content';
            content.innerHTML = htmlContent;

            messageWrapper.appendChild(avatar);
            messageWrapper.appendChild(content);
            chatBox.appendChild(messageWrapper);
            chatBox.scrollTop = chatBox.scrollHeight;
        };
        
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const messageText = userInput.value.trim();
            if (!messageText) return;

            addMessageToChat('user', `<p>${messageText.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</p>`);
            userInput.value = '';
            typingIndicator.style.display = 'flex';
            
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: messageText })
                });

                const data = await response.json();
                
                if (response.ok) {
                    addMessageToChat('ai', data.text); // Response from backend is markdown rendered to HTML
                } else {
                    addMessageToChat('ai', `<p>${data.text || t('js_ai_error')}</p>`);
                }

            } catch (error) {
                addMessageToChat('ai', `<p>${t('js_ai_error')}</p>`);
            } finally {
                typingIndicator.style.display = 'none';
            }
        });
    }

    // =============================================
    // ===      Skill Card 3D Hover Effect       ===
    // =============================================
    const skillCards = document.querySelectorAll('.skill-card');
    skillCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 10; // Intensity factor
            const rotateY = (centerX - x) / 10; // Intensity factor

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            
            // For the radial gradient effect in CSS
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
        });
    });

}); // End DOMContentLoaded