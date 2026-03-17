/* ════════════════════════════════════════
   CAFLink – Main JavaScript
   ════════════════════════════════════════ */

'use strict';

// ─── API BASE ───────────────────────────
const API = '';   // same-origin

// ─── UTILITY ────────────────────────────
const $ = id => document.getElementById(id);
const $$ = sel => document.querySelectorAll(sel);

function showToast(msg, type = 'info', duration = 4500) {
  const t = $('toast');
  t.textContent = msg;
  t.className = `show ${type}`;
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), duration);
}

// ─── NOTIFICATION BAR ───────────────────
(function initNotif() {
  const bar = $('notif-bar');
  const nav = $('main-nav');
  const dismissed = sessionStorage.getItem('notif_dismissed');
  if (!dismissed) {
    setTimeout(() => {
      bar.classList.add('show');
      nav.classList.add('notif-open');
    }, 1400);
  }
  $('notif-close').addEventListener('click', () => {
    bar.classList.remove('show');
    nav.classList.remove('notif-open');
    sessionStorage.setItem('notif_dismissed', '1');
  });
})();

// ─── NAV SCROLL + ACTIVE ────────────────
(function initNav() {
  const nav = $('main-nav');
  const sections = $$('section[id], div[id="home"]');
  const links = $$('.nav-links a');

  window.addEventListener('scroll', () => {
    // Scrolled shadow
    nav.classList.toggle('scrolled', window.scrollY > 20);
    // Scroll top button
    $('scroll-top').classList.toggle('show', window.scrollY > 500);
    // Active link
    let current = '';
    sections.forEach(s => {
      if (window.scrollY >= s.offsetTop - 120) current = s.id;
    });
    links.forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === '#' + current);
    });
  }, { passive: true });

  // Hamburger
  const ham = $('hamburger');
  const mob = $('mobile-nav');
  ham.addEventListener('click', () => {
    ham.classList.toggle('open');
    mob.classList.toggle('active');
  });
  mob.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      ham.classList.remove('open');
      mob.classList.remove('active');
    });
  });
})();

// ─── SCROLL TOP ─────────────────────────
$('scroll-top').addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// ─── REVEAL ON SCROLL ───────────────────
(function initReveal() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); obs.unobserve(e.target); } });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
  $$('.reveal').forEach(el => obs.observe(el));
})();

// ─── COUNTER ANIMATION ──────────────────
(function initCounters() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.querySelectorAll('[data-count]').forEach(el => {
          const target = parseInt(el.dataset.count);
          const suffix = el.dataset.suffix || '';
          let cur = 0;
          const step = target / 55;
          const t = setInterval(() => {
            cur += step;
            if (cur >= target) { el.textContent = target + suffix; clearInterval(t); }
            else { el.textContent = Math.floor(cur); }
          }, 18);
        });
        obs.disconnect();
      }
    });
  }, { threshold: 0.6 });
  const statsEl = document.querySelector('.hero-stats');
  if (statsEl) obs.observe(statsEl);
})();

// ─── LOAD SERVICES ──────────────────────
async function loadServices() {
  const grid = $('services-grid');
  if (!grid) return;
  try {
    const res = await fetch(API + '/api/services');
    const json = await res.json();
    if (!json.success) throw new Error();
    grid.innerHTML = '';
    json.data.forEach((s, i) => {
      const delay = ['', 'd1', 'd2', 'd1', 'd2', 'd3', ''][i] || '';
      const feats = (s.features || []).map(f => `<li>${f}</li>`).join('');
      grid.innerHTML += `
        <div class="svc-card reveal ${delay}" data-id="${s.id}">
          <div class="svc-icon-wrap">${s.icon || '⚡'}</div>
          <div class="svc-title">${s.title}</div>
          <div class="svc-desc">${s.description}</div>
          <ul class="svc-features">${feats}</ul>
          <span class="svc-arrow">Learn more →</span>
        </div>`;
    });
    // Re-observe new elements
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); obs.unobserve(e.target); } });
    }, { threshold: 0.1 });
    grid.querySelectorAll('.reveal').forEach(el => obs.observe(el));

    // Click handler
    grid.querySelectorAll('.svc-card').forEach(card => {
      card.addEventListener('click', () => {
        const title = card.querySelector('.svc-title').textContent;
        showToast(`Interested in "${title}"? Contact us below! 👇`, 'info');
        setTimeout(() => $('contact').scrollIntoView({ behavior: 'smooth' }), 1000);
      });
    });
  } catch {
    grid.innerHTML = `<div class="loading-card"><p style="color:var(--muted)">Could not load services. Please refresh.</p></div>`;
  }
}

// ─── LOAD TESTIMONIALS ──────────────────
async function loadTestimonials() {
  const grid = $('testi-grid');
  if (!grid) return;
  try {
    const res = await fetch(API + '/api/testimonials');
    const json = await res.json();
    if (!json.success) throw new Error();
    grid.innerHTML = '';
    json.data.forEach((t, i) => {
      const delay = ['', 'd1', 'd2', '', 'd1', 'd2'][i % 3] || '';
      const stars = '★'.repeat(t.rating || 5);
      grid.innerHTML += `
        <div class="testi-card reveal ${delay}">
          <div class="stars">${stars}</div>
          <div class="testi-q">"</div>
          <p class="testi-text">${t.message}</p>
          <div class="testi-author">
            <div class="tav">${t.avatar || t.name.substring(0,2).toUpperCase()}</div>
            <div>
              <div class="tav-name">${t.name}</div>
              <div class="tav-role">${t.role}${t.company ? ', ' + t.company : ''}</div>
            </div>
          </div>
        </div>`;
    });
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); obs.unobserve(e.target); } });
    }, { threshold: 0.1 });
    grid.querySelectorAll('.reveal').forEach(el => obs.observe(el));
  } catch {
    grid.innerHTML = `<div class="loading-testi"></div>`.repeat(3);
  }
}

// ─── LOAD STATS ─────────────────────────
async function loadStats() {
  try {
    const res = await fetch(API + '/api/stats');
    const json = await res.json();
    if (!json.success) return;
    const wrap = document.querySelector('.hero-stats');
    if (!wrap) return;
    wrap.innerHTML = '';
    json.data.forEach(s => {
      wrap.innerHTML += `
        <div>
          <div class="stat-n" data-count="${s.value}" data-suffix="${s.suffix}">0</div>
          <div class="stat-l">${s.label}</div>
        </div>`;
    });
    // Re-init counters
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.querySelectorAll('[data-count]').forEach(el => {
            const target = parseInt(el.dataset.count);
            const suffix = el.dataset.suffix || '';
            let cur = 0; const step = target / 55;
            const t = setInterval(() => {
              cur += step;
              if (cur >= target) { el.textContent = target + suffix; clearInterval(t); }
              else el.textContent = Math.floor(cur);
            }, 18);
          });
          obs.disconnect();
        }
      });
    }, { threshold: 0.6 });
    obs.observe(wrap);
  } catch { /* use fallback HTML */ }
}

// ─── CONTACT FORM ───────────────────────
(function initContactForm() {
  const form = $('contact-form');
  const btn  = $('contact-submit');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
      first_name: $('c-fname').value.trim(),
      last_name:  $('c-lname').value.trim(),
      email:      $('c-email').value.trim(),
      phone:      $('c-phone').value.trim(),
      service:    $('c-service').value,
      budget:     $('c-budget').value,
      message:    $('c-msg').value.trim(),
    };

    // Client-side validation
    if (!data.first_name) { showToast('First name is required', 'error'); $('c-fname').focus(); return; }
    if (!data.email || !data.email.includes('@')) { showToast('Valid email is required', 'error'); $('c-email').focus(); return; }
    if (!data.service) { showToast('Please select a service', 'error'); $('c-service').focus(); return; }

    btn.disabled = true;
    btn.innerHTML = '<span class="spin">⏳</span> Sending…';

    try {
      const res = await fetch(API + '/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const json = await res.json();
      if (json.success) {
        showToast(`✅ ${json.message}`, 'success', 6000);
        if (json.inquiry_number) {
          showToast(`📋 Your inquiry number: ${json.inquiry_number}`, 'info', 7000);
        }
        form.reset();
      } else {
        showToast(`❌ ${json.message}`, 'error');
      }
    } catch {
      showToast('Network error. Please try again.', 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = 'Send Message →';
    }
  });
})();

// ─── NEWSLETTER ─────────────────────────
async function subscribeNewsletter() {
  const input = $('nl-email');
  const email = input.value.trim();
  if (!email || !email.includes('@')) { showToast('Please enter a valid email address', 'error'); return; }
  const btn = $('nl-btn');
  btn.disabled = true; btn.textContent = '…';
  try {
    const res = await fetch(API + '/api/newsletter', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    const json = await res.json();
    showToast(json.message, json.success ? 'success' : 'error');
    if (json.success) input.value = '';
  } catch { showToast('Subscription failed. Try again.', 'error'); }
  finally { btn.disabled = false; btn.textContent = 'Subscribe'; }
}

// ─── SMOOTH SCROLL NAV ──────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth' }); }
  });
});

// ─── INIT ───────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  loadServices();
  loadTestimonials();
});
