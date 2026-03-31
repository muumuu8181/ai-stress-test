import { describe, it, expect, beforeEach, vi } from 'vitest';
import { h } from '../src/h';
import { render, useState } from '../src/component';
import { JSDOM } from 'jsdom';

describe('functional components', () => {
  let dom: JSDOM;
  let document: Document;

  beforeEach(() => {
    dom = new JSDOM('<!DOCTYPE html><html><body><div id="app"></div></body></html>');
    document = dom.window.document;
    global.document = document;
    global.Node = dom.window.Node;
    global.HTMLElement = dom.window.HTMLElement;
    global.SVGElement = dom.window.SVGElement;
    global.Text = dom.window.Text;
    global.Comment = dom.window.Comment;
    global.DocumentFragment = dom.window.DocumentFragment;
    global.Event = dom.window.Event;
  });

  it('renders a functional component', () => {
    const container = document.getElementById('app')!;
    const MyComponent = ({ name }: { name: string }) => h('div', null, `Hello, ${name}`);
    render(h(MyComponent, { name: 'World' }), container);
    expect(container.textContent).toBe('Hello, World');
  });

  it('handles isolated state for multiple instances', () => {
    const container = document.getElementById('app')!;
    let setA: any;
    let setB: any;

    const Counter = ({ name, set }: { name: string, set: (s: any) => void }) => {
      const [count, setCount] = useState(0);
      set(setCount);
      return h('div', null, `${name}: ${count}`);
    };

    render(h('div', null,
      h(Counter, { name: 'A', set: (s) => setA = s }),
      h(Counter, { name: 'B', set: (s) => setB = s })
    ), container);

    expect(container.textContent).toContain('A: 0');
    expect(container.textContent).toContain('B: 0');

    setA(1);
    expect(container.textContent).toContain('A: 1');
    expect(container.textContent).toContain('B: 0'); // B should still be 0

    setB(2);
    expect(container.textContent).toContain('A: 1');
    expect(container.textContent).toContain('B: 2');
  });

  it('persists state during parent re-renders', () => {
    const container = document.getElementById('app')!;
    let setParentCount: any;
    let setChildCount: any;

    const Child = () => {
      const [count, setCount] = useState(0);
      setChildCount = setCount;
      return h('span', null, `Child: ${count}`);
    };

    const Parent = () => {
      const [count, setCount] = useState(0);
      setParentCount = setCount;
      return h('div', null, `Parent: ${count}`, h(Child));
    };

    render(h(Parent), container);
    expect(container.textContent).toBe('Parent: 0Child: 0');

    setChildCount(5);
    expect(container.textContent).toBe('Parent: 0Child: 5');

    setParentCount(1);
    expect(container.textContent).toBe('Parent: 1Child: 5');
  });

  it('handles event listeners with delegation', () => {
    const container = document.getElementById('app')!;
    const handleClick = vi.fn();
    const Button = () => h('button', { onClick: handleClick }, 'Click me');

    render(h(Button), container);
    const button = container.querySelector('button')!;

    const clickEvent = new (dom.window as any).Event('click', { bubbles: true });
    button.dispatchEvent(clickEvent);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('updates root container when calling render multiple times', () => {
    const container = document.getElementById('app')!;
    render(h('div', null, 'First'), container);
    expect(container.textContent).toBe('First');

    render(h('div', null, 'Second'), container);
    expect(container.textContent).toBe('Second');
    expect(container.childNodes).toHaveLength(1);
  });
});
