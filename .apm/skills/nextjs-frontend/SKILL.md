---
name: nextjs-frontend
description: "Next.js 14+ App Router reference for lead-frontend-engineer: Server Components vs Client Components, API routes, data fetching, use client directive, Vercel vs self-hosted deployment, Vitest/Jest unit tests, Playwright E2E, environment variable handling, and common pitfalls."
---

# Next.js Frontend Skill

Version: 1.0 (2026-11-21)

## App Router Fundamentals (Next.js 14+)

### File conventions
```
app/
  layout.tsx           ← root layout (always a Server Component)
  page.tsx             ← / route
  loading.tsx          ← loading UI (Suspense boundary)
  error.tsx            ← error boundary ('use client' required)
  not-found.tsx        ← 404 page
  (auth)/              ← route group (no URL segment)
    login/
      page.tsx
  api/
    users/
      route.ts         ← API route handler
  users/
    [id]/
      page.tsx         ← /users/:id
```

## Server Components vs Client Components

| | Server Component | Client Component |
|-|-----------------|-----------------|
| Default? | Yes | Must add `'use client'` |
| Can use hooks? | No | Yes |
| Can use browser APIs? | No | Yes |
| Access server resources directly? | Yes | No |
| Bundle size impact | None (runs on server) | Added to JS bundle |

```tsx
// Server Component (default) — no directive needed
// app/users/page.tsx
async function UsersPage() {
  const users = await db.query('SELECT * FROM users');  // direct DB access
  return <UserList users={users} />;
}

// Client Component — add directive at top of file
'use client';
import { useState } from 'react';
export function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

**Rule**: keep `'use client'` boundaries as low in the component tree as possible. Server Components are free (no JS to client); push interactivity into leaf components.

## Data Fetching Patterns

### Server Component fetch (preferred)
```tsx
// Fetch with Next.js extended fetch — built-in caching
async function ProductPage({ params }: { params: { id: string } }) {
  // Cache for 60 seconds
  const product = await fetch(`https://api.example.com/products/${params.id}`, {
    next: { revalidate: 60 },
  }).then(r => r.json());

  return <div>{product.name}</div>;
}
```

### Static vs dynamic
```tsx
// Force dynamic (no caching — always fresh)
export const dynamic = 'force-dynamic';

// Force static (cache indefinitely)
export const dynamic = 'force-static';

// Revalidate on a schedule
export const revalidate = 3600;  // seconds
```

### Server Actions (forms)
```tsx
// Server action for form mutation
async function createUser(formData: FormData) {
  'use server';
  const name = formData.get('name') as string;
  await db.createUser({ name });
  revalidatePath('/users');
}

export function CreateUserForm() {
  return (
    <form action={createUser}>
      <input name="name" required />
      <button type="submit">Create</button>
    </form>
  );
}
```

## API Routes

```ts
// app/api/users/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const users = await db.getUsers();
  return NextResponse.json(users);
}

export async function POST(request: Request) {
  const body = await request.json();
  const user = await db.createUser(body);
  return NextResponse.json(user, { status: 201 });
}
```

## Environment Variables

```bash
# .env.local (never commit to git)
DATABASE_URL=postgres://...
NEXT_PUBLIC_API_URL=https://api.example.com  # NEXT_PUBLIC_ prefix → exposed to browser

# .env (commit to git — only non-secret defaults)
NEXT_PUBLIC_APP_NAME=MyApp
```

```ts
// Server-only (no NEXT_PUBLIC_)
const dbUrl = process.env.DATABASE_URL;  // only accessible server-side

// Browser-accessible
const apiUrl = process.env.NEXT_PUBLIC_API_URL;  // bundled into client JS
```

**Never** put secrets in `NEXT_PUBLIC_*` variables — they are visible in the browser bundle.

## Deployment

### Vercel (easiest)
- Push to GitHub; Vercel detects Next.js automatically.
- Preview deployments on every PR branch.
- Environment variables set in Vercel dashboard — never in committed files.

### Self-hosted (Node.js)
```bash
# Build
npm run build

# Start production server
node .next/standalone/server.js

# Or with PM2
pm2 start .next/standalone/server.js --name nextjs-app
```

```dockerfile
# Minimal production Dockerfile for Next.js standalone output
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

Add `output: 'standalone'` to `next.config.js` to enable the standalone output.

## Unit Tests (Vitest)

```bash
npm install -D vitest @vitejs/plugin-react @testing-library/react @testing-library/user-event jsdom
```

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins: [react()],
  test: { environment: 'jsdom', globals: true, setupFiles: ['./test-setup.ts'] },
});
```

For Server Components: render them as async functions in tests; mock `next/navigation`, `next/headers`, and database calls since the test environment has no Node server.

## E2E Tests (Playwright)

```bash
npm install -D @playwright/test
npx playwright install
```

```ts
// tests/e2e/home.spec.ts
import { test, expect } from '@playwright/test';

test('home page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /welcome/i })).toBeVisible();
});
```

```bash
# Run E2E tests (requires running dev/prod server)
npx playwright test
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Using `useState` in a Server Component | Move state to a Client Component with `'use client'` |
| Fetching the same data in many components | Fetch high up in the tree; pass as props or use React cache |
| Secrets in `NEXT_PUBLIC_*` | Only put non-secret values in `NEXT_PUBLIC_` variables |
| Large Client Component bundles | Lazy-load with `dynamic()` from `next/dynamic` |
| Not handling loading states | Add `loading.tsx` files alongside `page.tsx` |
| Stale data after mutation | Call `revalidatePath()` or `revalidateTag()` in Server Actions |
| Incorrect static/dynamic caching | Explicitly set `export const dynamic` — do not rely on inference |

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
