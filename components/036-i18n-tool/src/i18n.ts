import {
  TranslationResource,
  I18nOptions,
  TranslationContext,
} from './types';

/**
 * Main I18n class for handling translations, pluralization, and formatting.
 */
export class I18n {
  private currentLocale: string;
  private defaultLocale: string;
  private fallbackLocale: string | undefined;
  private translations: Map<string, TranslationResource> = new Map();
  private pluralRules: Map<string, Intl.PluralRules> = new Map();

  /**
   * Initializes the I18n instance.
   * @param options I18n configuration options.
   */
  constructor(options: I18nOptions) {
    this.defaultLocale = this.isValidLocale(options.defaultLocale) ? options.defaultLocale : 'en';
    this.currentLocale = this.defaultLocale;
    this.fallbackLocale = options.fallbackLocale && this.isValidLocale(options.fallbackLocale)
      ? options.fallbackLocale
      : undefined;

    if (options.translations) {
      for (const [locale, resource] of Object.entries(options.translations)) {
        this.loadTranslations(locale, resource);
      }
    }
  }

  /**
   * Validates a locale tag.
   * @param locale Locale tag to validate.
   * @returns True if valid, false otherwise.
   */
  private isValidLocale(locale: string): boolean {
    try {
      Intl.getCanonicalLocales(locale);
      return true;
    } catch (e) {
      return false;
    }
  }

  /**
   * Sets the current locale.
   * @param locale Locale code (e.g., 'en-US').
   */
  setLocale(locale: string): void {
    if (this.isValidLocale(locale)) {
      this.currentLocale = locale;
    }
  }

  /**
   * Gets the current locale.
   * @returns The current locale.
   */
  getLocale(): string {
    return this.currentLocale;
  }

  /**
   * Loads translations for a specific locale.
   * @param locale Locale code.
   * @param resource Translation resource object.
   */
  loadTranslations(locale: string, resource: TranslationResource): void {
    const existing = this.translations.get(locale) || {};
    this.translations.set(locale, this.deepMerge(existing, resource));
  }

  /**
   * Deep merges two translation resources.
   * Merges only own properties and prevents prototype pollution.
   * @param target The target resource.
   * @param source The source resource.
   * @returns The merged resource.
   */
  private deepMerge(target: TranslationResource, source: TranslationResource): TranslationResource {
    // If target is not an object, start with an empty object to avoid spreading strings/primitives
    const result: TranslationResource = (target !== null && typeof target === 'object' && !Array.isArray(target))
      ? { ...target }
      : {};

    const dangerousKeys = ['__proto__', 'constructor', 'prototype'];

    for (const key of Object.keys(source)) {
      if (dangerousKeys.includes(key)) continue;

      const sourceValue = source[key];
      const targetValue = result[key];

      if (
        sourceValue !== null &&
        typeof sourceValue === 'object' &&
        !Array.isArray(sourceValue)
      ) {
        result[key] = this.deepMerge(
          (targetValue as TranslationResource) || {},
          sourceValue as TranslationResource
        );
      } else {
        result[key] = sourceValue;
      }
    }
    return result;
  }

  /**
   * Translates a key with optional context for interpolation and pluralization.
   * @param key Translation key (can be nested using dot notation).
   * @param context Variables for interpolation and/or plural count.
   * @returns The translated string.
   */
  t(key: string, context: TranslationContext = {}): string {
    if (key === null || key === undefined) {
      return key as any;
    }
    const locales = this.getFallbackChain(this.currentLocale);

    for (const locale of locales) {
      const translation = this.resolveKey(locale, key, context);
      if (translation !== undefined) {
        return this.interpolate(translation, context);
      }
    }

    return key;
  }

  /**
   * Generates a fallback chain for a given locale.
   * e.g., 'zh-Hant-TW' -> ['zh-Hant-TW', 'zh-Hant', 'zh', fallbackLocale]
   * @param locale The starting locale.
   * @returns An array of locales to try in order.
   */
  private getFallbackChain(locale: string): string[] {
    const chain: string[] = [];
    let current = locale;

    while (current) {
      chain.push(current);
      const lastDashIndex = current.lastIndexOf('-');
      if (lastDashIndex === -1) break;
      current = current.substring(0, lastDashIndex);
    }

    if (this.fallbackLocale && !chain.includes(this.fallbackLocale)) {
      chain.push(this.fallbackLocale);
    }
    return chain;
  }

  /**
   * Resolves a nested key in a specific locale.
   * @param locale The locale to search in.
   * @param key The key to resolve.
   * @param context Context for pluralization.
   * @returns The resolved string or undefined.
   */
  private resolveKey(locale: string, key: string, context: TranslationContext): string | undefined {
    const resource = this.translations.get(locale);
    if (!resource) return undefined;

    const parts = key.split('.');
    let current: string | TranslationResource | undefined = resource;

    for (const part of parts) {
      if (current === undefined || typeof current === 'string') {
        return undefined;
      }
      current = current[part];
    }

    if (current === undefined) return undefined;

    // Handle pluralization if it's a nested object and count is provided
    if (typeof current === 'object' && context.count !== undefined) {
      const pluralRule = this.getPluralRule(locale);
      const category = pluralRule.select(context.count);

      const pluralized = (current as TranslationResource)[category] || (current as TranslationResource)['other'];
      if (typeof pluralized === 'string') {
        return pluralized;
      }
    }

    return typeof current === 'string' ? current : undefined;
  }

  /**
   * Gets or creates an Intl.PluralRules instance for a locale.
   * @param locale The locale.
   * @returns Intl.PluralRules instance.
   */
  private getPluralRule(locale: string): Intl.PluralRules {
    let rule = this.pluralRules.get(locale);
    if (!rule) {
      rule = new Intl.PluralRules(locale);
      this.pluralRules.set(locale, rule);
    }
    return rule;
  }

  /**
   * Interpolates variables into a string.
   * @param text The string with placeholders (e.g., "Hello {name}").
   * @param variables The variables to inject.
   * @returns The interpolated string.
   */
  private interpolate(text: string, variables: TranslationContext): string {
    return text.replace(/\{(\w+)\}/g, (match, key) => {
      return variables[key] !== undefined ? String(variables[key]) : match;
    });
  }

  /**
   * Formats a date according to the current locale.
   * @param date The date to format.
   * @param options Intl.DateTimeFormatOptions.
   * @returns The formatted date string.
   */
  formatDate(date: Date | number, options?: Intl.DateTimeFormatOptions): string {
    return new Intl.DateTimeFormat(this.currentLocale, options).format(date);
  }

  /**
   * Formats a number according to the current locale.
   * @param value The number to format.
   * @param options Intl.NumberFormatOptions.
   * @returns The formatted number string.
   */
  formatNumber(value: number, options?: Intl.NumberFormatOptions): string {
    return new Intl.NumberFormat(this.currentLocale, options).format(value);
  }
}
