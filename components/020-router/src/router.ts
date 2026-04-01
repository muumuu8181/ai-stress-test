import { RouterOptions, Route, NavigationGuard, RouterHistory } from './types';
import { RouterMatcher } from './matcher';
import { BrowserHistory, HashHistory } from './history';

/**
 * Main Router class
 */
export class Router {
  public currentRoute: Route | null = null;
  private matcher: RouterMatcher;
  private history: RouterHistory;
  private beforeGuards: NavigationGuard[] = [];
  private afterGuards: ((to: Route, from: Route | null) => void)[] = [];

  constructor(options: RouterOptions) {
    this.matcher = new RouterMatcher(options.routes);
    this.history =
      options.mode === 'hash'
        ? new HashHistory(options.base)
        : new BrowserHistory(options.base);

    this.history.listen((to) => {
      this.transitionTo(to);
    });

    // Initial transition
    this.transitionTo(this.history.location, true);
  }

  /**
   * Navigate to a new URL
   * @param to - Target URL
   */
  public push(to: string): void {
    this.transitionTo(to, false, (route) => {
      this.history.push(to);
    });
  }

  /**
   * Replace current URL
   * @param to - Target URL
   */
  public replace(to: string): void {
    this.transitionTo(to, false, (route) => {
      this.history.replace(to);
    });
  }

  /**
   * Move back or forward in history
   */
  public go(delta: number): void {
    this.history.go(delta);
  }

  /**
   * Add a global before-each guard
   */
  public beforeEach(guard: NavigationGuard): () => void {
    this.beforeGuards.push(guard);
    return () => {
      this.beforeGuards = this.beforeGuards.filter((g) => g !== guard);
    };
  }

  /**
   * Add a global after-each hook
   */
  public afterEach(hook: (to: Route, from: Route | null) => void): () => void {
    this.afterGuards.push(hook);
    return () => {
      this.afterGuards = this.afterGuards.filter((h) => h !== hook);
    };
  }

  /**
   * Internal method to handle route transitions
   */
  private async transitionTo(
    to: string,
    isInitial: boolean = false,
    onComplete?: (route: Route | null) => void
  ): Promise<void> {
    let route = this.matcher.match(to);

    // 404 Fallback - if no route matched, we could potentially have a fallback route
    // but for now, we just stay with a null or empty route if not found.
    // In a real router, users often define a '*' route.

    if (!route) {
      // Check if there is a '*' route defined
      route = this.matcher.match('*') || null;
    }

    if (route && route.matched.length > 0) {
      const lastMatch = route.matched[route.matched.length - 1];
      if (lastMatch.redirect) {
        const redirectPath =
          typeof lastMatch.redirect === 'function'
            ? lastMatch.redirect(route)
            : lastMatch.redirect;
        this.replace(redirectPath);
        return;
      }
    }

    // Run guards
    const guards = [...this.beforeGuards];
    // Add per-route guards
    if (route) {
      route.matched.forEach((record) => {
        if (record.beforeEnter) {
          guards.push(record.beforeEnter);
        }
      });
    }

    const iterator = async (index: number) => {
      if (index >= guards.length) {
        this.finalizeTransition(route, onComplete);
        return;
      }

      const guard = guards[index];
      await guard(route!, this.currentRoute, (nextArg) => {
        if (nextArg === false) {
          // Abort navigation
          if (!isInitial) {
            // If it's not initial, we might need to revert URL, but history.listen
            // usually triggers AFTER URL change in some cases.
            // Simplified: just don't update state.
          }
        } else if (typeof nextArg === 'string' || (nextArg && typeof nextArg === 'object' && nextArg.path)) {
          // Redirect
          const path = typeof nextArg === 'string' ? nextArg : nextArg.path;
          this.push(path);
        } else {
          iterator(index + 1);
        }
      });
    };

    if (route) {
      await iterator(0);
    } else {
      // Handle 404 - no route found and no '*' fallback
      this.finalizeTransition(null, onComplete);
    }
  }

  private finalizeTransition(route: Route | null, onComplete?: (route: Route | null) => void): void {
    const prevRoute = this.currentRoute;
    this.currentRoute = route;

    if (onComplete) {
      onComplete(route);
    }

    if (route) {
      this.afterGuards.forEach((hook) => hook(route, prevRoute));
    }
  }

  /**
   * Clean up
   */
  public destroy(): void {
    this.history.destroy();
    this.beforeGuards = [];
    this.afterGuards = [];
  }
}
