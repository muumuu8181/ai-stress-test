import { describe, it, expect } from 'vitest';
import { h, Fragment } from '../src/h';

describe('h function', () => {
  it('creates a simple element', () => {
    const vnode = h('div', { id: 'test' }, 'hello');
    expect(vnode.type).toBe('div');
    expect(vnode.props).toEqual({ id: 'test' });
    expect(vnode.children).toHaveLength(1);
    expect(vnode.children[0].type).toBe('TEXT_NODE');
    expect(vnode.children[0].props.nodeValue).toBe('hello');
  });

  it('handles multiple children', () => {
    const vnode = h('ul', null,
      h('li', null, 'item 1'),
      h('li', null, 'item 2')
    );
    expect(vnode.children).toHaveLength(2);
    expect(vnode.children[0].type).toBe('li');
  });

  it('handles fragments', () => {
    const vnode = h(Fragment, null, h('div', null, '1'), h('div', null, '2'));
    expect(vnode.type).toBe(Fragment);
    expect(vnode.children).toHaveLength(2);
  });

  it('flattens array children', () => {
    const vnode = h('div', null, [h('span', null, 'a'), h('span', null, 'b')]);
    expect(vnode.children).toHaveLength(2);
    expect(vnode.children[0].type).toBe('span');
  });

  it('handles nested array children', () => {
    const vnode = h('div', null, [h('span', null, 'a'), [h('span', null, 'b'), h('span', null, 'c')]]);
    expect(vnode.children).toHaveLength(3);
  });

  it('skips null/undefined/boolean children', () => {
    const vnode = h('div', null, 'text', null, undefined, true, false, h('span'));
    expect(vnode.children).toHaveLength(2);
    expect(vnode.children[0].props.nodeValue).toBe('text');
    expect(vnode.children[1].type).toBe('span');
  });

  it('extracts key from props', () => {
    const vnode = h('div', { key: 'my-key', id: 'my-id' });
    expect(vnode.key).toBe('my-key');
    expect(vnode.props.key).toBeUndefined();
    expect(vnode.props.id).toBe('my-id');
  });
});
