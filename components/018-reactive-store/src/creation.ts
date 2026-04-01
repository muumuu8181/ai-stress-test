import { Observable, Observer } from './observable';

/**
 * Merges multiple Observables into a single Observable.
 */
export function merge<T>(...observables: Observable<T>[]): Observable<T> {
  return new Observable<T>((observer) => {
    let completedCount = 0;
    const subscriptions = observables.map((obs) =>
      obs.subscribe({
        next: (val) => observer.next(val),
        error: (err) => {
          subscriptions.forEach((s) => s.unsubscribe());
          observer.error?.(err);
        },
        complete: () => {
          completedCount++;
          if (completedCount === observables.length) {
            observer.complete?.();
          }
        },
      })
    );

    return () => subscriptions.forEach((s) => s.unsubscribe());
  });
}

/**
 * Combines multiple Observables to create an Observable whose values are calculated from the latest values of each.
 */
export function combineLatest<T extends any[]>(...observables: { [K in keyof T]: Observable<T[K]> }): Observable<T> {
  return new Observable<T>((observer) => {
    const latestValues = new Array(observables.length).fill(undefined);
    const hasValue = new Array(observables.length).fill(false);
    let completedCount = 0;

    const subscriptions = (observables as Observable<any>[]).map((obs, index) =>
      obs.subscribe({
        next: (val) => {
          latestValues[index] = val;
          hasValue[index] = true;
          if (hasValue.every((v) => v)) {
            observer.next([...latestValues] as T);
          }
        },
        error: (err) => {
          subscriptions.forEach((s) => s.unsubscribe());
          observer.error?.(err);
        },
        complete: () => {
          completedCount++;
          if (completedCount === observables.length) {
            observer.complete?.();
          }
        },
      })
    );

    return () => subscriptions.forEach((s) => s.unsubscribe());
  });
}
