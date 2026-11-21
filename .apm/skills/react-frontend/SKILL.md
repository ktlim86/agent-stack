---
name: react-frontend
description: "React 18+ reference for lead-frontend-engineer: component patterns, hooks (useState/useEffect/useCallback/useMemo/useRef), Context API vs state management, Vite build config, Vitest + Testing Library patterns, accessibility, CSS approaches, performance patterns, and common pitfalls."
---

# React Frontend Skill

Version: 1.0 (2026-11-21)

## React 18+ Component Patterns

### Functional components only
```tsx
// Prefer named exports for components
export function UserCard({ name, email }: { name: string; email: string }) {
  return (
    <div className="user-card">
      <h2>{name}</h2>
      <p>{email}</p>
    </div>
  );
}
```

### Component file structure
```
src/
  components/          ← reusable UI components
    UserCard/
      UserCard.tsx
      UserCard.test.tsx
      index.ts         ← re-export: export { UserCard } from './UserCard'
  pages/               ← route-level components
  hooks/               ← custom hooks (use*.ts)
  services/            ← API calls, no JSX
  types/               ← TypeScript interfaces
```

## Hooks

### useState
```tsx
const [count, setCount] = useState(0);
const [user, setUser] = useState<User | null>(null);

// Functional update for state based on previous value
setCount(prev => prev + 1);
```

### useEffect
```tsx
// Fetch on mount — always handle cleanup
useEffect(() => {
  let cancelled = false;
  async function fetchData() {
    const data = await api.getUser(userId);
    if (!cancelled) setUser(data);
  }
  fetchData();
  return () => { cancelled = true; };
}, [userId]);  // ← dependency array is required; never omit it
```

### useCallback and useMemo
```tsx
// useCallback: memoize functions passed as props to avoid child re-renders
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);

// useMemo: memoize expensive derived values (not components)
const sortedItems = useMemo(() => items.slice().sort(compare), [items]);
```

**Rule**: only add `useCallback`/`useMemo` when there is a measurable performance problem. Premature memoisation adds complexity without benefit.

### useRef
```tsx
// DOM ref
const inputRef = useRef<HTMLInputElement>(null);
useEffect(() => { inputRef.current?.focus(); }, []);

// Mutable value that doesn't trigger re-render (e.g. timers, subscriptions)
const timerRef = useRef<NodeJS.Timeout | null>(null);
```

## Context API vs State Management Libraries

| Scenario | Recommendation |
|----------|---------------|
| Theme, locale, auth user | Context API — infrequently updated, read widely |
| Complex UI state with many updates | Zustand or Jotai — simpler API than Redux |
| Server state (cache, loading, errors) | TanStack Query — built for async server data |
| Form state | React Hook Form — avoids controlled component re-render churn |

**Context pitfall**: every consumer re-renders when context value changes. Split contexts by update frequency. Never put frequently updated state (e.g. mouse position) in a context used by many components.

## Vite Build Configuration

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': '/src' },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,    // always for staging; disable for production if size matters
  },
  server: {
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
});
```

## Vitest + Testing Library Patterns

```bash
npm install -D vitest @testing-library/react @testing-library/user-event @testing-library/jest-dom jsdom
```

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test-setup.ts'],
  },
});

// src/test-setup.ts
import '@testing-library/jest-dom';
```

```tsx
// Component test example
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserCard } from './UserCard';

test('displays user name and email', () => {
  render(<UserCard name="Alice" email="alice@example.com" />);
  expect(screen.getByText('Alice')).toBeInTheDocument();
  expect(screen.getByText('alice@example.com')).toBeInTheDocument();
});

test('calls onDelete when delete button clicked', async () => {
  const onDelete = vi.fn();
  render(<UserCard name="Alice" email="alice@example.com" onDelete={onDelete} />);
  await userEvent.click(screen.getByRole('button', { name: /delete/i }));
  expect(onDelete).toHaveBeenCalledOnce();
});
```

**Test what the user sees**: query by role, label, text — not by CSS class or internal state. Never test implementation details.

## Accessibility (ARIA Basics)

- Use semantic HTML first: `<button>`, `<nav>`, `<main>`, `<header>`, `<form>`, `<label>`.
- Every `<img>` needs `alt` (empty `alt=""` for decorative images).
- Every form input needs a `<label>` (use `htmlFor` matching input `id`).
- Interactive elements must be keyboard focusable and operable (Enter/Space for buttons).
- Use `aria-label` or `aria-labelledby` only when visible text is not sufficient.
- Colour contrast ratio: ≥ 4.5:1 for normal text, ≥ 3:1 for large text (WCAG AA).

```tsx
// Bad
<div onClick={handleClick}>Click me</div>

// Good
<button type="button" onClick={handleClick}>Click me</button>
```

## CSS Approaches

Follow the project's existing approach — do not introduce a new methodology.

| Approach | When to use |
|----------|------------|
| CSS Modules | Scoped styles without a runtime; pairs well with Vite |
| Tailwind CSS | Utility-first; fast iteration; no context switching |
| CSS-in-JS (styled-components, Emotion) | Dynamic styles based on props; heavier runtime |

```tsx
// CSS Modules example
import styles from './UserCard.module.css';
export function UserCard() {
  return <div className={styles.card}>...</div>;
}
```

## Performance Patterns

### Code splitting / lazy loading
```tsx
import { lazy, Suspense } from 'react';
const HeavyChart = lazy(() => import('./HeavyChart'));

function Dashboard() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyChart />
    </Suspense>
  );
}
```

### Image optimisation
- Use `loading="lazy"` on below-the-fold images.
- Serve WebP/AVIF with `<picture>` fallback.
- Always set explicit `width` and `height` to prevent layout shift.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Missing `key` prop in lists | Add stable unique `key` to each list item (not array index) |
| Stale closure in `useEffect` | Include all referenced variables in the dependency array |
| Direct state mutation | Always create new objects: `setItems([...items, newItem])` |
| Async state update after unmount | Cancel async work in cleanup function |
| Context causing unnecessary re-renders | Split context or use `useMemo` on the context value |
| `useEffect` with missing deps | Run `eslint-plugin-react-hooks`; treat all warnings as errors |
| Inline object/array as prop | Memoize or define outside render to prevent child re-renders |

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
