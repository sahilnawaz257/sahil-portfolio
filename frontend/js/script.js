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

    // Display Success-Style Preview Box
    if (previewBox) {
      if (previewSender) previewSender.textContent = name;
      if (previewEmail) previewEmail.textContent = email;
      if (previewSubject) previewSubject.textContent = subject || "Forward Deployed Opportunity / Project Collaboration";
      if (previewMessage) previewMessage.textContent = message;

      // Configure direct email mailto fallback link
      if (previewDirectMail) {
        const mailSubject = encodeURIComponent(subject || `Inquiry from ${name} (Portfolio)`);
        const mailBody = encodeURIComponent(`${message}\n\n---\nSent by: ${name} (${email})`);
        previewDirectMail.href = `mailto:sahilnawaz257@gmail.com?subject=${mailSubject}&body=${mailBody}`;
      }

      previewBox.style.display = "block";
      previewBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    // Inform user of successful validation and pending backend status
    showAlert(
      `✔ <strong>Validation Successful!</strong> Your message details have been verified locally. Notice: The Flask backend is pending integration, so no live email has been dispatched yet.`,
      "success"
    );
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
