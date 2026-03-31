/**
 * Represents a symbol for Fragments.
 */
export const Fragment = Symbol('Fragment');

/**
 * Common properties for VNodes.
 */
export type Props = Record<string, any>;

/**
 * Possible types for a VNode's tag.
 */
export type VNodeType = string | typeof Fragment | ((props: Props, children: VNode[]) => VNode);

/**
 * Represents a Virtual DOM Node.
 */
export interface VNode {
  type: VNodeType;
  props: Props;
  children: VNode[];
  key?: string | number;
  /**
   * Reference to the actual DOM element.
   */
  el?: Node;
}

/**
 * Possible types for children in h() function.
 */
export type VNodeChild = VNode | string | number | boolean | null | undefined | VNodeChild[];

/**
 * Types of patches to be applied to the DOM.
 */
export enum PatchType {
  CREATE = 'CREATE',
  REMOVE = 'REMOVE',
  REPLACE = 'REPLACE',
  UPDATE_PROPS = 'UPDATE_PROPS',
  REORDER_CHILDREN = 'REORDER_CHILDREN',
  TEXT_UPDATE = 'TEXT_UPDATE'
}

/**
 * Represents a patch for updating the DOM.
 */
export interface Patch {
  type: PatchType;
  props?: {
    added: Props;
    removed: string[];
    updated: Props;
  };
  children?: Patch[];
  newVNode?: VNode;
  oldVNode?: VNode;
  text?: string;
  moves?: Move[];
}

/**
 * Represents a child movement in keyed list reconciliation.
 */
export interface Move {
  type: 'INSERT' | 'REMOVE';
  index: number;
  item?: VNode;
}
