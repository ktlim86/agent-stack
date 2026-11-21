---
name: vanilla-frontend
description: "Vanilla JS / HTML5 reference for lead-frontend-engineer: semantic HTML5 structure, CSS custom properties, responsive design (flexbox/grid), vanilla DOM manipulation, ES modules, Vite bundling, Fetch API, Web Components basics, accessibility, and common pitfalls without a framework."
---

# Vanilla Frontend Skill

Version: 1.0 (2026-11-21)

## HTML5 Semantic Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>App Name</title>
  <link rel="stylesheet" href="/styles/main.css" />
</head>
<body>
  <header>
    <nav aria-label="Main navigation">
      <a href="/">Home</a>
      <a href="/about">About</a>
    </nav>
  </header>

  <main id="app">
    <section aria-labelledby="section-title">
      <h1 id="section-title">Section Title</h1>
      <article>...</article>
    </section>
  </main>

  <footer>
    <p>&copy; 2026 My App</p>
  </footer>

  <script type="module" src="/scripts/main.js"></script>
</body>
</html>
```

**Semantic elements to use**: `header`, `nav`, `main`, `section`, `article`, `aside`, `footer`, `figure`, `figcaption`, `time`, `address`.

## CSS Custom Properties and Responsive Design

### Custom properties (design tokens)
```css
:root {
  /* Colors */
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-text: #111827;
  --color-text-muted: #6b7280;
  --color-bg: #ffffff;
  --color-surface: #f9fafb;

  /* Spacing (4px base) */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-8: 2rem;

  /* Typography */
  --font-sans: system-ui, -apple-system, sans-serif;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;

  /* Radii */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
}
```

### Flexbox patterns
```css
/* Horizontal stack */
.row { display: flex; align-items: center; gap: var(--space-4); }

/* Vertical stack */
.col { display: flex; flex-direction: column; gap: var(--space-2); }

/* Push last item right */
.row--spread { display: flex; justify-content: space-between; align-items: center; }

/* Center both axes */
.center { display: flex; align-items: center; justify-content: center; }
```

### Grid patterns
```css
/* Responsive card grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
}

/* Two-column layout */
.layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: var(--space-8);
}
```

### Responsive breakpoints
```css
/* Mobile-first */
.container {
  padding: var(--space-4);
}

@media (min-width: 640px) {   /* sm */
  .container { padding: var(--space-8); }
}

@media (min-width: 1024px) {  /* lg */
  .container { max-width: 1280px; margin-inline: auto; }
}
```

## Vanilla JS DOM Manipulation

```js
// Query (prefer querySelector over getElementById for consistency)
const button = document.querySelector('#submit-btn');
const items = document.querySelectorAll('.list-item');  // returns NodeList

// Create and append
function createCard(title, body) {
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `<h2 class="card__title">${escapeHtml(title)}</h2>
                    <p class="card__body">${escapeHtml(body)}</p>`;
  return card;
}
document.querySelector('#cards').appendChild(createCard('Hello', 'World'));

// Event delegation (one listener for dynamic lists)
document.querySelector('#list').addEventListener('click', (event) => {
  const item = event.target.closest('[data-id]');
  if (item) handleItemClick(item.dataset.id);
});

// Update existing element
const counter = document.querySelector('#counter');
let count = 0;
button.addEventListener('click', () => {
  count += 1;
  counter.textContent = count;
});
```

### escapeHtml utility (always escape user content)
```js
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
```

**Never use `innerHTML` with unescaped user input** — it creates XSS vulnerabilities.

## ES Modules

```js
// utils/api.js — named exports
export async function fetchUsers() {
  const res = await fetch('/api/users');
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function createUser(data) {
  const res = await fetch('/api/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// main.js — import
import { fetchUsers } from './utils/api.js';
```

## Vite for Bundling

```bash
npm create vite@latest my-app -- --template vanilla
cd my-app && npm install
npm run dev    # dev server
npm run build  # production bundle to dist/
```

```js
// vite.config.js
import { defineConfig } from 'vite';
export default defineConfig({
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  server: {
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
});
```

## Fetch API for HTTP Calls

```js
// GET
async function getUser(id) {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch user: ${res.status}`);
  return res.json();
}

// POST with JSON
async function createUser(data) {
  const res = await fetch('/api/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create user: ${res.status}`);
  return res.json();
}

// With auth header
const res = await fetch('/api/protected', {
  headers: { 'Authorization': `Bearer ${token}` },
});

// AbortController for cancellation
const controller = new AbortController();
const res = await fetch('/api/users', { signal: controller.signal });
// cancel: controller.abort();
```

## Web Components Basics

```js
// Define a custom element
class UserCard extends HTMLElement {
  connectedCallback() {
    const name = this.getAttribute('name') ?? '';
    const email = this.getAttribute('email') ?? '';
    this.innerHTML = `
      <div class="user-card">
        <h2>${escapeHtml(name)}</h2>
        <p>${escapeHtml(email)}</p>
      </div>
    `;
  }
}

customElements.define('user-card', UserCard);
```

```html
<!-- Usage -->
<user-card name="Alice" email="alice@example.com"></user-card>
```

Use Web Components for reusable widgets shared across pages without a build step. For complex state management, prefer a simple module pattern over Web Components.

## Accessibility

- Use semantic HTML over `div` for every interactive element.
- All form fields need `<label>` elements with `for` matching input `id`.
- All images need `alt` text; `alt=""` for purely decorative images.
- Keyboard focus must be visible — never `outline: none` without a replacement.
- Interactive elements must be reachable by Tab and operable by Enter/Space.
- Use `aria-live="polite"` regions for dynamic content updates (e.g. error messages).

```html
<!-- Accessible form field -->
<div class="field">
  <label for="email">Email address</label>
  <input type="email" id="email" name="email" autocomplete="email" required />
  <span id="email-error" role="alert" aria-live="polite"></span>
</div>
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `innerHTML` with user content | Always escape with `escapeHtml()` or use `textContent` |
| No module type on `<script>` | Add `type="module"` to use `import`/`export` |
| Forgetting `.js` extension in imports | ES modules require the full file extension |
| Event listener memory leak | Remove listeners with `removeEventListener` when element is removed |
| Synchronous fetch blocking UI | Always use `async/await`; never call `.json()` without `await` |
| `querySelectorAll` returns NodeList not Array | Convert: `Array.from(document.querySelectorAll('.item'))` |
| Hardcoded API URLs | Use Vite's `import.meta.env` for environment-specific values |

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
