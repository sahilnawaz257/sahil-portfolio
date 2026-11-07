/**
 * Sahil Nawaz Portfolio — Vanilla JavaScript Interactivity
 * Complete Section-Wise SPA Navigation, WhatsApp Chat Widget & Google Meet Booking System
 */

document.addEventListener("DOMContentLoaded", () => {
  try {
    initSectionNavigation();
    initMobileMenu();
    initHeaderScroll();
    initBackToTop();
    initRoleTypingAnimation();
    initScrollReveal();
    initContactForm();
    initDynamicProjects();
    initProjectFilters();
    initCopyrightYear();
    initWhatsAppWidget();
    initGoogleMeetBooking();
  } catch (err) {
    console.error("Initialization error in portfolio scripts:", err);
  }
});

/**
 * =============================================================================
 * 01. SECTION-WISE SPA NAVIGATION SYSTEM
 * Displays ONLY the selected section while keeping inactive sections hidden.
 * Supports direct hash URLs (e.g. /#education), browser back/forward, and smooth transitions.
 * =============================================================================
 */
function initSectionNavigation() {
  const sections = document.querySelectorAll(".portfolio-section");
  const navLinks = document.querySelectorAll(".site-nav .nav-link, .footer-link");
  const validSectionIds = Array.from(sections).map((s) => s.id);

  if (!sections.length) return;

  function switchSection(targetId, updateHistory = true) {
    const cleanId = (targetId || "").replace(/^#/, "").trim();
    const activeId = validSectionIds.includes(cleanId) ? cleanId : "home";

    // 1. Hide all sections and show active one
    sections.forEach((sec) => {
      if (sec.id === activeId) {
        sec.classList.add("active-section");
        sec.style.display = "block";

        // Instantly activate any scroll-reveal elements within this section
        sec.querySelectorAll(".reveal-init").forEach((el) => {
          el.classList.add("reveal-active");
        });
      } else {
        sec.classList.remove("active-section");
        sec.style.display = "none";
      }
    });

    // 2. Update active states on navigation links
    document.querySelectorAll(".site-nav .nav-link").forEach((link) => {
      const href = link.getAttribute("href");
      if (href === `#${activeId}`) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
      } else if (href && href.startsWith("#")) {
        link.classList.remove("active");
        link.removeAttribute("aria-current");
      }
    });

    // 3. Update URL hash without jarring jump
    if (updateHistory) {
      if (history.pushState) {
        history.pushState(null, null, `#${activeId}`);
      } else {
        window.location.hash = `#${activeId}`;
      }
    }

    // 4. Smoothly scroll to top of viewport
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });

    // 5. Auto-close mobile menu if open
    const siteNav = document.getElementById("primary-navigation");
    const menuToggle = document.querySelector(".menu-toggle");
    const menuIcon = document.querySelector(".menu-icon");
    if (siteNav && siteNav.classList.contains("open")) {
      siteNav.classList.remove("open");
      if (menuToggle) menuToggle.setAttribute("aria-expanded", "false");
      if (menuIcon) menuIcon.textContent = "☰";
    }
  }

  // Intercept all internal navigation clicks targeting sections
  document.addEventListener("click", (e) => {
    const link = e.target.closest('a[href^="#"]');
    if (!link) return;

    const href = link.getAttribute("href");
    if (!href || href === "#") return;

    const targetSectionId = href.substring(1);
    if (validSectionIds.includes(targetSectionId)) {
      e.preventDefault();
      switchSection(targetSectionId, true);
    }
  });

  // Handle browser Back / Forward buttons (popstate & hashchange)
  window.addEventListener("popstate", () => {
    const currentHash = window.location.hash.replace(/^#/, "");
    switchSection(currentHash || "home", false);
  });

  window.addEventListener("hashchange", () => {
    const currentHash = window.location.hash.replace(/^#/, "");
    switchSection(currentHash || "home", false);
  });

  // Initial load: parse direct hash or default to 'home'
  const initialHash = window.location.hash.replace(/^#/, "");
  switchSection(initialHash || "home", false);
}

/**
 * =============================================================================
 * 02. MOBILE NAVIGATION MENU TOGGLE
 * =============================================================================
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

  menuToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    const isCurrentlyOpen = siteNav.classList.contains("open");
    setMenuState(!isCurrentlyOpen);
  });

  document.addEventListener("click", (e) => {
    if (siteNav.classList.contains("open") && !siteNav.contains(e.target) && !menuToggle.contains(e.target)) {
      setMenuState(false);
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && siteNav.classList.contains("open")) {
      setMenuState(false);
      menuToggle.focus();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 768 && siteNav.classList.contains("open")) {
      setMenuState(false);
    }
  });
}

/**
 * =============================================================================
 * 03. STICKY HEADER ELEVATION ON SCROLL
 * =============================================================================
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
 * =============================================================================
 * 04. BACK TO TOP BUTTON
 * =============================================================================
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
 * =============================================================================
 * 05. TYPING ANIMATION FOR HERO ROLE
 * =============================================================================
 */
function initRoleTypingAnimation() {
  const typedEl = document.getElementById("typed-role");
  if (!typedEl) return;

  const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) return;

  const roles = [
    "Forward Deployed Developer",
    "AI & ML Solutions Builder",
    "B.Tech CSE Undergrad · JBIET",
    "Full-Stack Web Engineer"
  ];

  let roleIdx = 0;
  let charIdx = roles[0].length;
  let isDeleting = true;
  const pauseDuration = 2200;

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

  setTimeout(typeTick, 2000);
}

/**
 * =============================================================================
 * 06. SCROLL REVEAL ANIMATIONS
 * =============================================================================
 */
function initScrollReveal() {
  if (!("IntersectionObserver" in window)) return;

  const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) return;

  const targets = document.querySelectorAll(
    ".edu-card-premium, .skill-category-card, .project-card, .contact-channel-card, .contact-form-box, .roadmap-item"
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
    { threshold: 0.1, rootMargin: "0px 0px -30px 0px" }
  );

  targets.forEach((target) => {
    target.classList.add("reveal-init");
    observer.observe(target);
  });
}

/**
 * =============================================================================
 * 07. WHATSAPP FLOATING INTERACTION WIDGET
 * Privacy Constraint: Does NOT display phone number as plain text on the page.
 * Opens popup with greeting and creates dynamically encoded wa.me link.
 * =============================================================================
 */
function initWhatsAppWidget() {
  const triggerBtn = document.getElementById("wa-trigger-btn");
  const popup = document.getElementById("whatsapp-popup");
  const closeBtn = document.getElementById("wa-close-btn");
  const customInput = document.getElementById("wa-custom-msg");
  const sendBtn = document.getElementById("wa-send-btn");
  const timeStamp = document.getElementById("wa-time-stamp");

  if (!triggerBtn || !popup) return;

  // Base WhatsApp URL with Sahil's verified phone number in href only
  const WA_BASE_URL = "https://wa.me/917323018308?text=";

  // Set real-time timestamp on greeting
  if (timeStamp) {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, "0");
    const minutes = now.getMinutes().toString().padStart(2, "0");
    timeStamp.textContent = `${hours}:${minutes}`;
  }

  function togglePopup(open) {
    if (open) {
      popup.classList.add("is-open");
      popup.setAttribute("aria-hidden", "false");
      triggerBtn.setAttribute("aria-expanded", "true");
      if (customInput) customInput.focus();
    } else {
      popup.classList.remove("is-open");
      popup.setAttribute("aria-hidden", "true");
      triggerBtn.setAttribute("aria-expanded", "false");
    }
  }

  triggerBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isOpen = popup.classList.contains("is-open");
    togglePopup(!isOpen);
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      togglePopup(false);
    });
  }

  // Update send URL as visitor customizes their message
  if (customInput && sendBtn) {
    customInput.addEventListener("input", () => {
      const val = customInput.value.trim() || "Hi Sahil! I came across your portfolio.";
      sendBtn.href = WA_BASE_URL + encodeURIComponent(val);
    });

    customInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        sendBtn.click();
      }
    });
  }

  // Close popup when clicking outside
  document.addEventListener("click", (e) => {
    if (popup.classList.contains("is-open") && !popup.contains(e.target) && !triggerBtn.contains(e.target)) {
      togglePopup(false);
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && popup.classList.contains("is-open")) {
      togglePopup(false);
      triggerBtn.focus();
    }
  });
}

/**
 * =============================================================================
 * 08. GOOGLE MEET BOOKING SYSTEM
 * Modal scheduling interface with client-side validation, past date prevention,
 * slot selection, and asynchronous booking dispatch to SQLite.
 * =============================================================================
 */
function initGoogleMeetBooking() {
  const modalBackdrop = document.getElementById("meet-modal-backdrop");
  const modalCloseBtn = document.getElementById("meet-modal-close-btn");
  const cancelBtn = document.getElementById("meet-cancel-btn");
  const form = document.getElementById("meet-booking-form");
  const dateInput = document.getElementById("meet-date");
  const statusBox = document.getElementById("meet-modal-status");
  const submitBtn = document.getElementById("meet-submit-btn");

  if (!modalBackdrop || !form) return;

  // Set minimum date to today (past dates are physically prevented)
  if (dateInput) {
    const todayStr = new Date().toISOString().split("T")[0];
    dateInput.min = todayStr;
    dateInput.value = todayStr;
  }

  function openModal() {
    modalBackdrop.classList.add("is-open");
    modalBackdrop.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    clearMeetStatus();
    const nameInput = document.getElementById("meet-name");
    if (nameInput) setTimeout(() => nameInput.focus(), 150);
  }

  function closeModal() {
    modalBackdrop.classList.remove("is-open");
    modalBackdrop.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    clearMeetStatus();
  }

  // Bind all triggers that open the Google Meet modal
  document.querySelectorAll(".open-meet-modal-trigger").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      openModal();
    });
  });

  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);
  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

  // Close on outside backdrop click
  modalBackdrop.addEventListener("click", (e) => {
    if (e.target === modalBackdrop) closeModal();
  });

  // Close on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modalBackdrop.classList.contains("is-open")) {
      closeModal();
    }
  });

  function showMeetStatus(msg, isSuccess = true) {
    if (!statusBox) return;
    statusBox.className = `meet-modal-status ${isSuccess ? "status-success" : "status-error"}`;
    statusBox.innerHTML = msg;
    statusBox.style.display = "block";
    statusBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function clearMeetStatus() {
    if (!statusBox) return;
    statusBox.style.display = "none";
    statusBox.innerHTML = "";
    statusBox.className = "meet-modal-status";
  }

  // Handle Form Submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearMeetStatus();

    const nameVal = (document.getElementById("meet-name")?.value || "").trim();
    const emailVal = (document.getElementById("meet-email")?.value || "").trim();
    const purposeVal = (document.getElementById("meet-purpose")?.value || "").trim();
    const dateVal = (document.getElementById("meet-date")?.value || "").trim();
    const timeVal = (document.getElementById("meet-slot")?.value || "").trim();
    const notesVal = (document.getElementById("meet-notes")?.value || "").trim();

    // Validation
    if (!nameVal || nameVal.length < 2) {
      showMeetStatus("Please provide your full name (minimum 2 characters).", false);
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailVal || !emailRegex.test(emailVal)) {
      showMeetStatus("Please enter a valid email address.", false);
      return;
    }

    if (!purposeVal) {
      showMeetStatus("Please select a meeting purpose/topic.", false);
      return;
    }

    if (!dateVal) {
      showMeetStatus("Please select a date for the meeting.", false);
      return;
    }

    const selectedDate = new Date(dateVal);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (selectedDate < today) {
      showMeetStatus("Meeting date cannot be in the past. Please choose today or a future date.", false);
      return;
    }

    if (!timeVal) {
      showMeetStatus("Please select a preferred 30-minute time slot.", false);
      return;
    }

    // Submit payload to Flask API
    const payload = {
      full_name: nameVal,
      email: emailVal,
      purpose: purposeVal,
      meeting_date: dateVal,
      meeting_time: timeVal,
      notes: notesVal
    };

    const originalBtnHtml = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Scheduling...</span> <span class="btn-spinner">⏳</span>`;

    const API_BASE = (window.location.origin.includes("5000") || (window.location.protocol === "http:" && window.location.port === "5000"))
      ? ""
      : "http://127.0.0.1:5000";

    try {
      const response = await fetch(`${API_BASE}/api/meetings/book`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.status === 201 && data.success) {
        showMeetStatus(
          `<strong>🎉 Request Submitted Successfully! (Booking #${data.booking_id})</strong><br>` +
          `Thank you, ${escapeHtml(nameVal)}! Your Google Meet request for <strong>${escapeHtml(dateVal)}</strong> at <strong>${escapeHtml(timeVal)}</strong> has been recorded in the database.<br>` +
          `Sahil has been notified at <em>sahilnawaz257@gmail.com</em> and will confirm your meeting with a Google Meet link shortly.`,
          true
        );
        form.reset();
        // Reset min date
        if (dateInput) {
          const todayStr = new Date().toISOString().split("T")[0];
          dateInput.min = todayStr;
          dateInput.value = todayStr;
        }
      } else if (response.status === 409) {
        showMeetStatus(
          `<strong>⚠️ Slot Already Requested:</strong><br>${escapeHtml(data.error || "You already have an active request for this date and time.")}`,
          false
        );
      } else {
        showMeetStatus(
          `<strong>Submission Failed:</strong> ${escapeHtml(data.error || "Please verify your information and try again.")}`,
          false
        );
      }
    } catch (err) {
      showMeetStatus(
        `<strong>Network Error:</strong> Unable to connect to the scheduling service (${escapeHtml(err.message)}). Please email Sahil directly at <em>sahilnawaz257@gmail.com</em>.`,
        false
      );
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnHtml;
    }
  });
}

/**
 * =============================================================================
 * 09. CONTACT FORM — FRONTEND VALIDATION & FLASK DATABASE SUBMISSION
 * =============================================================================
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

  const previewBox = document.getElementById("form-preview-box");
  const previewSender = document.getElementById("preview-sender");
  const previewEmail = document.getElementById("preview-email");
  const previewSubject = document.getElementById("preview-subject");
  const previewMessage = document.getElementById("preview-message");
  const previewMailto = document.getElementById("preview-direct-mail");
  const previewResetBtn = document.getElementById("preview-reset-btn");
  const charCount = document.getElementById("message-char-count");

  if (!contactForm) return;

  if (messageInput && charCount) {
    messageInput.addEventListener("input", () => {
      const len = messageInput.value.length;
      charCount.textContent = `${len} / 1000`;
      if (len > 1000) {
        charCount.style.color = "#dc3545";
      } else {
        charCount.style.color = "";
      }
    });
  }

  function validateField(type) {
    let isValid = true;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (type === "name" || type === "all") {
      const val = (nameInput?.value || "").trim();
      if (!val) {
        setFieldError(nameInput, nameError, "Full Name is required.");
        isValid = false;
      } else if (val.length < 2) {
        setFieldError(nameInput, nameError, "Full Name must be at least 2 characters.");
        isValid = false;
      } else {
        clearSingleFieldError(nameInput, nameError);
      }
    }

    if (type === "email" || type === "all") {
      const val = (emailInput?.value || "").trim();
      if (!val) {
        setFieldError(emailInput, emailError, "Email address is required.");
        isValid = false;
      } else if (!emailRegex.test(val)) {
        setFieldError(emailInput, emailError, "Please enter a valid email address (e.g., sahil@example.com).");
        isValid = false;
      } else {
        clearSingleFieldError(emailInput, emailError);
      }
    }

    if (type === "subject" || type === "all") {
      const val = (subjectInput?.value || "").trim();
      if (val && val.length > 150) {
        setFieldError(subjectInput, subjectError, "Subject must not exceed 150 characters.");
        isValid = false;
      } else {
        clearSingleFieldError(subjectInput, subjectError);
      }
    }

    if (type === "message" || type === "all") {
      const val = (messageInput?.value || "").trim();
      if (!val) {
        setFieldError(messageInput, messageError, "Message is required.");
        isValid = false;
      } else if (val.length < 10) {
        setFieldError(messageInput, messageError, "Message must be at least 10 characters long.");
        isValid = false;
      } else if (val.length > 1000) {
        setFieldError(messageInput, messageError, "Message cannot exceed 1000 characters.");
        isValid = false;
      } else {
        clearSingleFieldError(messageInput, messageError);
      }
    }

    return isValid;
  }

  if (nameInput) nameInput.addEventListener("blur", () => validateField("name"));
  if (emailInput) emailInput.addEventListener("blur", () => validateField("email"));
  if (subjectInput) subjectInput.addEventListener("blur", () => validateField("subject"));
  if (messageInput) messageInput.addEventListener("blur", () => validateField("message"));

  contactForm.addEventListener("submit", (e) => {
    e.preventDefault();
    clearFieldErrors();
    showAlert("", "");

    const isFormValid = validateField("all");
    if (!isFormValid) {
      showAlert("⚠️ Please correct the highlighted errors above.", "alert-danger");
      return;
    }

    const payload = {
      name: nameInput.value.trim(),
      email: emailInput.value.trim(),
      subject: (subjectInput?.value || "").trim() || "Forward Deployed Opportunity / Project Collaboration",
      message: messageInput.value.trim()
    };

    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Saving to Database...</span> <span class="btn-spinner" aria-hidden="true">⏳</span>`;

    const API_BASE = (window.location.origin.includes("5000") || (window.location.protocol === "http:" && window.location.port === "5000"))
      ? ""
      : "http://127.0.0.1:5000";

    fetch(`${API_BASE}/api/contact`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    })
      .then((res) => {
        return res.json().then((data) => ({ status: res.status, ok: res.ok, data }));
      })
      .then(({ ok, data }) => {
        if (!ok || !data.success) {
          throw new Error(data.error || "Submission rejected by server.");
        }

        showAlert(`✓ <strong>Success:</strong> ${escapeHtml(data.message)}`, "alert-success");

        if (previewBox) {
          if (previewSender) previewSender.textContent = payload.name;
          if (previewEmail) previewEmail.textContent = payload.email;
          if (previewSubject) previewSubject.textContent = payload.subject;
          if (previewMessage) previewMessage.textContent = payload.message;

          if (previewMailto) {
            const mailtoUrl = `mailto:sahilnawaz257@gmail.com?subject=${encodeURIComponent(payload.subject)}&body=${encodeURIComponent("From: " + payload.name + " (" + payload.email + ")\n\n" + payload.message)}`;
            previewMailto.setAttribute("href", mailtoUrl);
          }

          previewBox.style.display = "block";
          previewBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }

        contactForm.reset();
        if (charCount) charCount.textContent = "0 / 1000";
      })
      .catch((err) => {
        showAlert(`⚠️ <strong>Submission Note:</strong> ${escapeHtml(err.message)}`, "alert-danger");
      })
      .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      });
  });

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

  function clearSingleFieldError(inputEl, errorEl) {
    if (inputEl) {
      inputEl.classList.remove("is-invalid");
      inputEl.removeAttribute("aria-invalid");
    }
    if (errorEl) {
      errorEl.textContent = "";
      errorEl.classList.remove("visible");
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
 * =============================================================================
 * 10. DYNAMIC COPYRIGHT YEAR
 * =============================================================================
 */
function initCopyrightYear() {
  const yearElement = document.getElementById("current-year");
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }
}

/**
 * =============================================================================
 * 11. FILTER PROJECTS BY CATEGORY
 * =============================================================================
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
 * =============================================================================
 * 12. DYNAMIC PROJECTS LOADER FROM SQLITE DATABASE
 * =============================================================================
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
      return;
    }

    const data = await res.json();
    if (data && data.success && Array.isArray(data.projects) && data.projects.length > 0) {
      renderProjectCards(grid, data.projects);
    }
  } catch (err) {
    console.info("Using static projects showcase:", err.message);
  }
}

function renderProjectCards(container, projects) {
  const cardsHtml = projects.map((p, idx) => {
    const num = String(idx + 1).padStart(2, "0");
    const titleLower = (p.title || "").toLowerCase();

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

    const techItems = (p.technologies || "")
      .split(/[,|;]/)
      .map((t) => t.trim())
      .filter(Boolean);
    const techListHtml = techItems.length > 0
      ? techItems.map((t) => `<li>${escapeHtml(t)}</li>`).join("")
      : `<li>Software</li>`;

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

function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
