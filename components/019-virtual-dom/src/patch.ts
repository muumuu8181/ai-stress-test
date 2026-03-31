import { VNode, Patch, PatchType, Fragment } from './types';
import { updateEvents } from './events';
import { renderComponent } from './component';

const SVG_NS = 'http://www.w3.org/2000/svg';

/**
 * Creates a real DOM node from a VNode.
 *
 * @param vnode - The Virtual DOM Node.
 * @param isSVG - Whether the current context is SVG.
 * @returns A real DOM Node.
 */
export function createElement(vnode: VNode, isSVG = false): Node {
  if (vnode.type === 'TEXT_NODE') {
    const el = document.createTextNode(vnode.props.nodeValue);
    vnode.el = el;
    return el;
  }

  if (vnode.type === Fragment) {
    const el = document.createDocumentFragment();
    vnode.children.forEach(child => {
      el.appendChild(createElement(child, isSVG));
    });
    vnode.el = el;
    return el;
  }

  if (typeof vnode.type === 'function') {
    const el = renderComponent(vnode, isSVG);
    vnode.el = el;
    return el;
  }

  const tag = vnode.type as string;
  const currentIsSVG = isSVG || tag === 'svg';
  const el = currentIsSVG
    ? document.createElementNS(SVG_NS, tag)
    : document.createElement(tag);

  vnode.el = el;

  for (const [key, value] of Object.entries(vnode.props)) {
    applyProp(el as HTMLElement, key, value, null, currentIsSVG);
  }

  vnode.children.forEach(child => {
    el.appendChild(createElement(child, currentIsSVG));
  });

  return el;
}

/**
 * Applies a single property to a DOM element.
 */
export function applyProp(el: HTMLElement | SVGElement, key: string, value: any, oldValue: any, isSVG: boolean) {
  if (key.startsWith('on')) {
    updateEvents(el, key.toLowerCase().slice(2), value, oldValue);
  } else if (key === 'style' && typeof value === 'object') {
    const style = (el as HTMLElement).style;
    if (oldValue && typeof oldValue === 'object') {
      for (const s in oldValue) {
        if (!(s in value)) (style as any)[s] = '';
      }
    }
    for (const s in value) {
      (style as any)[s] = value[s];
    }
  } else if (key === 'className') {
    if (isSVG) {
      el.setAttribute('class', value || '');
    } else {
      (el as HTMLElement).className = value || '';
    }
  } else if (value === false || value === null || value === undefined) {
    el.removeAttribute(key);
  } else {
    if (isSVG) {
      el.setAttribute(key, value);
    } else {
      (el as any)[key] = value;
      if (typeof value !== 'object' && typeof value !== 'function') {
        el.setAttribute(key, value);
      }
    }
  }
}

/**
 * Applies a patch to the real DOM.
 *
 * @param parent - The parent DOM element.
 * @param patchObj - The patch to apply.
 * @param index - The index of the child node in the parent.
 */
export function patch(parent: Node, patchObj: Patch | null, index = 0): void {
  if (!patchObj) return;

  const child = parent.childNodes[index];

  switch (patchObj.type) {
    case PatchType.CREATE: {
      if (patchObj.newVNode) {
        const el = createElement(patchObj.newVNode);
        if (index >= parent.childNodes.length) {
          parent.appendChild(el);
        } else {
          parent.insertBefore(el, parent.childNodes[index]);
        }
      }
      break;
    }
    case PatchType.REMOVE: {
      if (child) {
        parent.removeChild(child);
      }
      break;
    }
    case PatchType.REPLACE: {
      if (patchObj.newVNode && child) {
        parent.replaceChild(createElement(patchObj.newVNode), child);
      }
      break;
    }
    case PatchType.TEXT_UPDATE: {
      if (child && patchObj.text !== undefined) {
        child.nodeValue = patchObj.text;
      }
      break;
    }
    case PatchType.UPDATE_PROPS: {
      const el = child as HTMLElement;
      if (!el) return;
      const { props, children } = patchObj;
      const isSVG = el instanceof SVGElement;

      if (props) {
        props.removed.forEach(key => {
          el.removeAttribute(key);
          if (key.startsWith('on')) updateEvents(el, key.toLowerCase().slice(2), null, null);
        });
        const allUpdates = { ...props.added, ...props.updated };
        for (const [key, value] of Object.entries(allUpdates)) {
          applyProp(el, key, value, null, isSVG);
        }
      }

      if (children) {
        let offset = 0;
        children.forEach((childPatch, i) => {
          if (!childPatch) return;
          patch(el, childPatch, i + offset);
          if (childPatch.type === PatchType.REMOVE) {
            offset--;
          } else if (childPatch.type === PatchType.CREATE) {
            offset++;
          }
        });
      }
      break;
    }
  }
}
