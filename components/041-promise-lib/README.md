
# 041-promise-lib

A Promise/A+ compliant library implemented in TypeScript.

## Features

- [x] Promise/A+ compliant `then` method.
- [x] Chaining support.
- [x] `catch` and `finally` instance methods.
- [x] Static methods: `resolve`, `reject`, `all`, `race`, `allSettled`, `any`.
- [x] TypeScript types and JSDoc.

## Usage

```typescript
import { MyPromise } from './src/index';

const p = new MyPromise((resolve, reject) => {
  setTimeout(() => resolve('success!'), 100);
});

p.then(val => console.log(val))
 .catch(err => console.error(err))
 .finally(() => console.log('Done'));

// Static methods
MyPromise.all([p, MyPromise.resolve(42)])
  .then(results => console.log(results));
```

## Running Tests

To run the unit tests:

```bash
npm test
```

To run the Promise/A+ compliance tests:

```bash
# First build the source
npm run build
# Then run the compliance tests
npx promises-aplus-tests tests/adapter.cjs
```

To see the test coverage:

```bash
npm test -- --coverage
```

## Running the Example

```bash
npx ts-node src/example.ts
```
