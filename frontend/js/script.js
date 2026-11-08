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
    document.querySelectorAll(".site-nav .nav-link, .footer-nav-list .footer-link").forEach((link) => {
      const targetAttr = link.getAttribute("data-target");
      const href = link.getAttribute("href") || "";
      const matchesTarget = targetAttr === activeId || href === `#${activeId}`;

      if (matchesTarget && link.classList.contains("nav-link")) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
      } else if (link.classList.contains("nav-link")) {
        link.classList.remove("active");
        link.removeAttribute("aria-current");
      }
    });

    // 3. Update URL hash cleanly
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
    const trigger = e.target.closest('a[href^="#"], [data-target]');
    if (!trigger) return;

    // Check if it's an action button inside form or modal
    if (trigger.closest("#meet-modal-backdrop") || trigger.closest("#whatsapp-widget") || trigger.type === "submit") {
      return;
    }

    let targetSectionId = trigger.getAttribute("data-target");
    if (!targetSectionId) {
      const href = trigger.getAttribute("href");
      if (href && href.startsWith("#") && href.length > 1) {
        targetSectionId = href.substring(1);
      }
    }

    if (targetSectionId && validSectionIds.includes(targetSectionId)) {
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
    "Founder · Gymsewa",
    "AI & ML Solutions Builder",
    "B.Tech CSE · JB Group of Institutions",
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
    ".edu-card-premium, .skill-group-card, .detailed-skill-card, .project-card-large, .contact-channel-card, .contact-form-box, .overview-card, .about-preview-card, .contact-cta-banner"
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
 * Dynamically resolves the API base URL:
 * - When served by Flask on Render, custom domains, or local port 5000, returns "" (same-origin relative paths).
 * - Only when running on file:// or from a separate local dev server (port 5500, 3000), routes to http://127.0.0.1:5000.
 */
function getApiBaseUrl() {
  if (typeof window === "undefined" || !window.location) {
    return "";
  }
  if (window.location.protocol === "file:") {
    return "http://127.0.0.1:5000";
  }
  const hostname = window.location.hostname;
  const isLocalHost = hostname === "localhost" || hostname === "127.0.0.1";
  if (isLocalHost && window.location.port && window.location.port !== "5000") {
    return "http://127.0.0.1:5000";
  }
  return "";
}

/**
 * =============================================================================
 * 08. GOOGLE MEET BOOKING SYSTEM & GOOGLE FORM INTEGRATION
 * Modal scheduling interface with client-side validation, past date prevention,
 * slot selection, 1-click Google Calendar integration, and WhatsApp receipt.
 * =============================================================================
 */
const GOOGLE_FORM_URL = "https://docs.google.com/forms";

/**
 * Constructs an instant 1-Click "Add to Google Calendar" URL
 * Formats start/end dates in IST (Asia/Kolkata) with complete meeting summary.
 */
function generateGoogleCalendarUrl({ title, date, timeSlot, details, location }) {
  const cleanDate = (date || "").replace(/-/g, "");
  let startHour = 10, startMin = 0, endHour = 10, endMin = 30;

  if (timeSlot) {
    const parts = timeSlot.split("-");
    const parseTime = (tStr) => {
      const match = (tStr || "").trim().match(/(\d+):(\d+)\s*(AM|PM)/i);
      if (match) {
        let h = parseInt(match[1], 10);
        const m = parseInt(match[2], 10);
        const period = match[3].toUpperCase();
        if (period === "PM" && h < 12) h += 12;
        if (period === "AM" && h === 12) h = 0;
        return { h, m };
      }
      return null;
    };
    if (parts[0]) {
      const st = parseTime(parts[0]);
      if (st) { startHour = st.h; startMin = st.m; }
    }
    if (parts[1]) {
      const et = parseTime(parts[1]);
      if (et) { endHour = et.h; endMin = et.m; }
    } else {
      endHour = startHour;
      endMin = startMin + 30;
      if (endMin >= 60) { endHour += 1; endMin -= 60; }
    }
  }

  const pad = (n) => String(n).padStart(2, "0");
  const startStr = `${cleanDate}T${pad(startHour)}${pad(startMin)}00`;
  const endStr = `${cleanDate}T${pad(endHour)}${pad(endMin)}00`;

  const params = new URLSearchParams({
    action: "TEMPLATE",
    text: title || "Google Meet Consultation with Sahil Nawaz",
    dates: `${startStr}/${endStr}`,
    ctz: "Asia/Kolkata",
    details: details || "Google Meet consultation with Sahil Nawaz (Forward Deployed Developer).",
    location: location || "Google Meet"
  });

  return `https://calendar.google.com/calendar/render?${params.toString()}`;
}

function initGoogleMeetBooking() {
  const modalBackdrop = document.getElementById("meet-modal-backdrop");
  const modalCloseBtn = document.getElementById("meet-modal-close-btn");
  const cancelBtn = document.getElementById("meet-cancel-btn");
  const form = document.getElementById("meet-booking-form");
  const dateInput = document.getElementById("meet-date");
  const slotSelect = document.getElementById("meet-slot");
  const statusBox = document.getElementById("meet-modal-status");
  const submitBtn = document.getElementById("meet-submit-btn");
  const modalActions = form ? form.querySelector(".meet-modal-actions") : null;
  const originalActionsHtml = modalActions ? modalActions.innerHTML : "";

  // Bind Google Form links dynamically
  const topGFormLink = document.getElementById("meet-gform-top-link");
  const contactGFormCard = document.getElementById("contact-google-form-card");
  if (topGFormLink) topGFormLink.href = GOOGLE_FORM_URL;
  if (contactGFormCard) contactGFormCard.href = GOOGLE_FORM_URL;

  if (!modalBackdrop || !form) return;

  const API_BASE = getApiBaseUrl();

  function restoreOriginalActions() {
    if (modalActions && originalActionsHtml) {
      modalActions.innerHTML = originalActionsHtml;
      const newCancel = document.getElementById("meet-cancel-btn");
      if (newCancel) newCancel.addEventListener("click", closeModal);
    }
  }

  function resetFormToDefault() {
    form.reset();
    const formFields = form.querySelectorAll(".meet-form-grid, .meet-field-group");
    formFields.forEach((el) => { el.style.display = ""; });
    clearMeetStatus();
    restoreOriginalActions();
    if (dateInput) {
      const todayStr = new Date().toISOString().split("T")[0];
      dateInput.min = todayStr;
      dateInput.value = todayStr;
      fetchAvailableSlots(todayStr);
    }
  }

  // Set minimum date to today (past dates are physically prevented)
  if (dateInput) {
    const todayStr = new Date().toISOString().split("T")[0];
    dateInput.min = todayStr;
    dateInput.value = todayStr;
  }

  async function fetchAvailableSlots(dateVal) {
    if (!slotSelect || !dateVal) return;
    try {
      const res = await fetch(`${API_BASE}/api/meetings/available-slots?date=${encodeURIComponent(dateVal)}`);
      const data = await res.json();
      if (data.success && Array.isArray(data.slots)) {
        slotSelect.innerHTML = `<option value="" disabled selected>Choose a 30-min window...</option>`;
        let hasAvailable = false;
        data.slots.forEach((s) => {
          const opt = document.createElement("option");
          opt.value = s.slot;
          if (s.available) {
            opt.textContent = `${s.slot} (Available)`;
            hasAvailable = true;
          } else {
            opt.textContent = `${s.slot} — Booked`;
            opt.disabled = true;
          }
          slotSelect.appendChild(opt);
        });

        if (!hasAvailable) {
          showMeetStatus("All slots on this date are currently booked. Please choose another date.", false);
        }
      }
    } catch (e) {
      console.warn("Could not fetch slot availability:", e);
    }
  }

  if (dateInput) {
    dateInput.addEventListener("change", () => {
      fetchAvailableSlots(dateInput.value);
    });
  }

  function openModal() {
    modalBackdrop.classList.add("is-open");
    modalBackdrop.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    clearMeetStatus();
    if (dateInput && dateInput.value) {
      fetchAvailableSlots(dateInput.value);
    }
    const nameInput = document.getElementById("meet-name");
    if (nameInput) setTimeout(() => nameInput.focus(), 150);
  }

  function closeModal() {
    modalBackdrop.classList.remove("is-open");
    modalBackdrop.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if (statusBox && statusBox.classList.contains("status-success-card")) {
      resetFormToDefault();
    } else {
      clearMeetStatus();
    }
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

  let isBooking = false;

  // Handle Form Submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (isBooking) return;
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

    isBooking = true;
    const payload = {
      full_name: nameVal,
      email: emailVal,
      purpose: purposeVal,
      preferred_date: dateVal,
      meeting_date: dateVal,
      preferred_time: timeVal,
      meeting_time: timeVal,
      notes: notesVal
    };

    const originalBtnHtml = submitBtn ? submitBtn.innerHTML : "";
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span>Recording Request...</span> <span class="btn-spinner">⏳</span>`;
    }

    try {
      const response = await fetch(`${API_BASE}/api/meetings/book`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(payload)
      });

      let data = {};
      try {
        data = await response.json();
      } catch (_) {
        data = { success: false, error: "Server returned status " + response.status };
      }

      if (response.status === 201 && data.success) {
        const isVisitorConfirmed = Boolean(
          data.email_notification &&
          (data.email_notification.visitor_confirmed ||
           (data.email_notification.visitor_details && data.email_notification.visitor_details.success))
        );

        const emailNotice = isVisitorConfirmed
          ? `<div class="meet-ticket-email delivered">✉️ <strong>Confirmation Sent:</strong> An automated confirmation receipt has been dispatched to <b>${escapeHtml(emailVal)}</b>.</div>`
          : `<div class="meet-ticket-email pending">💾 <strong>Recorded in Database:</strong> Sahil has received your request and will review and send your official Google Meet link to <b>${escapeHtml(emailVal)}</b> shortly.</div>`;

        const bookingRef = String(data.booking_id || "NEW").slice(0, 8);
        const gCalUrl = generateGoogleCalendarUrl({
          title: `Google Meet: Sahil Nawaz & ${nameVal}`,
          date: dateVal,
          timeSlot: timeVal,
          details: `Booking Reference: #${bookingRef}\nVisitor: ${nameVal} (${emailVal})\nTopic: ${purposeVal}\nNotes: ${notesVal || "None"}\nGoogle Meet link will be provided by Sahil Nawaz (Forward Deployed Developer).`,
          location: "Google Meet"
        });

        const waText = `Hi Sahil! I have scheduled a Google Meet consultation for ${dateVal} at ${timeVal} (Booking Ref: #${bookingRef}).\nName: ${nameVal}\nTopic: ${purposeVal}\nPlease confirm!`;
        const waUrl = `https://wa.me/917323018308?text=${encodeURIComponent(waText)}`;

        statusBox.className = "meet-modal-status status-success-card";
        statusBox.innerHTML = `
          <div class="meet-receipt-card">
            <div class="meet-receipt-header">
              <span class="meet-receipt-check" aria-hidden="true">✓</span>
              <div>
                <h4 class="meet-receipt-title">Consultation Request Confirmed!</h4>
                <span class="meet-receipt-badge">Booking Ref: #${escapeHtml(bookingRef)}</span>
              </div>
            </div>
            <div class="meet-receipt-grid">
              <div class="receipt-item"><span class="r-label">Name:</span> <span class="r-val">${escapeHtml(nameVal)}</span></div>
              <div class="receipt-item"><span class="r-label">Email:</span> <span class="r-val">${escapeHtml(emailVal)}</span></div>
              <div class="receipt-item"><span class="r-label">Topic:</span> <span class="r-val">${escapeHtml(purposeVal)}</span></div>
              <div class="receipt-item"><span class="r-label">Date:</span> <span class="r-val">📅 ${escapeHtml(dateVal)}</span></div>
              <div class="receipt-item"><span class="r-label">Time (IST):</span> <span class="r-val">⏰ ${escapeHtml(timeVal)}</span></div>
            </div>
            ${emailNotice}
            <div class="meet-instant-buttons">
              <a href="${gCalUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm btn-gcal">
                <span>📅 Add to Google Calendar</span>
              </a>
              <a href="${waUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm btn-wa-receipt">
                <span>💬 Confirm on WhatsApp</span>
              </a>
            </div>
          </div>
        `;
        statusBox.style.display = "block";
        statusBox.scrollIntoView({ behavior: "smooth", block: "nearest" });

        // Hide form fields so visitor sees only the clear confirmation ticket
        const formFields = form.querySelectorAll(".meet-form-grid, .meet-field-group");
        formFields.forEach((el) => { el.style.display = "none"; });

        if (modalActions) {
          modalActions.innerHTML = `
            <button type="button" class="btn btn-outline" id="meet-book-another-btn">Schedule Another Slot</button>
            <button type="button" class="btn btn-primary" id="meet-done-btn">Done</button>
          `;
          document.getElementById("meet-done-btn")?.addEventListener("click", closeModal);
          document.getElementById("meet-book-another-btn")?.addEventListener("click", resetFormToDefault);
        }
      } else if (response.status === 409) {
        showMeetStatus(
          `<strong>⚠️ Scheduling Conflict:</strong><br>${escapeHtml(data.error || "This time slot has already been requested.")}`,
          false
        );
        if (dateVal) fetchAvailableSlots(dateVal);
      } else {
        showMeetStatus(
          `<strong>Submission Notice:</strong> ${escapeHtml(data.error || "Please verify your information and try again.")}`,
          false
        );
      }
    } catch (err) {
      const fallbackWaText = `Hi Sahil! I would like to schedule a Google Meet consultation for ${dateVal} at ${timeVal}.\nName: ${nameVal}\nTopic: ${purposeVal}\nNotes: ${notesVal || "None"}`;
      const fallbackWaUrl = `https://wa.me/917323018308?text=${encodeURIComponent(fallbackWaText)}`;
      showMeetStatus(
        `<strong>Network Notice:</strong> Unable to reach scheduling service (${escapeHtml(err.message)}).<br>
        <span style="display:block;margin-top:6px;font-size:0.9em;">You can instantly lock in this slot directly with Sahil on WhatsApp:</span>
        <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;">
          <a href="${fallbackWaUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="text-decoration:none;display:inline-flex;align-items:center;gap:6px;">
            <span>💬 Confirm via WhatsApp Now</span>
          </a>
          <a href="mailto:sahilnawaaz257@gmail.com?subject=Google%20Meet%20Consultation%20Request&body=${encodeURIComponent(fallbackWaText)}" class="btn btn-outline btn-sm" style="text-decoration:none;display:inline-flex;align-items:center;gap:6px;">
            <span>✉️ Email Sahil</span>
          </a>
        </div>`,
        false
      );
    } finally {
      setTimeout(() => {
        isBooking = false;
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnHtml;
        }
      }, 1200);
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

  let isSubmitting = false;

  contactForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    clearFieldErrors();
    showAlert("", "");

    const isFormValid = validateField("all");
    if (!isFormValid) {
      showAlert("⚠️ Please correct the highlighted errors above.", "alert-danger");
      return;
    }

    const payload = {
      full_name: nameInput.value.trim(),
      name: nameInput.value.trim(),
      email: emailInput.value.trim(),
      subject: (subjectInput?.value || "").trim() || "Forward Deployed Opportunity / Project Collaboration",
      message: messageInput.value.trim()
    };

    isSubmitting = true;
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Saving to Database...</span> <span class="btn-spinner" aria-hidden="true">⏳</span>`;

    const API_BASE = getApiBaseUrl();

    fetch(`${API_BASE}/api/contact`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    })
      .then(async (res) => {
        let data = {};
        try {
          data = await res.json();
        } catch (_) {
          data = { success: false, error: "Server returned status " + res.status };
        }
        return { status: res.status, ok: res.ok, data };
      })
      .then(({ ok, data }) => {
        if (!ok || !data.success) {
          throw new Error(data.error || "Submission rejected by server.");
        }

        showAlert(`✓ <strong>Success:</strong> ${escapeHtml(data.message)}`, "alert-success");

        if (previewBox) {
          if (previewSender) previewSender.textContent = payload.full_name;
          if (previewEmail) previewEmail.textContent = payload.email;
          if (previewSubject) previewSubject.textContent = payload.subject;
          if (previewMessage) previewMessage.textContent = payload.message;

          const previewIdBadge = document.getElementById("preview-id-badge");
          if (previewIdBadge && data.contact_id) {
            previewIdBadge.textContent = `Ref: #${String(data.contact_id).slice(0, 8)}`;
          }

          const previewWaBtn = document.getElementById("preview-whatsapp-btn");
          if (previewWaBtn) {
            const waMsg = `Hi Sahil! I just submitted an inquiry on your portfolio (Ref: #${String(data.contact_id || "").slice(0, 8)}).\nFrom: ${payload.full_name} (${payload.email})\nSubject: ${payload.subject}\nMessage: ${payload.message}`;
            previewWaBtn.setAttribute("href", `https://wa.me/917323018308?text=${encodeURIComponent(waMsg)}`);
          }

          const previewDbStatus = document.getElementById("preview-db-status");
          if (previewDbStatus) {
            const isVisitorConfirmed = Boolean(data.email_notification && data.email_notification.visitor_confirmed);
            if (isVisitorConfirmed) {
              previewDbStatus.textContent = `Your inquiry has been recorded and an automated confirmation copy was dispatched to ${payload.email}.`;
            } else {
              previewDbStatus.textContent = `Your message is securely recorded in the database. Sahil will review your inquiry and reply to ${payload.email}.`;
            }
          }

          previewBox.style.display = "block";
          previewBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }

        contactForm.reset();
        if (charCount) charCount.textContent = "0 / 1000";
      })
      .catch((err) => {
        showAlert(`⚠️ <strong>Submission Notice:</strong> ${escapeHtml(err.message)}`, "alert-danger");
      })
      .finally(() => {
        setTimeout(() => {
          isSubmitting = false;
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnText;
        }, 1200);
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
    const isSuccess = (type || "").includes("success");
    formAlert.className = isSuccess ? "form-alert success alert-success" : "form-alert error alert-danger";
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
  const projectCards = document.querySelectorAll("#project-grid .project-card-large, #project-grid .project-card");

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

  const API_BASE_URL = getApiBaseUrl();
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
      initProjectFilters(); // Rebind filters for dynamically loaded elements
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
    let category = "ai";

    if (titleLower.includes("crowd") || titleLower.includes("density")) {
      category = "ai";
      bannerHtml = `
        <div class="project-banner banner-crowd" aria-hidden="true">
          <div class="banner-visual-stats">
            <span class="stat-highlight">1,248</span>
            <small>Crowd Analytics Preview</small>
          </div>
          <div class="crowd-visual-bars">
            <span style="height: 25px;"></span>
            <span style="height: 48px;"></span>
            <span style="height: 32px;"></span>
            <span style="height: 60px;"></span>
            <span style="height: 42px;"></span>
            <span style="height: 52px;"></span>
            <span style="height: 30px;"></span>
          </div>
        </div>
      `;
    } else if (titleLower.includes("library")) {
      category = "system";
      bannerHtml = `
        <div class="project-banner banner-library" aria-hidden="true">
          <div class="library-mockup-graphic">
            <span class="mockup-label">RELATIONAL DATABASE SYSTEM</span>
            <b>Books · Student Records · Transactions</b>
          </div>
        </div>
      `;
    } else if (titleLower.includes("brand") || titleLower.includes("guideline") || titleLower.includes("audit")) {
      category = "tool";
      bannerHtml = `
        <div class="project-banner banner-brand" aria-hidden="true">
          <div class="brand-audit-graphic">
            <span class="audit-typography">Aa</span>
            <div class="audit-swatches">
              <span style="background: #df7568;"></span>
              <span style="background: #f3b5aa;"></span>
              <span style="background: #e8d6c9;"></span>
              <span style="background: #39312e;"></span>
            </div>
          </div>
        </div>
      `;
    } else {
      category = "ai";
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
      ? techItems.map((t) => `<span class="tech-tag">${escapeHtml(t)}</span>`).join("")
      : `<span class="tech-tag">Software</span>`;

    let linksHtml = "";
    if (p.github_url && p.github_url.trim()) {
      linksHtml += `
        <a href="${escapeHtml(p.github_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" aria-label="View ${escapeHtml(p.title)} on GitHub">
          <span>🐙 GitHub Repository ↗</span>
        </a>
      `;
    }
    if (p.live_demo_url && p.live_demo_url.trim()) {
      linksHtml += `
        <a href="${escapeHtml(p.live_demo_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm" aria-label="Live Demo for ${escapeHtml(p.title)}">
          <span>🌐 Live Demo ↗</span>
        </a>
      `;
    }
    if (!linksHtml) {
      linksHtml = `<span style="font-size: 0.8rem; color: var(--text-muted); font-style: italic; padding: 6px 0;">Academic Repository / Core Project</span>`;
    }

    const tag = `${num} / ${escapeHtml(p.title.split(' ')[0])}`;

    return `
      <article class="project-card-large" data-category="${category}">
        ${bannerHtml}
        <div class="project-card-body">
          <div class="project-meta-row">
            <span class="project-badge">${tag}</span>
            <span class="project-status-dot">Production System</span>
          </div>
          <h3 class="project-title">${escapeHtml(p.title)}</h3>
          <p class="project-description">${escapeHtml(p.description)}</p>
          <div class="project-tech-group">
            ${techListHtml}
          </div>
          <div class="project-action-row">
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
