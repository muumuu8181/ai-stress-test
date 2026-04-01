import { describe, it, expect } from 'vitest';
import { parseQuery, stringifyQuery } from '../src/utils';

describe('Query Utils', () => {
  it('parses simple query', () => {
    expect(parseQuery('a=1&b=2')).toEqual({ a: '1', b: '2' });
  });

  it('parses query with leading ?', () => {
    expect(parseQuery('?a=1&b=2')).toEqual({ a: '1', b: '2' });
  });

  it('parses array parameters', () => {
    expect(parseQuery('a=1&a=2&b=3')).toEqual({ a: ['1', '2'], b: '3' });
  });

  it('parses empty values', () => {
    expect(parseQuery('a=&b')).toEqual({ a: '', b: null });
  });

  it('handles encoded values', () => {
    expect(parseQuery('name=John%20Doe&city=New%20York')).toEqual({
      name: 'John Doe',
      city: 'New York',
    });
  });

  it('stringifies simple query', () => {
    expect(stringifyQuery({ a: '1', b: '2' })).toBe('?a=1&b=2');
  });

  it('stringifies array parameters', () => {
    expect(stringifyQuery({ a: ['1', '2'], b: '3' })).toBe('?a=1&a=2&b=3');
  });

  it('stringifies null values', () => {
    expect(stringifyQuery({ a: null, b: '' })).toBe('?a&b=');
  });

  it('handles empty query object', () => {
    expect(stringifyQuery({})).toBe('');
  });
});
