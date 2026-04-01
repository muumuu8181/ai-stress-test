# 020-router: Client-side Router

A lightweight, dependency-free client-side router for TypeScript.

## Features

- **History API Base**: Modern routing using the HTML5 History API.
- **Hash Mode**: Support for legacy browsers or simple static hosting.
- **Dynamic Matching**: Support for path parameters (e.g., `/users/:id`).
- **Nested Routes**: Define hierarchical route structures.
- **Navigation Guards**: `beforeEach` and `afterEach` hooks for authentication and logic.
- **Per-route Guards**: `beforeEnter` guard for specific routes.
- **Redirects & 404**: Flexible redirection and wildcard matching.
- **Query & Hash**: Automatic parsing and stringification of query parameters and hashes.

## Installation

```bash
npm install
npm run build
```

## Usage

### Basic Setup

```typescript
import { Router } from './router';

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/about', name: 'about', component: About },
  { path: '/users/:id', name: 'user', component: UserDetail },
  { path: '*', name: 'not-found', component: NotFound }
];

const router = new Router({
  routes,
  mode: 'history', // or 'hash'
  base: '/'
});

// Access current route
console.log(router.currentRoute);
```

### Programmatic Navigation

```typescript
router.push('/about');
router.replace('/login');
router.go(-1); // Go back
```

### Nested Routes

```typescript
const routes = [
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      { path: 'dashboard', component: Dashboard },
      { path: 'settings', component: Settings }
    ]
  }
];
```

### Navigation Guards

```typescript
// Global guard
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isLoggedIn()) {
    next('/login');
  } else {
    next();
  }
});

// Per-route guard
const routes = [
  {
    path: '/profile',
    beforeEnter: (to, from, next) => {
      // Check auth here
      next();
    }
  }
];
```

## API Documentation

### `Router` Class

#### `constructor(options: RouterOptions)`
Initializes the router with the given options.

#### `push(to: string): void`
Navigates to the specified path and adds an entry to the history stack.

#### `replace(to: string): void`
Navigates to the specified path and replaces the current history entry.

#### `go(delta: number): void`
Moves backward or forward in history.

#### `beforeEach(guard: NavigationGuard): () => void`
Registers a global guard. Returns an unregister function.

#### `afterEach(hook: (to: Route, from: Route | null) => void): () => void`
Registers a global after-each hook. Returns an unregister function.

### `Route` Object

- `path`: Matched path pattern.
- `fullPath`: Full resolved URL.
- `params`: Parsed path parameters.
- `query`: Parsed query parameters.
- `hash`: URL hash.
- `name`: Route name.
- `meta`: Custom meta information.
- `matched`: Array of matched route records.

## License

ISC
