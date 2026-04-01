import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { Router } from '../src/router';
import { RouteRecord, Route } from '../src/types';

describe('Router Integration', () => {
  const routes: RouteRecord[] = [
    { path: '/', name: 'home' },
    { path: '/about', name: 'about' },
    { path: '/redirect', name: 'redirect', redirect: '/about' },
    {
      path: '/user/:id',
      name: 'user',
      beforeEnter: (to, from, next) => {
        if (to.params.id === '0') {
          next(false);
        } else {
          next();
        }
      },
    },
    { path: '*', name: 'not-found' },
  ];

  let router: Router;

  beforeEach(() => {
    // Reset browser environment for each test
    window.history.replaceState({}, '', '/');
    router = new Router({ routes });
  });

  afterEach(() => {
    router.destroy();
  });

  it('initializes with current route', () => {
    expect(router.currentRoute).not.toBeNull();
    expect(router.currentRoute?.name).toBe('home');
  });

  it('navigates to a new route via push', () => {
    router.push('/about');
    expect(router.currentRoute?.name).toBe('about');
    expect(window.location.pathname).toBe('/about');
  });

  it('navigates with params', () => {
    router.push('/user/123');
    expect(router.currentRoute?.name).toBe('user');
    expect(router.currentRoute?.params).toEqual({ id: '123' });
    expect(window.location.pathname).toBe('/user/123');
  });

  it('handles global beforeEach guards', async () => {
    const guard = vi.fn((to, from, next) => next());
    router.beforeEach(guard);

    router.push('/about');

    // We need to wait for the transition because it's async
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(guard).toHaveBeenCalled();
    expect(router.currentRoute?.name).toBe('about');
  });

  it('aborts navigation if beforeEach guard returns false', async () => {
    router.beforeEach((to, from, next) => {
      if (to.path === '/about') {
        next(false);
      } else {
        next();
      }
    });

    router.push('/about');
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(router.currentRoute?.name).toBe('home');
  });

  it('handles per-route guards (beforeEnter)', async () => {
    router.push('/user/0'); // This ID is restricted in beforeEnter
    await new Promise(resolve => setTimeout(resolve, 0));
    expect(router.currentRoute?.name).toBe('home');

    router.push('/user/123');
    await new Promise(resolve => setTimeout(resolve, 0));
    expect(router.currentRoute?.name).toBe('user');
  });

  it('handles redirects', async () => {
    router.push('/redirect');
    await new Promise(resolve => setTimeout(resolve, 0));
    expect(router.currentRoute?.name).toBe('about');
    expect(window.location.pathname).toBe('/about');
  });

  it('handles global afterEach hooks', async () => {
    const hook = vi.fn();
    router.afterEach(hook);

    router.push('/about');
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(hook).toHaveBeenCalled();
    // Verify that at least one call had 'about' as destination
    const calledWithAbout = hook.mock.calls.some(call => call[0].name === 'about');
    expect(calledWithAbout).toBe(true);
  });

  it('navigates to fallback route for unknown paths', async () => {
    router.push('/unknown-path');
    await new Promise(resolve => setTimeout(resolve, 0));
    expect(router.currentRoute?.name).toBe('not-found');
  });
});
