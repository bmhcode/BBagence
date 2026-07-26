/* ============================================================
   YES MALL — Main JavaScript
   ============================================================ */




document.addEventListener('DOMContentLoaded', () => {

  /* ── 1. Navbar scroll effect ── */
  const navbar = document.getElementById('ym-navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 40);
    });
  }

  /* ── 2. Hero BG Ken-Burns ── */
  const heroBg = document.querySelector('.ym-hero__bg');
  if (heroBg) {
    setTimeout(() => heroBg.classList.add('loaded'), 100);
  }

  /* ── 3. Search Overlay ── */
  const searchBtns  = document.querySelectorAll('.ym-navbar__search-btn, [data-search-open]');
  const overlay     = document.getElementById('ym-search-overlay');
  const overlayClose = document.getElementById('ym-search-close');
  const searchInput = document.getElementById('ym-search-input');

  function openSearch() {
    overlay?.classList.add('active');
    setTimeout(() => searchInput?.focus(), 200);
    document.body.style.overflow = 'hidden';
  }
  function closeSearch() {
    overlay?.classList.remove('active');
    document.body.style.overflow = '';
  }

  searchBtns.forEach(btn => btn.addEventListener('click', openSearch));
  overlayClose?.addEventListener('click', closeSearch);
  overlay?.addEventListener('click', e => { if (e.target === overlay) closeSearch(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSearch(); });

  /* ── 4. Mobile Nav ── */
  const hamburger       = document.getElementById('ym-hamburger');
  const mobileNav       = document.getElementById('ym-mobile-nav');
  const mobileClose     = document.getElementById('ym-mobile-close');
  const mobileBackdrop  = document.getElementById('ym-mobile-backdrop');

  function openMobileNav() {
    mobileNav?.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeMobileNav() {
    mobileNav?.classList.remove('open');
    document.body.style.overflow = '';
  }

  hamburger?.addEventListener('click', openMobileNav);
  mobileClose?.addEventListener('click', closeMobileNav);
  mobileBackdrop?.addEventListener('click', closeMobileNav);

  /* ── 5. Scroll Reveal ── */
  const reveals = document.querySelectorAll('.ym-reveal');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, (entry.target.dataset.delay || 0) * 1);
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  reveals.forEach(el => revealObserver.observe(el));

  /* ── 6. Staggered grid items ── */
  document.querySelectorAll('.ym-stores-grid, .ym-blog-grid, .ym-promos-grid').forEach(grid => {
    grid.querySelectorAll(':scope > *').forEach((child, i) => {
      child.style.transitionDelay = `${i * 80}ms`;
    });
  });

  /* ── 7. Stats counter ── */
  const statNumbers = document.querySelectorAll('.ym-hero__stat-number[data-count]');
  const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el    = entry.target;
        const end   = parseInt(el.dataset.count);
        const dur   = 1500;
        const step  = Math.ceil(end / (dur / 16));
        let current = 0;
        const timer = setInterval(() => {
          current = Math.min(current + step, end);
          el.textContent = current + (el.dataset.suffix || '');
          if (current >= end) clearInterval(timer);
        }, 16);
        statsObserver.unobserve(el);
      }
    });
  }, { threshold: 0.5 });
  statNumbers.forEach(el => statsObserver.observe(el));

  /* ── 8. Category filter ── */
  const filterBtns = document.querySelectorAll('.ym-filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  /* ── 9. Wishlist heart toggle ── */
  document.querySelectorAll('.ym-store-card__fav').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const icon = btn.querySelector('i');
      icon.classList.toggle('fas');
      icon.classList.toggle('far');
      btn.style.color = icon.classList.contains('fas') ? 'var(--color-pink)' : '';
    });
  });

  /* ── 10. Toast auto-dismiss ── */
  document.querySelectorAll('.ym-toast').forEach(toast => {
    setTimeout(() => {
      toast.style.opacity    = '0';
      toast.style.transform  = 'translateX(40px)';
      toast.style.transition = 'all 0.4s ease';
      setTimeout(() => toast.remove(), 400);
    }, 4000);
  });

  /* ── 11. Active nav link ── */
  const currentPath = window.location.pathname;
  document.querySelectorAll('.ym-navbar__nav a, .ym-mobile-nav__links a').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  /* ── 12. Account Dropdown Toggle ── */
  const accountToggle = document.getElementById('ym-account-toggle');
  const accountMenu   = document.getElementById('ym-account-menu');

  if (accountToggle && accountMenu) {
    accountToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      accountMenu.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
      if (!accountToggle.contains(e.target) && !accountMenu.contains(e.target)) {
        accountMenu.classList.remove('active');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') accountMenu.classList.remove('active');
    });
  }
});


