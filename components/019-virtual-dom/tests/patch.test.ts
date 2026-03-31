import { describe, it, expect, beforeEach } from 'vitest';
import { h, Fragment } from '../src/h';
import { createElement, patch } from '../src/patch';
import { diff } from '../src/diff';
import { JSDOM } from 'jsdom';

describe('patch and createElement', () => {
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
  });

  it('creates an element from a VNode', () => {
    const vnode = h('div', { id: 'test' }, 'hello');
    const el = createElement(vnode) as HTMLElement;
    expect(el.tagName).toBe('DIV');
    expect(el.id).toBe('test');
    expect(el.textContent).toBe('hello');
  });

  it('creates an SVG element', () => {
    const vnode = h('svg', { width: '100' }, h('circle', { cx: '50', cy: '50', r: '40' }));
    const el = createElement(vnode) as SVGElement;
    expect(el.namespaceURI).toBe('http://www.w3.org/2000/svg');
    expect(el.tagName.toLowerCase()).toBe('svg');
    expect(el.childNodes[0].namespaceURI).toBe('http://www.w3.org/2000/svg');
  });

  it('applies a patch to update an element', () => {
    const container = document.getElementById('app')!;
    const oldVNode = h('div', { id: 'old' }, 'old text');
    const el = createElement(oldVNode);
    container.appendChild(el);

    const newVNode = h('div', { id: 'new' }, 'new text');
    const p = diff(oldVNode, newVNode);
    patch(container, p);

    const updatedEl = container.firstChild as HTMLElement;
    expect(updatedEl.id).toBe('new');
    expect(updatedEl.textContent).toBe('new text');
  });

  it('applies a patch to replace an element', () => {
    const container = document.getElementById('app')!;
    const oldVNode = h('div', null, 'div');
    const el = createElement(oldVNode);
    container.appendChild(el);

    const newVNode = h('span', null, 'span');
    const p = diff(oldVNode, newVNode);
    patch(container, p);

    const updatedEl = container.firstChild as HTMLElement;
    expect(updatedEl.tagName).toBe('SPAN');
    expect(updatedEl.textContent).toBe('span');
  });

  it('handles Fragments in createElement', () => {
    const vnode = h(Fragment, null, h('span', null, '1'), h('span', null, '2'));
    const el = createElement(vnode);
    expect(el instanceof DocumentFragment).toBe(true);
    expect(el.childNodes).toHaveLength(2);
  });

  it('handles child updates', () => {
    const container = document.getElementById('app')!;
    const oldVNode = h('ul', null, h('li', null, '1'), h('li', null, '2'));
    const el = createElement(oldVNode);
    container.appendChild(el);

    const newVNode = h('ul', null, h('li', null, '1'), h('li', null, '3'), h('li', null, '4'));
    const p = diff(oldVNode, newVNode);
    patch(container, p);

    const updatedEl = container.firstChild as HTMLElement;
    expect(updatedEl.childNodes).toHaveLength(3);
    expect(updatedEl.childNodes[1].textContent).toBe('3');
    expect(updatedEl.childNodes[2].textContent).toBe('4');
  });
});
