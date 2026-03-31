# Internationalization (i18n) Toolkit

A comprehensive and lightweight internationalization (i18n) toolkit for TypeScript.

## Features

- **Translation File Management**: Load and merge translation resources easily.
- **Nested Keys**: Support for dot-notated nested keys (e.g., `user.profile.name`).
- **Fallback Chain**: Intelligent fallback mechanism (e.g., `en-US` -> `en` -> `fallback`).
- **Variable Interpolation**: Simple placeholder replacement (e.g., `Hello, {name}!`).
- **Pluralization**: Built-in pluralization support using `Intl.PluralRules`.
- **Date & Number Formatting**: Localized formatting using standard `Intl` APIs.
- **CLI/REPL**: Interactive command-line interface for quick testing.

## Installation

```bash
cd components/036-i18n-tool
npm install
```

## Usage

### Basic Usage

```typescript
import { I18n } from './src/i18n';

const i18n = new I18n({
  defaultLocale: 'en-US',
  fallbackLocale: 'en',
  translations: {
    'en-US': {
      welcome: 'Welcome!',
      greet: 'Hello, {name}!',
    },
    'en': {
      fallback: 'This is a fallback message.',
    }
  },
});

console.log(i18n.t('welcome')); // Welcome!
console.log(i18n.t('greet', { name: 'Jules' })); // Hello, Jules!
console.log(i18n.t('fallback')); // This is a fallback message.
```

### Pluralization

```typescript
const translations = {
  'en-US': {
    apples: {
      one: 'I have {count} apple.',
      other: 'I have {count} apples.',
    }
  }
};

const i18n = new I18n({ defaultLocale: 'en-US', translations });
console.log(i18n.t('apples', { count: 1 })); // I have 1 apple.
console.log(i18n.t('apples', { count: 5 })); // I have 5 apples.
```

### Formatting

```typescript
const i18n = new I18n({ defaultLocale: 'en-US' });

// Date Formatting
console.log(i18n.formatDate(new Date())); // e.g., 5/20/2024

// Number Formatting
console.log(i18n.formatNumber(1234567.89)); // 1,234,567.89

i18n.setLocale('ja-JP');
console.log(i18n.formatDate(new Date())); // 2024/5/20
```

## CLI

You can interact with the toolkit via the CLI:

```bash
npm run cli
```

Available commands:
- `t <key> [name=value ...] [count=N]` - Translate a key
- `locale <lang>` - Set the current locale
- `date [iso-date]` - Format a date
- `number <value>` - Format a number
- `exit` - Exit the CLI

## Development

- `npm test`: Run tests
- `npm run test:coverage`: Run tests with coverage report
- `npm run build`: Compile TypeScript to JavaScript
