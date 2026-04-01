import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { Router } from '../src/router';
import { RouteRecord } from '../src/types';

describe('Hash Router', () => {
  const routes: RouteRecord[] = [
    { path: '/', name: 'home' },
    { path: '/about', name: 'about' },
  ];

  let router: Router;

  beforeEach(() => {
    // Reset browser environment for hash routing
    window.location.hash = '';
    router = new Router({ routes, mode: 'hash' });
  });

  afterEach(() => {
    router.destroy();
  });

  it('initializes with hash route', () => {
    expect(window.location.hash).toBe('#/');
    expect(router.currentRoute?.name).toBe('home');
  });

  it('navigates via hash change', async () => {
    router.push('/about');
    expect(window.location.hash).toBe('#/about');
    expect(router.currentRoute?.name).toBe('about');
  });

  it('handles manual hash change', async () => {
    window.location.hash = '#/about';
    // Manually trigger hashchange event for testing
    window.dispatchEvent(new HashChangeEvent('hashchange'));

    // History.listen will trigger transitionTo, which is async
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(router.currentRoute?.name).toBe('about');
  });
});
