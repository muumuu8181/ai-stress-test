/**
 * Translation resource structure.
 * Supports nested keys.
 */
export interface TranslationResource {
  [key: string]: string | TranslationResource;
}

/**
 * Options for the I18n class.
 */
export interface I18nOptions {
  /**
   * The default locale to use.
   */
  defaultLocale: string;
  /**
   * Fallback locale if a key is not found in the current locale.
   */
  fallbackLocale?: string;
  /**
   * Initial translations to load.
   */
  translations?: Record<string, TranslationResource>;
}

/**
 * Pluralization rules function.
 * Returns the plural category (e.g., 'zero', 'one', 'two', 'few', 'many', 'other').
 */
export type PluralRule = (count: number) => Intl.LDMLPluralRule;

/**
 * Variables for interpolation.
 */
export interface TranslationVariables {
  [key: string]: string | number;
}

/**
 * Context for translation.
 */
export interface TranslationContext {
  [key: string]: string | number | undefined;
  count?: number;
}
