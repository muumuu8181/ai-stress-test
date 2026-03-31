import * as readline from 'readline';
import { I18n } from './i18n';

const i18n = new I18n({
  defaultLocale: 'en-US',
  fallbackLocale: 'en',
  translations: {
    'en-US': {
      welcome: 'Welcome to the i18n tool!',
      greeting: 'Hello, {name}!',
      apples: {
        one: 'I have {count} apple.',
        other: 'I have {count} apples.',
      },
    },
    'ja-JP': {
      welcome: 'i18nツールへようこそ！',
      greeting: 'こんにちは、{name}さん！',
      apples: {
        other: '{count}個のりんごがあります。',
      },
    },
  },
});

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: 'i18n > ',
});

console.log('--- Internationalization (i18n) Toolkit CLI ---');
console.log('Available commands:');
console.log('  t <key> [name=value ...] [count=N] - Translate a key');
console.log('  locale <lang>                      - Set the current locale');
console.log('  date [iso-date]                    - Format current or specified date');
console.log('  number <value>                     - Format a number');
console.log('  exit                               - Exit the CLI');
console.log('');
console.log(`Current locale: ${i18n.getLocale()}`);
rl.prompt();

rl.on('line', (line) => {
  const [command, ...args] = line.trim().split(/\s+/);

  switch (command) {
    case 'exit':
      rl.close();
      break;

    case 'locale':
      if (args[0]) {
        i18n.setLocale(args[0]);
        console.log(`Locale set to: ${i18n.getLocale()}`);
      } else {
        console.log(`Current locale: ${i18n.getLocale()}`);
      }
      break;

    case 't':
      if (args[0]) {
        const key = args[0];
        const context: any = {};
        args.slice(1).forEach((arg) => {
          const [k, v] = arg.split('=');
          if (k === 'count') {
            context[k] = Number(v);
          } else {
            context[k] = v;
          }
        });
        console.log(i18n.t(key, context));
      } else {
        console.log('Usage: t <key> [name=value ...] [count=N]');
      }
      break;

    case 'date':
      try {
        const date = args[0] ? new Date(args[0]) : new Date();
        console.log(i18n.formatDate(date, { dateStyle: 'full', timeStyle: 'long' }));
      } catch (e) {
        console.log('Invalid date format.');
      }
      break;

    case 'number':
      if (args[0]) {
        const val = Number(args[0]);
        if (!isNaN(val)) {
          console.log(i18n.formatNumber(val));
        } else {
          console.log('Invalid number.');
        }
      } else {
        console.log('Usage: number <value>');
      }
      break;

    case '':
      break;

    default:
      console.log(`Unknown command: ${command}`);
      break;
  }
  rl.prompt();
}).on('close', () => {
  console.log('Exiting...');
  process.exit(0);
});
