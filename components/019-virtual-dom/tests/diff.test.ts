import { describe, it, expect } from 'vitest';
import { h } from '../src/h';
import { diff } from '../src/diff';
import { PatchType } from '../src/types';

describe('diff algorithm', () => {
  it('returns CREATE patch if oldVNode is undefined', () => {
    const vnode = h('div');
    const patch = diff(undefined, vnode);
    expect(patch?.type).toBe(PatchType.CREATE);
    expect(patch?.newVNode).toBe(vnode);
  });

  it('returns REMOVE patch if newVNode is undefined', () => {
    const vnode = h('div');
    const patch = diff(vnode, undefined);
    expect(patch?.type).toBe(PatchType.REMOVE);
    expect(patch?.oldVNode).toBe(vnode);
  });

  it('returns REPLACE patch if tags are different', () => {
    const oldVNode = h('div');
    const newVNode = h('span');
    const patch = diff(oldVNode, newVNode);
    expect(patch?.type).toBe(PatchType.REPLACE);
    expect(patch?.newVNode).toBe(newVNode);
  });

  it('returns REPLACE patch if keys are different', () => {
    const oldVNode = h('div', { key: 'a' });
    const newVNode = h('div', { key: 'b' });
    const patch = diff(oldVNode, newVNode);
    expect(patch?.type).toBe(PatchType.REPLACE);
    expect(patch?.newVNode).toBe(newVNode);
  });

  it('returns TEXT_UPDATE patch if text nodes have different values', () => {
    const oldVNode = h('div', null, 'hello');
    const newVNode = h('div', null, 'world');
    const patch = diff(oldVNode.children[0], newVNode.children[0]);
    expect(patch?.type).toBe(PatchType.TEXT_UPDATE);
    expect(patch?.text).toBe('world');
  });

  it('returns UPDATE_PROPS patch if props are different', () => {
    const oldVNode = h('div', { id: 'old', className: 'foo' });
    const newVNode = h('div', { id: 'new', className: 'foo', title: 'test' });
    const patch = diff(oldVNode, newVNode);
    expect(patch?.type).toBe(PatchType.UPDATE_PROPS);
    expect(patch?.props?.added).toEqual({ title: 'test' });
    expect(patch?.props?.updated).toEqual({ id: 'new' });
    expect(patch?.props?.removed).toEqual([]);
  });

  it('detects removed props', () => {
    const oldVNode = h('div', { id: 'old', className: 'foo' });
    const newVNode = h('div', { id: 'old' });
    const patch = diff(oldVNode, newVNode);
    expect(patch?.props?.removed).toEqual(['className']);
  });

  it('diffs children and preserves keyed identity', () => {
    const oldVNode = h('ul', null, h('li', { key: '1' }, '1'), h('li', { key: '2' }, '2'));
    const newVNode = h('ul', null, h('li', { key: '1' }, '1'), h('li', { key: '3' }, '3'), h('li', { key: '2' }, '2'));
    const patchObj = diff(oldVNode, newVNode);

    // index 1: new key '3' is not in old. Expect CREATE.
    expect(patchObj?.children![1].type).toBe(PatchType.CREATE);
    // index 2: new key '2' was at old index 1. Expect UPDATE_PROPS (matching key).
    expect(patchObj?.children![2].type).toBe(PatchType.UPDATE_PROPS);
  });
});
