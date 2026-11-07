/**
 * Sahil Nawaz Portfolio — Vanilla JavaScript Interactivity
 * Step 11: Complete Interactions, Animations, and Frontend Validation
 */

document.addEventListener("DOMContentLoaded", () => {
  try {
    initSmoothScroll();
    initMobileMenu();
    initActiveNavLink();
    initHeaderScroll();
    initBackToTop();
    initRoleTypingAnimation();
    initScrollReveal();
    initContactForm();
    initDynamicProjects();
    initProjectFilters();
    initCopyrightYear();
  } catch (err) {
    console.error("Initialization error in portfolio scripts:", err);
  }
});

/**
 * 01. Smooth Scrolling for Internal Navigation Links with Sticky Header Offset
 */
function initSmoothScroll() {
  const scrollLinks = document.querySelectorAll('a[href^="#"]');

  scrollLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      const targetId = link.getAttribute("href");
      if (!targetId || targetId === "#") return;

      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        const headerHeight = 78;
        const elementPosition = targetEl.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - headerHeight;

        window.scrollTo({
          top: offsetPosition,
          behavior: "smooth"
        });

        // Update URL hash cleanly without instant jump
        if (history.pushState) {
          history.pushState(null, null, targetId);
        } else {
          window.location.hash = targetId;
        }
      }
    });
  });
}

/**
 * 02. Mobile Navigation Menu Toggle with Full Accessibility
 */
function initMobileMenu() {
  const menuToggle = document.querySelector(".menu-toggle");
  const siteNav = document.getElementById("primary-navigation") || document.querySelector(".site-nav");
  const menuIcon = document.querySelector(".menu-icon");

  if (!menuToggle || !siteNav) return;

  function setMenuState(open) {
    if (open) {
      siteNav.classList.add("open");
      menuToggle.setAttribute("aria-expanded", "true");
      if (menuIcon) menuIcon.textContent = "✕";
    } else {
      siteNav.classList.remove("open");
      menuToggle.setAttribute("aria-expanded", "false");
      if (menuIcon) menuIcon.textContent = "☰";
    }
  }

  // Toggle button click
  menuToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    const isCurrentlyOpen = siteNav.classList.contains("open");
    setMenuState(!isCurrentlyOpen);
  });

  // Close menu when clicking outside
  document.addEventListener("click", (e) => {
    if (siteNav.classList.contains("open") && !siteNav.contains(e.target) && !menuToggle.contains(e.target)) {
      setMenuState(false);
    }
  });

  // Close menu on Escape key press
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && siteNav.classList.contains("open")) {
      setMenuState(false);
      menuToggle.focus();
    }
  });

  // Close menu when any nav link is tapped
  siteNav.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", () => {
      setMenuState(false);
    });
  });

  // Auto-close menu if viewport resized to desktop
  window.addEventListener("resize", () => {
    if (window.innerWidth > 768 && siteNav.classList.contains("open")) {
      setMenuState(false);
    }
  });
}

/**
 * 03. ScrollSpy & Active Navigation Link Tracking
 */
function initActiveNavLink() {
  const navLinks = document.querySelectorAll(".site-nav .nav-link");
  const sections = document.querySelectorAll("section[id]");

  if (!sections.length || !navLinks.length) return;

  let isTicking = false;

  const updateActiveLink = () => {
    let currentSectionId = "";
    const scrollPosition = window.scrollY + 130;

    sections.forEach((section) => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      if (scrollPosition >= top && scrollPosition < top + height) {
        currentSectionId = section.getAttribute("id");
      }
    });

    if (currentSectionId) {
      navLinks.forEach((link) => {
        const href = link.getAttribute("href");
        if (href === `#${currentSectionId}`) {
          link.classList.add("active");
        } else if (href && href.startsWith("#")) {
          link.classList.remove("active");
        }
      });
    }

    isTicking = false;
  };

  window.addEventListener("scroll", () => {
    if (!isTicking) {
      window.requestAnimationFrame(updateActiveLink);
      isTicking = true;
    }
  }, { passive: true });

  updateActiveLink();
}

/**
 * 04. Sticky Header Elevation on Scroll
 */
function initHeaderScroll() {
  const header = document.querySelector(".site-header");
  if (!header) return;

  const handleScroll = () => {
    if (window.scrollY > 20) {
      header.classList.add("scrolled");
    } else {
      header.classList.remove("scrolled");
    }
  };

  window.addEventListener("scroll", handleScroll, { passive: true });
  handleScroll();
}

/**
 * 05. Back to Top Button
 */
function initBackToTop() {
  const backToTopBtn = document.getElementById("back-to-top");
  if (!backToTopBtn) return;

  backToTopBtn.addEventListener("click", (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  });
}

/**
 * 06. Typing Animation for Professional Role in Hero Section
 */
function initRoleTypingAnimation() {
  const typedEl = document.getElementById("typed-role");
  if (!typedEl) return;

  // Respect user preference for reduced motion
  const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) return;

  const roles = [
    "Forward Deployed Developer",
    "AI & ML Solutions Builder",
    "Frontend & Product Developer",
    "B.Tech CSE Undergrad · JBIET"
  ];

  let roleIdx = 0;
  let charIdx = roles[0].length;
  let isDeleting = true; // Start by deleting default pre-rendered text after a pause
  let pauseDuration = 2200;

  function typeTick() {
    const currentRole = roles[roleIdx];

    if (isDeleting) {
      charIdx--;
      typedEl.textContent = currentRole.substring(0, charIdx);
      if (charIdx === 0) {
        isDeleting = false;
        roleIdx = (roleIdx + 1) % roles.length;
        setTimeout(typeTick, 350);
        return;
      }
      setTimeout(typeTick, 40);
    } else {
      charIdx++;
      typedEl.textContent = currentRole.substring(0, charIdx);
      if (charIdx === currentRole.length) {
        isDeleting = true;
        setTimeout(typeTick, pauseDuration);
        return;
      }
      setTimeout(typeTick, 70);
    }
  }

  // Initial delay before first deletion cycle
  setTimeout(typeTick, 2000);
}

/**
 * 07. Subtle Scroll Reveal Animations using IntersectionObserver
 */
function initScrollReveal() {
  if (!("IntersectionObserver" in window)) return;

  // Respect reduced motion
  const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) return;

  const targets = document.querySelectorAll(
    ".section-wrapper, .highlights-bar, .skill-category-card, .project-card, .edu-journey-card, .contact-channel-card, .contact-form-box"
  );

  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("reveal-active");
          obs.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.12,
      rootMargin: "0px 0px -40px 0px"
    }
  );

  targets.forEach((target) => {
    target.classList.add("reveal-init");
    observer.observe(target);
  });
}

/**
 * 08. Contact Form — Frontend Validation & Success Preview
 */
function initContactForm() {
  const contactForm = document.getElementById("contact-form");
  const formAlert = document.getElementById("form-alert");
  const submitBtn = document.getElementById("submit-btn");

  const nameInput = document.getElementById("contact-name");
  const emailInput = document.getElementById("contact-email");
  const subjectInput = document.getElementById("contact-subject");
  const messageInput = document.getElementById("contact-message");

  const nameError = document.getElementById("name-error");
  const emailError = document.getElementById("email-error");
  const subjectError = document.getElementById("subject-error");
  const messageError = document.getElementById("message-error");

  const charCount = document.getElementById("char-count");
  const previewBox = document.getElementById("preview-box");
  const previewSender = document.getElementById("preview-sender");
  const previewEmail = document.getElementById("preview-email");
  const previewSubject = document.getElementById("preview-subject");
  const previewMessage = document.getElementById("preview-message");
  const previewDirectMail = document.getElementById("preview-direct-mail");
  const previewResetBtn = document.getElementById("preview-reset-btn");

  if (!contactForm) return;

  // Real-time character counter for textarea
  if (messageInput && charCount) {
    messageInput.addEventListener("input", () => {
      const currentLen = messageInput.value.length;
      charCount.textContent = `${currentLen} / 1000`;
      if (currentLen > 1000) {
        charCount.style.color = "#f87171";
      } else {
        charCount.style.color = "#8f837f";
      }
    });
  }

  // Clear field errors dynamically on keystroke
  [nameInput, emailInput, subjectInput, messageInput].forEach((input) => {
    if (!input) return;
    input.addEventListener("input", () => {
      if (input.classList.contains("is-invalid")) {
        input.classList.remove("is-invalid");
      }
      const errEl = document.getElementById(`${input.name}-error`);
      if (errEl) {
        errEl.textContent = "";
        errEl.classList.remove("visible");
      }
      if (formAlert && formAlert.classList.contains("error")) {
        showAlert("", "");
      }
    });
  });

  // Handle Form Submission
  contactForm.addEventListener("submit", (e) => {
    e.preventDefault();

    // Reset previous feedback
    showAlert("", "");
    clearFieldErrors();
    if (previewBox) previewBox.style.display = "none";

    const name = nameInput ? nameInput.value.trim() : "";
    const email = emailInput ? emailInput.value.trim() : "";
    const subject = subjectInput ? subjectInput.value.trim() : "";
    const message = messageInput ? messageInput.value.trim() : "";

    let hasErrors = false;
    let firstInvalidInput = null;

    // Validate Full Name
    if (!name) {
      setFieldError(nameInput, nameError, "Full Name is required.");
      hasErrors = true;
      if (!firstInvalidInput) firstInvalidInput = nameInput;
    } else if (name.length < 2) {
      setFieldError(nameInput, nameError, "Name must be at least 2 characters.");
      hasErrors = true;
      if (!firstInvalidInput) firstInvalidInput = nameInput;
    }

    // Validate Email Address
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      setFieldError(emailInput, emailError, "Email address is required.");
      hasErrors = true;
      if (!firstInvalidInput) firstInvalidInput = emailInput;
    } else if (!emailRegex.test(email)) {
      setFieldError(emailInput, emailError, "Please enter a valid email address (e.g., sahil@example.com).");
      hasErrors = true;
      if (!firstInvalidInput) firstInvalidInput = emailInput;
    }

    // Validate Subject (Optional, max 150 chars)
    if (subject && subject.length > 150) {
      setFieldError(subjectInput, subjectError, "Subject must not exceed 150 characters.");
      hasErrors = true;
      if (!firstInvalidInput) firstInvalidInput = subjectInput;
    }

    // Validate Message
    if (!message) {
      setFieldError(messageInput, messageError, "Message is required.");
      hasErrors = true;
      if (!firstInvalidInput) firstInvalidInput = messageInput;
    } else if (message.length < 10) {
      setFieldError(messageInput, messageError, "Please provide at least 10 characters so I can understand your inquiry.");
      hasErrors = true;
      if (!firstInvalidInput) firstInvalidInput = messageInput;
    } else if (message.length > 1000) {
      setFieldError(messageInput, messageError, "Message cannot exceed 1000 characters.");
      hasErrors = true;
      if (!firstInvalidInput) firstInvalidInput = messageInput;
    }

    // If validation fails, alert user and focus first error field
    if (hasErrors) {
      showAlert("Please review and fix the highlighted fields above.", "error");
      if (firstInvalidInput) {
        firstInvalidInput.focus();
      }
      return;
    }

    // Configure API base URL (configurable for local live server, static file, or Flask port 5000)
    const API_BASE_URL = (window.location.origin.includes("5000") || (window.location.protocol === "http:" && window.location.port === "5000"))
      ? ""
      : "http://127.0.0.1:5000";
    const endpoint = `${API_BASE_URL}/api/contact`;

    // Set loading state on submit button
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Sending to Flask Backend...</span>`;

    const payload = { name, email, subject, message };

    fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    })
      .then(async (response) => {
        const result = await response.json().catch(() => ({}));

        if (response.ok && result.success) {
          // Success Response from Flask Backend with SQLite Persistence
          const inquiryId = result.contact_id || (result.stored_data ? result.stored_data.id : "");
          const idBadge = inquiryId ? ` <span class="badge" style="background: rgba(16,185,129,0.15); color: #047857; padding: 2px 8px; border-radius: 999px; font-weight: 700; font-size: 0.8rem;">Ref #${inquiryId}</span>` : "";
          showAlert(
            `✔ <strong>Message Saved to SQLite Database!</strong> ${result.message || "Your message was successfully received."}${idBadge}<br><small style="opacity: 0.9;">Inquiry stored persistently in <code>database/portfolio.db</code>.</small>`,
            "success"
          );

          if (previewBox) {
            if (previewSender) previewSender.textContent = name;
            if (previewEmail) previewEmail.textContent = email;
            if (previewSubject) previewSubject.textContent = subject || "Forward Deployed Opportunity / Project Collaboration";
            if (previewMessage) previewMessage.textContent = message;

            if (previewDirectMail) {
              const mailSubject = encodeURIComponent(subject || `Inquiry from ${name} (Portfolio)`);
              const mailBody = encodeURIComponent(`${message}\n\n---\nSent by: ${name} (${email})`);
              previewDirectMail.href = `mailto:sahilnawaz257@gmail.com?subject=${mailSubject}&body=${mailBody}`;
            }

            previewBox.style.display = "block";
            previewBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
          }

          contactForm.reset();
          if (charCount) charCount.textContent = "0 / 1000";
        } else {
          // Server returned validation error (400)
          const errorMsg = result.error || "Failed to process message on backend.";
          if (result.field) {
            const fieldEl = document.getElementById(`contact-${result.field}`);
            const errEl = document.getElementById(`${result.field}-error`);
            setFieldError(fieldEl, errEl, errorMsg);
            if (fieldEl) fieldEl.focus();
          }
          showAlert(`⚠️ ${errorMsg}`, "error");
        }
      })
      .catch((err) => {
        console.warn("Backend API request failed or offline:", err);
        const mailtoLink = `mailto:sahilnawaz257@gmail.com?subject=${encodeURIComponent(subject || 'Inquiry from ' + name)}&body=${encodeURIComponent(message + '\n\n---\nSent by: ' + name + ' (' + email + ')')}`;

        showAlert(
          `⚠️ <strong>Flask Backend is currently offline</strong> (expected if server is not running on <code>http://127.0.0.1:5000</code>). Your details were verified on the frontend. <a href="${mailtoLink}" style="color: inherit; text-decoration: underline; font-weight: bold;">Click here to send directly via Email client</a> instead.`,
          "error"
        );

        if (previewBox) {
          if (previewSender) previewSender.textContent = name;
          if (previewEmail) previewEmail.textContent = email;
          if (previewSubject) previewSubject.textContent = subject || "Forward Deployed Opportunity / Project Collaboration";
          if (previewMessage) previewMessage.textContent = message;
          if (previewDirectMail) previewDirectMail.href = mailtoLink;

          previewBox.style.display = "block";
          previewBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      })
      .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      });
  });

  // Reset / Write Another Message button inside preview
  if (previewResetBtn) {
    previewResetBtn.addEventListener("click", () => {
      contactForm.reset();
      clearFieldErrors();
      showAlert("", "");
      if (previewBox) previewBox.style.display = "none";
      if (charCount) charCount.textContent = "0 / 1000";
      if (nameInput) nameInput.focus();
    });
  }

  function setFieldError(inputEl, errorEl, msg) {
    if (inputEl) {
      inputEl.classList.add("is-invalid");
      inputEl.setAttribute("aria-invalid", "true");
    }
    if (errorEl) {
      errorEl.textContent = msg;
      errorEl.classList.add("visible");
    }
  }

  function clearFieldErrors() {
    [nameInput, emailInput, subjectInput, messageInput].forEach((input) => {
      if (input) {
        input.classList.remove("is-invalid");
        input.removeAttribute("aria-invalid");
      }
    });
    [nameError, emailError, subjectError, messageError].forEach((err) => {
      if (err) {
        err.textContent = "";
        err.classList.remove("visible");
      }
    });
  }

  function showAlert(msg, type) {
    if (!formAlert) return;
    if (!msg) {
      formAlert.className = "form-alert";
      formAlert.style.display = "none";
      formAlert.innerHTML = "";
      return;
    }

    formAlert.className = `form-alert ${type}`;
    formAlert.innerHTML = msg;
    formAlert.style.display = "block";
  }
}

/**
 * 09. Dynamic Copyright Year in Footer
 */
function initCopyrightYear() {
  const yearElement = document.getElementById("current-year");
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }
}

/**
 * 10. Filter Projects by Category (Projects page / showcase)
 */
function initProjectFilters() {
  const filterButtons = document.querySelectorAll(".filter-btn");
  const projectCards = document.querySelectorAll(".project-card");

  if (!filterButtons.length || !projectCards.length) return;

  filterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const selectedFilter = btn.getAttribute("data-filter");

      projectCards.forEach((card) => {
        const cardCategory = card.getAttribute("data-category");

        if (selectedFilter === "all" || cardCategory === selectedFilter) {
          card.style.display = "flex";
          setTimeout(() => {
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
          }, 20);
        } else {
          card.style.opacity = "0";
          card.style.transform = "translateY(15px)";
          setTimeout(() => {
            card.style.display = "none";
          }, 200);
        }
      });
    });
  });
}

/**
 * 11. Dynamic Projects Loader from SQLite Database (Phase 2)
 * Fetches projects from GET /api/projects and populates the project grid
 * while retaining progressive enhancement fallback if API is unavailable.
 */
async function initDynamicProjects() {
  const grid = document.getElementById("project-grid");
  if (!grid) return;

  const API_BASE_URL = (window.location.origin.includes("5000") || (window.location.protocol === "http:" && window.location.port === "5000"))
    ? ""
    : "http://127.0.0.1:5000";
  const endpoint = `${API_BASE_URL}/api/projects`;

  try {
    const res = await fetch(endpoint, {
      headers: { "Accept": "application/json" }
    });

    if (!res.ok) {
      console.info("Projects API returned status:", res.status);
      return; // Keep existing static markup
    }

    const data = await res.json();
    if (data && data.success && Array.isArray(data.projects) && data.projects.length > 0) {
      renderProjectCards(grid, data.projects);
    }
  } catch (err) {
    console.info("Using static projects showcase (backend offline or standalone mode):", err.message);
  }
}

/**
 * Renders dynamic project cards into the given container
 */
function renderProjectCards(container, projects) {
  const cardsHtml = projects.map((p, idx) => {
    const num = String(idx + 1).padStart(2, "0");
    const titleLower = (p.title || "").toLowerCase();

    // Determine banner theme based on project title/type
    let bannerHtml = "";
    if (titleLower.includes("crowd") || titleLower.includes("density")) {
      bannerHtml = `
        <div class="project-banner banner-crowd" aria-hidden="true">
          <span class="stat-number">1,248</span>
          <span class="stat-label">Crowd Analytics Preview</span>
          <div class="crowd-bars">
            <span style="height: 18px;"></span>
            <span style="height: 32px;"></span>
            <span style="height: 24px;"></span>
            <span style="height: 48px;"></span>
            <span style="height: 36px;"></span>
            <span style="height: 40px;"></span>
            <span style="height: 22px;"></span>
          </div>
        </div>
      `;
    } else if (titleLower.includes("library")) {
      bannerHtml = `
        <div class="project-banner banner-library" aria-hidden="true">
          <div class="library-mockup">
            <small>LIBRARY & ATTENDANCE</small>
            <b>Books. Records.<br>Transactions.</b>
          </div>
        </div>
      `;
    } else if (titleLower.includes("brand") || titleLower.includes("guideline") || titleLower.includes("audit")) {
      bannerHtml = `
        <div class="project-banner banner-brand" aria-hidden="true">
          <div class="brand-mockup">
            <span class="brand-symbol">Aa</span>
            <div class="brand-palette">
              <small>AUDIT TOKENS</small>
              <div class="palette-swatches">
                <span style="background: #df7568;"></span>
                <span style="background: #f3b5aa;"></span>
                <span style="background: #e8d6c9;"></span>
                <span style="background: #39312e;"></span>
              </div>
            </div>
          </div>
        </div>
      `;
    } else {
      bannerHtml = `
        <div class="project-banner banner-api" aria-hidden="true">
          <div class="code-mockup">
            <span>&lt;/&gt; ${escapeHtml(p.title)}</span><br>
            <span style="color: #ef5966;">Active Production Build</span>
          </div>
        </div>
      `;
    }

    // Process technology badges
    const techItems = (p.technologies || "")
      .split(/[,|;]/)
      .map((t) => t.trim())
      .filter(Boolean);
    const techListHtml = techItems.length > 0
      ? techItems.map((t) => `<li>${escapeHtml(t)}</li>`).join("")
      : `<li>Software</li>`;

    // Process project action links (only rendered if URL is valid)
    let linksHtml = "";
    if (p.github_url && p.github_url.trim()) {
      linksHtml += `
        <a href="${escapeHtml(p.github_url)}" target="_blank" rel="noopener noreferrer" class="project-link-btn" aria-label="View ${escapeHtml(p.title)} on GitHub">
          <span class="btn-icon" aria-hidden="true">🐙</span> GitHub ↗
        </a>
      `;
    }
    if (p.live_demo_url && p.live_demo_url.trim()) {
      linksHtml += `
        <a href="${escapeHtml(p.live_demo_url)}" target="_blank" rel="noopener noreferrer" class="project-link-btn" aria-label="Live Demo for ${escapeHtml(p.title)}">
          <span class="btn-icon" aria-hidden="true">🌐</span> Live Demo ↗
        </a>
      `;
    }
    if (!linksHtml) {
      linksHtml = `<span style="font-size: 0.8rem; color: var(--text-muted); font-style: italic; padding: 6px 0;">Academic Repository / Core Project</span>`;
    }

    const tag = `${num} / ${escapeHtml(p.title.split(' ')[0])}`;

    return `
      <article class="project-card">
        ${bannerHtml}
        <div class="project-body">
          <span class="project-tag">${tag}</span>
          <h3 class="project-title">${escapeHtml(p.title)}</h3>
          <p class="project-desc">${escapeHtml(p.description)}</p>
          <ul class="project-tech" aria-label="Technologies used">
            ${techListHtml}
          </ul>
          <div class="project-links">
            ${linksHtml}
          </div>
        </div>
      </article>
    `;
  }).join("");

  container.innerHTML = cardsHtml;
}

/**
 * Escapes HTML characters safely to prevent XSS injection
 */
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
