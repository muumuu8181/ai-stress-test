import { Observable, OperatorFunction } from './observable';

/**
 * Transforms each value emitted by the source Observable.
 */
export function map<T, R>(project: (value: T, index: number) => R): OperatorFunction<T, R> {
  return (source: Observable<T>) => {
    return new Observable<R>((observer) => {
      let index = 0;
      return source.subscribe({
        next: (val) => observer.next(project(val, index++)),
        error: (err) => observer.error?.(err),
        complete: () => observer.complete?.(),
      });
    });
  };
}

/**
 * Filter values emitted by the source Observable.
 */
export function filter<T>(predicate: (value: T, index: number) => boolean): OperatorFunction<T, T> {
  return (source: Observable<T>) => {
    return new Observable<T>((observer) => {
      let index = 0;
      return source.subscribe({
        next: (val) => {
          if (predicate(val, index++)) {
            observer.next(val);
          }
        },
        error: (err) => observer.error?.(err),
        complete: () => observer.complete?.(),
      });
    });
  };
}

/**
 * Applies an accumulator function over the source Observable.
 */
export function reduce<T, R>(accumulator: (acc: R, value: T, index: number) => R, seed: R): OperatorFunction<T, R> {
  return (source: Observable<T>) => {
    return new Observable<R>((observer) => {
      let acc = seed;
      let index = 0;
      return source.subscribe({
        next: (val) => {
          acc = accumulator(acc, val, index++);
        },
        error: (err) => observer.error?.(err),
        complete: () => {
          observer.next(acc);
          observer.complete?.();
        },
      });
    });
  };
}

/**
 * Emits a value from the source Observable only after a particular time span has passed without another source emission.
 */
export function debounce<T>(duration: number): OperatorFunction<T, T> {
  return (source: Observable<T>) => {
    return new Observable<T>((observer) => {
      let timeoutId: any = null;
      let lastValue: T;
      let hasValue = false;

      const subscription = source.subscribe({
        next: (val) => {
          if (timeoutId !== null) {
            clearTimeout(timeoutId);
          }
          lastValue = val;
          hasValue = true;
          timeoutId = setTimeout(() => {
            observer.next(lastValue);
            timeoutId = null;
          }, duration);
        },
        error: (err) => {
          if (timeoutId !== null) clearTimeout(timeoutId);
          observer.error?.(err);
        },
        complete: () => {
          if (timeoutId !== null) {
            clearTimeout(timeoutId);
            if (hasValue) {
              observer.next(lastValue);
            }
          }
          observer.complete?.();
        },
      });

      return () => {
        if (timeoutId !== null) clearTimeout(timeoutId);
        subscription.unsubscribe();
      };
    });
  };
}

/**
 * Emits a value from the source Observable, then ignores subsequent source values for a duration.
 */
export function throttle<T>(duration: number): OperatorFunction<T, T> {
  return (source: Observable<T>) => {
    return new Observable<T>((observer) => {
      let lastEmissionTime = 0;

      return source.subscribe({
        next: (val) => {
          const now = Date.now();
          if (now - lastEmissionTime >= duration) {
            lastEmissionTime = now;
            observer.next(val);
          }
        },
        error: (err) => observer.error?.(err),
        complete: () => observer.complete?.(),
      });
    });
  };
}
