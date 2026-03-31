import { VNode, Props } from './types';
import { diff } from './diff';
import { patch, createElement } from './patch';

/**
 * Functional component state.
 */
interface ComponentState {
  states: any[];
  vnode: VNode;
  isSVG: boolean;
  renderedVNode?: VNode;
}

let currentComponentState: ComponentState | null = null;
let currentHookIndex = 0;

/**
 * Simple hook for state management in functional components.
 */
export function useState<T>(initialState: T): [T, (newState: T | ((prev: T) => T)) => void] {
  if (!currentComponentState) {
    throw new Error('useState must be called inside a functional component');
  }

  const state = currentComponentState;
  const i = currentHookIndex++;

  if (state.states[i] === undefined) {
    state.states[i] = initialState;
  }

  const setState = (newState: T | ((prev: T) => T)) => {
    const val = typeof newState === 'function' ? (newState as Function)(state.states[i]) : newState;
    if (state.states[i] !== val) {
      state.states[i] = val;
      updateComponent(state);
    }
  };

  return [state.states[i], setState];
}

/**
 * Renders a functional component and returns its DOM node.
 */
export function renderComponent(vnode: VNode, isSVG = false): Node {
  // To ensure isolated state per instance, we store the state on the VNode's _state property.
  // This state must be carried over when the VNode is updated (in diff/patch).
  let state: ComponentState = (vnode as any)._state;
  if (!state) {
    state = {
      states: [],
      vnode,
      isSVG
    };
    (vnode as any)._state = state;
  }
  state.vnode = vnode;

  const previousState = currentComponentState;
  const previousHookIndex = currentHookIndex;

  currentComponentState = state;
  currentHookIndex = 0;

  const renderedVNode = (vnode.type as Function)(vnode.props, vnode.children);
  state.renderedVNode = renderedVNode;

  currentComponentState = previousState;
  currentHookIndex = previousHookIndex;

  const el = createElement(renderedVNode, isSVG);
  vnode.el = el;
  return el;
}

function updateComponent(state: ComponentState): void {
  const oldVNode = state.renderedVNode!;

  const previousState = currentComponentState;
  const previousHookIndex = currentHookIndex;

  currentComponentState = state;
  currentHookIndex = 0;

  const newVNode = (state.vnode.type as Function)(state.vnode.props, state.vnode.children);
  state.renderedVNode = newVNode;

  currentComponentState = previousState;
  currentHookIndex = previousHookIndex;

  const p = diff(oldVNode, newVNode);
  if (p) {
    const el = oldVNode.el;
    const parent = el?.parentNode;
    if (parent) {
      const index = Array.prototype.indexOf.call(parent.childNodes, el);
      if (index !== -1) {
        patch(parent, p, index);
        // Ensure the new element is tracked if it was replaced
        state.vnode.el = parent.childNodes[index];
      }
    }
  }
}

/**
 * Main entry point to mount or update the Virtual DOM in a container.
 */
let rootVNodeMap = new Map<Node, VNode>();

export function render(vnode: VNode, container: Node): void {
  const oldVNode = rootVNodeMap.get(container);
  if (oldVNode) {
    const p = diff(oldVNode, vnode);
    if (p) {
      patch(container, p);
    }
  } else {
    const el = createElement(vnode);
    container.appendChild(el);
  }
  rootVNodeMap.set(container, vnode);
}
