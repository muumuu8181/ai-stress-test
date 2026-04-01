/**
 * Represents a subscription to an Observable.
 */
export interface Subscription {
  /**
   * Cancels the subscription.
   */
  unsubscribe(): void;
}

/**
 * Interface for an observer that can receive values from an Observable.
 */
export interface Observer<T> {
  next(value: T): void;
  error?(err: any): void;
  complete?(): void;
}

/**
 * Type definition for a teardown function returned by an Observable setup.
 */
export type TeardownLogic = (() => void) | Subscription | void;

/**
 * Type definition for an operator function that transforms one Observable into another.
 */
export type OperatorFunction<T, R> = (source: Observable<T>) => Observable<R>;

/**
 * Core Observable class implementing the RxJS-like pattern.
 */
export class Observable<T> {
  private _subscriber?: (observer: Observer<T>) => TeardownLogic;

  /**
   * @param subscribe Function that defines the subscription logic.
   */
  constructor(
    subscribe?: (observer: Observer<T>) => TeardownLogic
  ) {
    if (subscribe) {
      this._subscriber = subscribe;
    }
  }

  /**
   * Internal subscription logic that can be overridden by subclasses.
   */
  protected _subscribe(observer: Observer<T>): TeardownLogic {
    return this._subscriber?.(observer);
  }

  /**
   * Subscribes an observer to this Observable.
   * @param observer The observer or next function.
   * @returns A Subscription object.
   */
  subscribe(observerOrNext: Partial<Observer<T>> | ((value: T) => void)): Subscription {
    let observer: Observer<T>;
    if (typeof observerOrNext === 'function') {
      observer = { next: observerOrNext };
    } else {
      observer = {
        next: (val) => observerOrNext.next?.(val),
        error: (err) => observerOrNext.error?.(err),
        complete: () => observerOrNext.complete?.(),
      };
    }

    let isUnsubscribed = false;
    const safeObserver: Observer<T> = {
      next: (val) => {
        if (!isUnsubscribed) {
          observer.next(val);
        }
      },
      error: (err) => {
        if (!isUnsubscribed) {
          isUnsubscribed = true;
          observer.error?.(err);
        }
      },
      complete: () => {
        if (!isUnsubscribed) {
          isUnsubscribed = true;
          observer.complete?.();
        }
      },
    };

    const teardown = this._subscribe(safeObserver);

    return {
      unsubscribe: () => {
        isUnsubscribed = true;
        if (typeof teardown === 'function') {
          teardown();
        } else if (teardown && typeof teardown.unsubscribe === 'function') {
          teardown.unsubscribe();
        }
      },
    };
  }

  /**
   * Pipes operators to transform the Observable.
   * @param fns Operator functions.
   * @returns A transformed Observable.
   */
  pipe<R>(...fns: Array<OperatorFunction<any, any>>): Observable<R> {
    return fns.reduce((prev, fn) => fn(prev), this) as Observable<R>;
  }

  /**
   * Static creation method to create an Observable from a value.
   */
  static of<T>(...values: T[]): Observable<T> {
    return new Observable<T>((observer) => {
      values.forEach((v) => observer.next(v));
      observer.complete?.();
    });
  }
}
