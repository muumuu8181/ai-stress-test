import { describe, it, expect, beforeEach } from 'vitest';
import { I18n } from '../src/i18n';

describe('I18n Class', () => {
  let i18n: I18n;

  beforeEach(() => {
    i18n = new I18n({
      defaultLocale: 'en-US',
      fallbackLocale: 'en',
      translations: {
        'en-US': {
          hello: 'Hello',
          nested: {
            world: 'World',
          },
          greet: 'Hi, {name}!',
          apples: {
            one: 'One apple',
            other: '{count} apples',
          },
        },
        'en': {
          fallbackKey: 'This is fallback',
          hello: 'Hello from en',
        },
        'ja-JP': {
          hello: 'こんにちは',
          apples: {
            other: '{count}個のりんご',
          },
        },
      },
    });
  });

  describe('Basic Translation', () => {
    it('should translate a simple key', () => {
      expect(i18n.t('hello')).toBe('Hello');
    });

    it('should translate a nested key', () => {
      expect(i18n.t('nested.world')).toBe('World');
    });

    it('should return the key if translation is missing', () => {
      expect(i18n.t('missing.key')).toBe('missing.key');
    });
  });

  describe('Locale Management', () => {
    it('should change locale', () => {
      i18n.setLocale('ja-JP');
      expect(i18n.getLocale()).toBe('ja-JP');
      expect(i18n.t('hello')).toBe('こんにちは');
    });
  });

  describe('Fallback Chain', () => {
    it('should fallback from en-US to en', () => {
      expect(i18n.t('fallbackKey')).toBe('This is fallback');
    });

    it('should fallback to fallbackLocale if key is missing in current locale', () => {
      i18n.setLocale('ja-JP');
      expect(i18n.t('fallbackKey')).toBe('This is fallback');
    });

    it('should try language code if full locale not found', () => {
      i18n.setLocale('en-GB');
      expect(i18n.t('hello')).toBe('Hello from en');
    });
  });

  describe('Interpolation', () => {
    it('should interpolate variables', () => {
      expect(i18n.t('greet', { name: 'Jules' })).toBe('Hi, Jules!');
    });

    it('should leave unknown placeholders as is', () => {
      expect(i18n.t('greet', { name_not_found: 'Jules' })).toBe('Hi, {name}!');
    });
  });

  describe('Pluralization', () => {
    it('should pluralize correctly in English (one)', () => {
      expect(i18n.t('apples', { count: 1 })).toBe('One apple');
    });

    it('should pluralize correctly in English (other)', () => {
      expect(i18n.t('apples', { count: 5 })).toBe('5 apples');
    });

    it('should pluralize correctly in English (zero -> other)', () => {
      expect(i18n.t('apples', { count: 0 })).toBe('0 apples');
    });

    it('should handle languages with only "other" category', () => {
      i18n.setLocale('ja-JP');
      expect(i18n.t('apples', { count: 1 })).toBe('1個のりんご');
      expect(i18n.t('apples', { count: 5 })).toBe('5個のりんご');
    });
  });

  describe('Formatting', () => {
    it('should format numbers correctly', () => {
      i18n.setLocale('en-US');
      // Use replace to normalize non-breaking spaces if any, though for numbers it's usually standard spaces or commas
      expect(i18n.formatNumber(1000.5).replace(/\u00A0/g, ' ')).toBe('1,000.5');

      i18n.setLocale('ja-JP');
      expect(i18n.formatNumber(1000.5)).toBe('1,000.5');
    });

    it('should format dates correctly', () => {
      const date = new Date(2023, 0, 1); // 2023-01-01
      i18n.setLocale('en-US');
      expect(i18n.formatDate(date)).toBe('1/1/2023');

      i18n.setLocale('ja-JP');
      expect(i18n.formatDate(date)).toBe('2023/1/1');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty translations', () => {
      const i18nEmpty = new I18n({ defaultLocale: 'en' });
      expect(i18nEmpty.t('any')).toBe('any');
    });

    it('should handle null/undefined inputs gracefully', () => {
      expect(i18n.t('')).toBe('');
      // @ts-ignore
      expect(i18n.t(null)).toBe(null);
    });

    it('should handle non-object translation resource leaf', () => {
      i18n.loadTranslations('en', { invalid: { sub: 'value' } });
      expect(i18n.t('invalid')).toBe('invalid');
    });

    it('should handle deep merging correctly', () => {
      i18n.loadTranslations('en-US', { nested: { more: 'Deep' } });
      expect(i18n.t('nested.world')).toBe('World');
      expect(i18n.t('nested.more')).toBe('Deep');
    });
  });
});
