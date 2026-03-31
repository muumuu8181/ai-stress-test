import { VNode, Patch, PatchType, Props } from './types';

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

  // Handle functional component type updates correctly
  if (typeof oldVNode.type === 'function' && typeof newVNode.type === 'function') {
    if (oldVNode.type !== newVNode.type || oldVNode.key !== newVNode.key) {
      return { type: PatchType.REPLACE, newVNode, oldVNode };
    }

    // Carry over component state if present
    if ((oldVNode as any)._state) {
      (newVNode as any)._state = (oldVNode as any)._state;
      (newVNode as any)._state.vnode = newVNode;
    }

    const propsDiff = diffProps(oldVNode.props, newVNode.props);
    if (propsDiff) {
       // Functional components should re-render on prop changes.
       // We can return a special REPLACE patch that preserves state, or just REPLACE for now.
       return { type: PatchType.REPLACE, newVNode, oldVNode };
    }
    newVNode.el = oldVNode.el;
    return null;
  }

  if (oldVNode.type !== newVNode.type || oldVNode.key !== newVNode.key) {
    return { type: PatchType.REPLACE, newVNode, oldVNode };
  }

  // Preserve DOM reference
  newVNode.el = oldVNode.el;

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
      children: childrenDiff,
      oldVNode
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

function diffChildren(oldChildren: VNode[], newChildren: VNode[]): (Patch | null)[] {
  const patches: (Patch | null)[] = [];

  const oldKeyMap = new Map<string | number, { vnode: VNode, index: number }>();
  oldChildren.forEach((child, i) => {
    if (child.key !== undefined) oldKeyMap.set(child.key, { vnode: child, index: i });
  });

  const maxLength = Math.max(oldChildren.length, newChildren.length);
  const usedOldIndices = new Set<number>();

  for (let i = 0; i < maxLength; i++) {
    const newChild = newChildren[i];
    const oldChildAtIdx = oldChildren[i];

    if (newChild && newChild.key !== undefined) {
      const matchedOld = oldKeyMap.get(newChild.key);
      if (matchedOld) {
        patches[i] = diff(matchedOld.vnode, newChild);
        usedOldIndices.add(matchedOld.index);
      } else {
        patches[i] = diff(undefined, newChild);
      }
    } else {
      if (oldChildAtIdx && oldChildAtIdx.key === undefined && !usedOldIndices.has(i)) {
         patches[i] = diff(oldChildAtIdx, newChild);
         usedOldIndices.add(i);
      } else {
         patches[i] = diff(undefined, newChild);
      }
    }
  }

  return patches;
}
