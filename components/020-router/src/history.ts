import { RouterHistory } from './types';

/**
 * Normalizes base path
 */
function normalizeBase(base?: string): string {
  if (!base) return '/';
  if (!base.startsWith('/')) base = '/' + base;
  return base.endsWith('/') ? base.slice(0, -1) : base;
}

/**
 * Base history class
 */
abstract class BaseHistory implements RouterHistory {
  protected listeners: ((to: string) => void)[] = [];
  public readonly base: string;

  constructor(base?: string) {
    this.base = normalizeBase(base);
  }

  abstract get location(): string;
  abstract push(to: string): void;
  abstract replace(to: string): void;
  abstract go(delta: number): void;

  listen(cb: (to: string) => void): () => void {
    this.listeners.push(cb);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== cb);
    };
  }

  protected notify(to: string): void {
    this.listeners.forEach((cb) => cb(to));
  }

  abstract destroy(): void;
}

/**
 * HTML5 History API based history
 */
export class BrowserHistory extends BaseHistory {
  private _popstateHandler: (e: PopStateEvent) => void;

  constructor(base?: string) {
    super(base);
    this._popstateHandler = () => {
      this.notify(this.location);
    };
    window.addEventListener('popstate', this._popstateHandler);
  }

  get location(): string {
    const path = window.location.pathname + window.location.search + window.location.hash;
    if (this.base !== '/' && path.startsWith(this.base)) {
      return path.slice(this.base.length) || '/';
    }
    return path;
  }

  push(to: string): void {
    const fullPath = this.base === '/' ? to : this.base + to;
    window.history.pushState({}, '', fullPath);
    this.notify(to);
  }

  replace(to: string): void {
    const fullPath = this.base === '/' ? to : this.base + to;
    window.history.replaceState({}, '', fullPath);
    this.notify(to);
  }

  go(delta: number): void {
    window.history.go(delta);
  }

  destroy(): void {
    window.removeEventListener('popstate', this._popstateHandler);
    this.listeners = [];
  }
}

/**
 * Hash-based history
 */
export class HashHistory extends BaseHistory {
  private _hashchangeHandler: (e: HashChangeEvent) => void;

  constructor(base?: string) {
    super(base);
    this._hashchangeHandler = () => {
      this.notify(this.location);
    };
    window.addEventListener('hashchange', this._hashchangeHandler);

    // Ensure initial hash
    if (!window.location.hash.startsWith('#/')) {
      window.location.hash = '#/';
    }
  }

  get location(): string {
    const hash = window.location.hash;
    return hash.slice(1) || '/';
  }

  push(to: string): void {
    window.location.hash = to;
    this.notify(to);
  }

  replace(to: string): void {
    const url = new URL(window.location.href);
    url.hash = to;
    window.location.replace(url.href);
    this.notify(to);
  }

  go(delta: number): void {
    window.history.go(delta);
  }

  destroy(): void {
    window.removeEventListener('hashchange', this._hashchangeHandler);
    this.listeners = [];
  }
}
