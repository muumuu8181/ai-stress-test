/**
 * Parameters for a route, e.g., { id: '123' } for /users/:id
 */
export type RouteParams = Record<string, string>;

/**
 * Query parameters for a route, e.g., { q: 'search' } for ?q=search
 */
export type RouteQuery = Record<string, string | (string | null)[] | null>;

/**
 * Represents a resolved route
 */
export interface Route {
  /**
   * The matched path pattern
   */
  path: string;
  /**
   * The full resolved path with filled params and query
   */
  fullPath: string;
  /**
   * Path parameters
   */
  params: RouteParams;
  /**
   * Query parameters
   */
  query: RouteQuery;
  /**
   * URL hash
   */
  hash: string;
  /**
   * Route name if defined
   */
  name?: string;
  /**
   * Meta information
   */
  meta?: any;
  /**
   * List of matched route records (for nested routes)
   */
  matched: RouteRecord[];
}

/**
 * Result of a navigation guard
 */
export type NavigationGuardNext = (to?: string | false | { path: string }) => void;

/**
 * Navigation guard function
 */
export type NavigationGuard = (
  to: Route,
  from: Route | null,
  next: NavigationGuardNext
) => void | Promise<void>;

/**
 * Route definition record
 */
export interface RouteRecord {
  /**
   * Path pattern, e.g., '/users/:id'
   */
  path: string;
  /**
   * Optional name for the route
   */
  name?: string;
  /**
   * Nested child routes
   */
  children?: RouteRecord[];
  /**
   * Redirect path or function
   */
  redirect?: string | ((to: Route) => string);
  /**
   * Custom meta information
   */
  meta?: any;
  /**
   * Per-route navigation guard
   */
  beforeEnter?: NavigationGuard;
  /**
   * Component or any data associated with the route
   */
  component?: any;
}

/**
 * Router configuration options
 */
export interface RouterOptions {
  /**
   * Route definitions
   */
  routes: RouteRecord[];
  /**
   * Routing mode: 'history' (HTML5 History API) or 'hash'
   * @default 'history'
   */
  mode?: 'history' | 'hash';
  /**
   * Base path for the application
   * @default '/'
   */
  base?: string;
}

/**
 * Abstract interface for history management
 */
export interface RouterHistory {
  /**
   * Current location path
   */
  readonly location: string;
  /**
   * Base path
   */
  readonly base: string;
  /**
   * Navigate to a new URL
   */
  push(to: string): void;
  /**
   * Replace current URL
   */
  replace(to: string): void;
  /**
   * Move back or forward in history
   */
  go(delta: number): void;
  /**
   * Listen for location changes
   * @returns unsubscribe function
   */
  listen(cb: (to: string) => void): () => void;
  /**
   * Clean up listeners
   */
  destroy(): void;
}
