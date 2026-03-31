import { VNode, VNodeChild, VNodeType, Props, Fragment } from './types';

export { Fragment };

/**
 * Creates a Virtual DOM Node.
 *
 * @param type - The tag name, Fragment, or a functional component.
 * @param props - The properties/attributes for the node.
 * @param children - The child nodes.
 * @returns A VNode object.
 */
export function h(
  type: VNodeType,
  props: Props | null = null,
  ...children: VNodeChild[]
): VNode {
  const normalizedProps: Props = props ? { ...props } : {};
  const key = normalizedProps.key;
  if (key !== undefined) {
    delete normalizedProps.key;
  }

  const flattenedChildren: VNode[] = [];

  function addChildren(child: VNodeChild) {
    if (child === null || child === undefined || typeof child === 'boolean') {
      return;
    }

    if (Array.isArray(child)) {
      child.forEach(addChildren);
    } else if (typeof child === 'string' || typeof child === 'number') {
      flattenedChildren.push({
        type: 'TEXT_NODE',
        props: { nodeValue: String(child) },
        children: []
      });
    } else {
      flattenedChildren.push(child as VNode);
    }
  }

  children.forEach(addChildren);

  return {
    type,
    props: normalizedProps,
    children: flattenedChildren,
    key
  };
}
