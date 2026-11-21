---
name: vue-frontend
description: "Vue 3 reference for lead-frontend-engineer: Composition API (setup/ref/reactive/computed/watch), component patterns, Pinia state management, Vue Router, Vite configuration, Vitest + Vue Test Utils patterns, accessibility, and common pitfalls."
---

# Vue Frontend Skill

Version: 1.0 (2026-11-21)

## Vue 3 Composition API

### `<script setup>` (preferred)
```vue
<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

// Props and emits
const props = defineProps<{ userId: string }>();
const emit = defineEmits<{ (e: 'update', value: string): void }>();

// Reactive state
const count = ref(0);
const user = ref<User | null>(null);

// Computed
const displayName = computed(() => user.value?.name ?? 'Anonymous');

// Watcher
watch(() => props.userId, async (newId) => {
  user.value = await fetchUser(newId);
}, { immediate: true });

// Lifecycle
onMounted(() => {
  console.log('mounted');
});
</script>

<template>
  <div>{{ displayName }}</div>
</template>
```

### ref vs reactive
```ts
// ref: primitives and objects you want to reassign
const count = ref(0);          // access as count.value in script
const items = ref<string[]>([]);

// reactive: objects you never reassign the top-level reference
const form = reactive({ name: '', email: '' });
// access as form.name (no .value needed in template or script)

// Prefer ref for most cases — easier to extract into composables
```

### computed
```ts
const total = computed(() => items.value.reduce((sum, item) => sum + item.price, 0));
// computed is read-only by default
// writable computed (rare):
const fullName = computed({
  get: () => `${firstName.value} ${lastName.value}`,
  set: (val) => { [firstName.value, lastName.value] = val.split(' '); },
});
```

### watch vs watchEffect
```ts
// watch: explicit sources, lazy by default
watch(count, (newVal, oldVal) => { console.log(newVal); });
watch([a, b], ([newA, newB]) => { /* ... */ });

// watchEffect: tracks dependencies automatically, runs immediately
watchEffect(() => {
  document.title = `Count: ${count.value}`;  // re-runs whenever count changes
});
```

## Component Patterns

### File structure
```
src/
  components/          ← reusable UI components
    BaseButton.vue
    UserCard.vue
  views/               ← route-level components
    HomeView.vue
  composables/         ← reusable logic (use*.ts)
    useUser.ts
  stores/              ← Pinia stores
    user.ts
  router/              ← Vue Router config
    index.ts
```

### Component naming
- Single-file components: `PascalCase.vue`
- Base/global components: prefix with `Base` (e.g. `BaseButton.vue`)
- View components: suffix with `View` (e.g. `HomeView.vue`)

### Composables
```ts
// composables/useUser.ts
export function useUser(userId: Ref<string>) {
  const user = ref<User | null>(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  watch(userId, async (id) => {
    loading.value = true;
    error.value = null;
    try {
      user.value = await fetchUser(id);
    } catch (e) {
      error.value = e as Error;
    } finally {
      loading.value = false;
    }
  }, { immediate: true });

  return { user, loading, error };
}
```

## Pinia State Management

```bash
npm install pinia
```

```ts
// stores/user.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null);
  const isLoggedIn = computed(() => currentUser.value !== null);

  async function login(email: string, password: string) {
    currentUser.value = await api.login(email, password);
  }

  function logout() {
    currentUser.value = null;
  }

  return { currentUser, isLoggedIn, login, logout };
});
```

```ts
// main.ts — register Pinia
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';

const app = createApp(App);
app.use(createPinia());
app.mount('#app');
```

## Vue Router

```ts
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/users/:id', name: 'user', component: () => import('@/views/UserView.vue') },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
  ],
});

// Navigation guard for auth
router.beforeEach((to) => {
  const store = useUserStore();
  if (to.meta.requiresAuth && !store.isLoggedIn) {
    return { name: 'login' };
  }
});
```

## Vite Configuration

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
});
```

## Vitest + Vue Test Utils

```bash
npm install -D vitest @vue/test-utils jsdom @testing-library/vue
```

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
export default defineConfig({
  plugins: [vue()],
  test: { environment: 'jsdom', globals: true },
});
```

```ts
// UserCard.test.ts
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import UserCard from '@/components/UserCard.vue';

describe('UserCard', () => {
  it('displays user name', () => {
    const wrapper = mount(UserCard, {
      props: { name: 'Alice', email: 'alice@example.com' },
      global: { plugins: [createPinia()] },
    });
    expect(wrapper.text()).toContain('Alice');
  });

  it('emits delete event when button clicked', async () => {
    const wrapper = mount(UserCard, { props: { name: 'Alice', email: 'a@b.com' } });
    await wrapper.find('[data-testid="delete-btn"]').trigger('click');
    expect(wrapper.emitted('delete')).toBeTruthy();
  });
});
```

## Accessibility

- Use semantic HTML: `<button>`, `<nav>`, `<main>`, `<header>`, `<form>`, `<label>`.
- All form inputs need a `<label>` with matching `for`/`id` (or use `v-model` with label wrapping).
- Use `aria-label` only when no visible label is possible.
- All images need `alt`; decorative images use `alt=""`.
- Test keyboard navigation: Tab, Enter, Space, Escape must work correctly for interactive elements.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Mutating props directly | Use `emit` to notify parent; never `props.x = value` |
| Losing reactivity with destructuring | `const { count } = storeToRefs(store)` — not `const { count } = store` |
| `reactive()` object reassignment | `Object.assign(form, newData)` — never `form = newData` |
| Missing `:key` in `v-for` | Always provide a stable unique key |
| `v-if` and `v-for` on same element | Use a wrapper `<template>` — never combine on same element |
| Async setup without error handling | Wrap in try/catch; set an error ref |
| Store actions not awaited | Always `await store.fetchUser()` to catch errors |

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
