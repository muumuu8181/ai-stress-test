# 018-reactive-store

A lightweight, reactive state store built with TypeScript, inspired by RxJS and Redux.

## Features

- **Observable / Observer Pattern**: Core implementation of reactive streams.
- **Rich Operators**: `map`, `filter`, `reduce`, `debounce`, `throttle`.
- **Creation Utilities**: `merge`, `combineLatest`, `Observable.of`.
- **Subjects**: `Subject`, `BehaviorSubject`, `ReplaySubject`.
- **State Store**: Reducer-based state management.
- **Middleware**: Intercept and process actions.
- **Selectors**: Memoized state selectors.
- **Time Travel**: Built-in state history and restoration.

## Installation

```bash
# This is a standalone package
cd components/018-reactive-store
npm install
```

## Usage Examples

### Observable and Operators

```typescript
import { Observable } from './src/observable';
import { map, filter } from './src/operators';

const numbers = Observable.of(1, 2, 3, 4, 5);

numbers.pipe(
  filter(x => x % 2 === 0),
  map(x => x * 10)
).subscribe(val => console.log(val)); // 20, 40
```

### Store with Middleware and Selectors

```typescript
import { Store, Action, Middleware } from './src/store';
import { createSelector } from './src/selector';

interface State { count: number }
const reducer = (state: State, action: Action) => {
  if (action.type === 'inc') return { count: state.count + 1 };
  return state;
};

const logger: Middleware<State> = store => next => action => {
  console.log('Action:', action);
  next(action);
};

const store = new Store(reducer, { count: 0 }, [logger]);

const selectCount = (s: State) => s.count;
const selectDouble = createSelector([selectCount], c => c * 2);

store.state$.subscribe(state => {
  console.log('Current count:', state.count);
  console.log('Double count:', selectDouble(state));
});

store.dispatch({ type: 'inc' });
```

### Time Travel

```typescript
store.dispatch({ type: 'inc' });
const history = store.getHistory();
store.restoreState(0); // Jump back to initial state
```

## Development

### Running Tests

```bash
npm test
npm run test:coverage
```

### Building

```bash
npm run build
```
