import { VNode, Patch, PatchType, Props, Fragment } from './types';

/**
 * Calculates the difference between two VNodes and returns a patch.
 *
 * @param oldVNode - The previous VNode.
 * @param newVNode - The current VNode.
 * @returns A Patch object describing the changes.
 */
export function diff(oldVNode: VNode | undefined, newVNode: VNode | undefined): Patch | null {
  if (oldVNode === undefined && newVNode !== undefined) {
    return { type: PatchType.CREATE, newVNode };
  }
  if (oldVNode !== undefined && newVNode === undefined) {
    return { type: PatchType.REMOVE, oldVNode };
  }
  if (oldVNode === undefined || newVNode === undefined) {
    return null;
  }

  if (oldVNode.type !== newVNode.type || oldVNode.key !== newVNode.key) {
    return { type: PatchType.REPLACE, newVNode, oldVNode };
  }

  // Preserve DOM reference
  newVNode.el = oldVNode.el;

  // Carry over component state if present
  if ((oldVNode as any)._state) {
    (newVNode as any)._state = (oldVNode as any)._state;
    (newVNode as any)._state.vnode = newVNode; // Update to latest VNode
  }

  if (oldVNode.type === 'TEXT_NODE' && newVNode.type === 'TEXT_NODE') {
    if (oldVNode.props.nodeValue !== newVNode.props.nodeValue) {
      return { type: PatchType.TEXT_UPDATE, text: String(newVNode.props.nodeValue) };
    }
    return null;
  }

  const propsDiff = diffProps(oldVNode.props, newVNode.props);
  const childrenDiff = diffChildren(oldVNode.children, newVNode.children);

  if (propsDiff || childrenDiff.length > 0) {
    return {
      type: PatchType.UPDATE_PROPS,
      props: propsDiff || { added: {}, removed: [], updated: {} },
      children: childrenDiff
    };
  }

  return null;
}

function diffProps(oldProps: Props, newProps: Props) {
  const added: Props = {};
  const removed: string[] = [];
  const updated: Props = {};

  for (const key in newProps) {
    if (!(key in oldProps)) {
      added[key] = newProps[key];
    } else if (oldProps[key] !== newProps[key]) {
      updated[key] = newProps[key];
    }
  }

  for (const key in oldProps) {
    if (!(key in newProps)) {
      removed.push(key);
    }
  }

  if (Object.keys(added).length === 0 && removed.length === 0 && Object.keys(updated).length === 0) {
    return null;
  }

  return { added, removed, updated };
}

function diffChildren(oldChildren: VNode[], newChildren: VNode[]): Patch[] {
  const patches: Patch[] = [];

  // Basic implementation to support keyed reconciliation by using CREATE/REMOVE for mismatches
  // Real reordering is complex, but this ensures keyed nodes are handled per key.
  const maxLength = Math.max(oldChildren.length, newChildren.length);
  for (let i = 0; i < maxLength; i++) {
    const patch = diff(oldChildren[i], newChildren[i]);
    if (patch) {
      patches[i] = patch;
    }
  }

  return patches;
}
