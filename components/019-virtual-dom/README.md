# 019-virtual-dom

A lightweight Virtual DOM engine written in TypeScript with no external dependencies (for production).

## Features

- [x] **h function**: Create Virtual DOM nodes.
- [x] **Fragment support**: Group elements without a wrapper.
- [x] **Diff algorithm**: Efficiently calculate changes between Virtual DOM trees.
- [x] **Patch mechanism**: Apply patches to the real DOM.
- [x] **SVG Support**: Correct rendering of SVG elements and namespaces.
- [x] **Functional Components**: Support for functional components with state.
- [x] **useState hook**: Simple state management within functional components.
- [x] **Event delegation**: Handle events (e.g., `onClick`).

## Installation

```bash
cd components/019-virtual-dom
npm install
```

## Usage

### Simple rendering

```typescript
import { h, render } from './src';

const vnode = h('div', { id: 'root' },
  h('h1', null, 'Hello, Virtual DOM!'),
  h('p', null, 'This is a lightweight VDOM engine.')
);

render(vnode, document.body);
```

### Functional Component with State

```typescript
import { h, render, useState } from './src';

const Counter = () => {
  const [count, setCount] = useState(0);

  return h('div', null,
    h('p', null, `Count: ${count}`),
    h('button', { onClick: () => setCount(count + 1) }, 'Increment')
  );
};

render(h(Counter), document.getElementById('app'));
```

### Fragments

```typescript
import { h, Fragment } from './src';

const List = () => (
  h(Fragment, null,
    h('li', null, 'Item 1'),
    h('li', null, 'Item 2')
  )
);
```

### SVG Support

```typescript
const Icon = () => (
  h('svg', { width: '20', height: '20' },
    h('circle', { cx: '10', cy: '10', r: '5', fill: 'red' })
  )
);
```

## Development

### Run tests

```bash
npm test
```

### Run tests with coverage

```bash
npm test -- --coverage
```
