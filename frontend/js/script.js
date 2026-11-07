/**
 * Sahil Nawaz Portfolio — Frontend Script
 * Step 02: Premium Responsive Navbar & Interactivity
 */

document.addEventListener("DOMContentLoaded", () => {
  initMobileMenu();
  initActiveNavLink();
  initHeaderScroll();
  initCopyrightYear();
  initContactForm();
  initProjectFilters();
});

/**
 * Mobile Navigation Menu Toggle with Accessibility
 */
function initMobileMenu() {
  const menuToggle = document.querySelector(".menu-toggle");
  const siteNav = document.getElementById("primary-navigation") || document.querySelector(".site-nav");
  const menuIcon = document.querySelector(".menu-icon");

  if (!menuToggle || !siteNav) return;

  function toggleMenu(forceClose = false) {
    const isCurrentlyOpen = siteNav.classList.contains("open");
    const nextState = forceClose ? false : !isCurrentlyOpen;

    if (nextState) {
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
    toggleMenu();
  });

  // Close menu when clicking outside
  document.addEventListener("click", (e) => {
    if (siteNav.classList.contains("open") && !siteNav.contains(e.target) && !menuToggle.contains(e.target)) {
      toggleMenu(true);
    }
  });

  // Close menu on Escape key press
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && siteNav.classList.contains("open")) {
      toggleMenu(true);
      menuToggle.focus();
    }
  });

  // Close menu when any nav link is tapped
  siteNav.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", () => {
      toggleMenu(true);
    });
  });
}

/**
 * Sticky Header Scroll Effect
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
 * ScrollSpy & Active Navigation Link Tracking
 */
function initActiveNavLink() {
  const navLinks = document.querySelectorAll(".site-nav .nav-link");
  const sections = document.querySelectorAll("section[id]");

  if (!sections.length || !navLinks.length) return;

  const updateActiveLink = () => {
    let currentSectionId = "";
    const scrollPosition = window.scrollY + 120; // Offset for header height

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
        } else if (href.startsWith("#")) {
          link.classList.remove("active");
        }
      });
    }
  };

  window.addEventListener("scroll", updateActiveLink, { passive: true });
  updateActiveLink();
}

/**
 * Set dynamic copyright year in footer
 */
function initCopyrightYear() {
  const yearElement = document.getElementById("current-year");
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }
}

/**
 * Contact Form Submission with API integration & Fallback
 */
function initContactForm() {
  const contactForm = document.getElementById("contact-form");
  const formAlert = document.getElementById("form-alert");
  const submitBtn = document.getElementById("submit-btn");

  if (!contactForm) return;

  contactForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Clear previous alert
    showAlert("", "");

    const name = document.getElementById("contact-name").value.trim();
    const email = document.getElementById("contact-email").value.trim();
    const subject = document.getElementById("contact-subject") ? document.getElementById("contact-subject").value.trim() : "";
    const message = document.getElementById("contact-message").value.trim();

    if (!name || !email || !message) {
      showAlert("Please fill in all required fields (Name, Email, Message).", "error");
      return;
    }

    // Set loading state
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Sending...</span>`;

    const payload = { name, email, subject, message };

    // Determine target API endpoint
    // If served via Flask, use relative path "/api/contact"
    // If opened via file:// or another port (Live Server 5500), point to 127.0.0.1:5000
    const apiUrl = window.location.origin.includes("5000") 
      ? "/api/contact" 
      : "http://127.0.0.1:5000/api/contact";

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        showAlert(`✨ ${data.message || "Message sent successfully! Sahil will be in touch soon."}`, "success");
        contactForm.reset();
      } else {
        throw new Error(data.error || "Failed to submit message.");
      }
    } catch (err) {
      console.warn("API request failed:", err);
      // Helpful fallback message with direct mailto
      const mailtoLink = `mailto:sahilnawaz257@gmail.com?subject=${encodeURIComponent(subject || "Portfolio Inquiry from " + name)}&body=${encodeURIComponent(message + "\n\nFrom: " + name + " (" + email + ")")}`;
      
      showAlert(
        `Backend server is offline or unreachable. <a href="${mailtoLink}" style="color: inherit; text-decoration: underline; font-weight: bold;">Click here to send directly via Email client</a> instead.`,
        "error"
      );
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
    }
  });

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
    formAlert.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

/**
 * Filter projects by category on the Projects page
 */
function initProjectFilters() {
  const filterButtons = document.querySelectorAll(".filter-btn");
  const projectCards = document.querySelectorAll(".project-card");

  if (!filterButtons.length || !projectCards.length) return;

  filterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      // Update active button state
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

