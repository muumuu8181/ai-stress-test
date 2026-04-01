import { describe, it, expect } from 'vitest';
import { RouterMatcher } from '../src/matcher';
import { RouteRecord } from '../src/types';

describe('RouterMatcher', () => {
  const routes: RouteRecord[] = [
    { path: '/', name: 'home' },
    { path: '/about', name: 'about' },
    {
      path: '/users/:id',
      name: 'user-detail',
      children: [{ path: 'profile', name: 'user-profile' }],
    },
    { path: '*', name: 'not-found' },
  ];

  const matcher = new RouterMatcher(routes);

  it('matches simple path', () => {
    const route = matcher.match('/');
    expect(route).not.toBeNull();
    expect(route?.name).toBe('home');
    expect(route?.path).toBe('/');
  });

  it('matches path with params', () => {
    const route = matcher.match('/users/123');
    expect(route).not.toBeNull();
    expect(route?.name).toBe('user-detail');
    expect(route?.params).toEqual({ id: '123' });
  });

  it('matches nested paths', () => {
    const route = matcher.match('/users/123/profile');
    expect(route).not.toBeNull();
    expect(route?.name).toBe('user-profile');
    expect(route?.params).toEqual({ id: '123' });
    expect(route?.matched.length).toBe(2);
  });

  it('handles query parameters', () => {
    const route = matcher.match('/about?q=vitest');
    expect(route).not.toBeNull();
    expect(route?.name).toBe('about');
    expect(route?.query).toEqual({ q: 'vitest' });
  });

  it('handles hashes', () => {
    const route = matcher.match('/about#section1');
    expect(route).not.toBeNull();
    expect(route?.name).toBe('about');
    expect(route?.hash).toBe('#section1');
  });

  it('handles fallback route', () => {
    const route = matcher.match('/non-existent');
    expect(route).not.toBeNull();
    expect(route?.name).toBe('not-found');
  });

  it('normalizes trailing slash', () => {
    const route = matcher.match('/about/');
    expect(route).not.toBeNull();
    expect(route?.name).toBe('about');
  });
});
