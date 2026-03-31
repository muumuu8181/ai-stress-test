
/**
 * Promise/A+ Implementation in TypeScript
 */

type State = 'pending' | 'fulfilled' | 'rejected';

type Resolve<T> = (value: T | PromiseLike<T>) => void;
type Reject = (reason?: any) => void;
type Executor<T> = (resolve: Resolve<T>, reject: Reject) => void;

/**
 * Standard Promise AggregateError fallback
 */
class MyAggregateError extends Error {
  constructor(public errors: any[], message?: string) {
    super(message || 'All promises were rejected');
    this.name = 'AggregateError';
  }
}

export class MyPromise<T> {
  private state: State = 'pending';
  private value?: T;
  private reason?: any;
  private onFulfilledCallbacks: Array<() => void> = [];
  private onRejectedCallbacks: Array<() => void> = [];

  /**
   * MyPromise constructor
   * @param executor - A function that is passed with resolve and reject functions
   */
  constructor(executor: Executor<T>) {
    const fulfill = (value: T) => {
      if (this.state === 'pending') {
        this.state = 'fulfilled';
        this.value = value;
        this.onFulfilledCallbacks.forEach((cb) => cb());
      }
    };

    const reject: Reject = (reason) => {
      if (this.state === 'pending') {
        this.state = 'rejected';
        this.reason = reason;
        this.onRejectedCallbacks.forEach((cb) => cb());
      }
    };

    const resolve: Resolve<T> = (value) => {
      resolvePromise(this, value, fulfill, reject);
    };

    try {
      executor(resolve, reject);
    } catch (error) {
      reject(error);
    }
  }

  /**
   * then method according to Promise/A+ spec
   * @param onFulfilled - Callback to execute when the promise is fulfilled
   * @param onRejected - Callback to execute when the promise is rejected
   * @returns A new MyPromise
   */
  then<TResult1 = T, TResult2 = never>(
    onFulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | undefined | null,
    onRejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | undefined | null
  ): MyPromise<TResult1 | TResult2> {
    const promise2 = new MyPromise<TResult1 | TResult2>((resolve, reject) => {
      const fulfilledTask = () => {
        queueMicrotask(() => {
          try {
            if (typeof onFulfilled !== 'function') {
              resolve(this.value as any);
            } else {
              const x = onFulfilled(this.value as T);
              resolvePromise(promise2, x, resolve, reject);
            }
          } catch (e) {
            reject(e);
          }
        });
      };

      const rejectedTask = () => {
        queueMicrotask(() => {
          try {
            if (typeof onRejected !== 'function') {
              reject(this.reason);
            } else {
              const x = onRejected(this.reason);
              resolvePromise(promise2, x, resolve, reject);
            }
          } catch (e) {
            reject(e);
          }
        });
      };

      if (this.state === 'fulfilled') {
        fulfilledTask();
      } else if (this.state === 'rejected') {
        rejectedTask();
      } else {
        this.onFulfilledCallbacks.push(fulfilledTask);
        this.onRejectedCallbacks.push(rejectedTask);
      }
    });

    return promise2;
  }

  /**
   * catch method for handling rejections
   * @param onRejected - Callback to execute when the promise is rejected
   * @returns A new promise that resolves to the return value of onRejected
   */
  catch<TResult = never>(
    onRejected?: ((reason: any) => TResult | PromiseLike<TResult>) | undefined | null
  ): MyPromise<T | TResult> {
    return this.then(null, onRejected);
  }

  /**
   * finally method for executing logic regardless of promise outcome
   * @param onFinally - Callback to execute when the promise is settled
   * @returns A new promise that resolves to the same value/reason as the original promise
   */
  finally(onFinally?: (() => void) | undefined | null): MyPromise<T> {
    return this.then(
      (value) => {
        if (typeof onFinally === 'function') {
          onFinally();
        }
        return value;
      },
      (reason) => {
        if (typeof onFinally === 'function') {
          onFinally();
        }
        throw reason;
      }
    );
  }

  /**
   * Static method to create a resolved promise
   * @param value - The value to resolve
   */
  static resolve<T>(value: T | PromiseLike<T>): MyPromise<T> {
    if (value instanceof MyPromise) {
      return value;
    }
    return new MyPromise<T>((resolve) => resolve(value));
  }

  /**
   * Static method to create a rejected promise
   * @param reason - The reason for rejection
   */
  static reject<T = never>(reason?: any): MyPromise<T> {
    return new MyPromise<T>((_, reject) => reject(reason));
  }

  /**
   * Static method that resolves when all of the given promises resolve,
   * or rejects when any of them rejects.
   * @param values - An iterable of promises or values
   */
  static all<T>(values: Iterable<T | PromiseLike<T>>): MyPromise<T[]> {
    return new MyPromise((resolve, reject) => {
      const results: T[] = [];
      let completedCount = 0;
      const arrayValues = Array.from(values);

      if (arrayValues.length === 0) {
        resolve([]);
        return;
      }

      arrayValues.forEach((value, i) => {
        MyPromise.resolve(value).then(
          (val) => {
            results[i] = val;
            completedCount++;
            if (completedCount === arrayValues.length) {
              resolve(results);
            }
          },
          (reason) => {
            reject(reason);
          }
        );
      });
    });
  }

  /**
   * Static method that settles when the first of the given promises settles.
   * @param values - An iterable of promises or values
   */
  static race<T>(values: Iterable<T | PromiseLike<T>>): MyPromise<T> {
    return new MyPromise((resolve, reject) => {
      for (const value of values) {
        MyPromise.resolve(value).then(resolve, reject);
      }
    });
  }

  /**
   * Static method that resolves when all given promises settle.
   * @param values - An iterable of promises or values
   */
  static allSettled<T>(
    values: Iterable<T | PromiseLike<T>>
  ): MyPromise<Array<{ status: 'fulfilled'; value: T } | { status: 'rejected'; reason: any }>> {
    return new MyPromise((resolve) => {
      const results: Array<
        { status: 'fulfilled'; value: T } | { status: 'rejected'; reason: any }
      > = [];
      let completedCount = 0;
      const arrayValues = Array.from(values);

      if (arrayValues.length === 0) {
        resolve([]);
        return;
      }

      arrayValues.forEach((value, i) => {
        MyPromise.resolve(value).then(
          (val) => {
            results[i] = { status: 'fulfilled', value: val };
            completedCount++;
            if (completedCount === arrayValues.length) {
              resolve(results);
            }
          },
          (reason) => {
            results[i] = { status: 'rejected', reason };
            completedCount++;
            if (completedCount === arrayValues.length) {
              resolve(results);
            }
          }
        );
      });
    });
  }

  /**
   * Static method that resolves when any of the given promises resolve.
   * If all fail, it rejects with an AggregateError.
   * @param values - An iterable of promises or values
   */
  static any<T>(values: Iterable<T | PromiseLike<T>>): MyPromise<T> {
    return new MyPromise((resolve, reject) => {
      const errors: any[] = [];
      let rejectedCount = 0;
      const arrayValues = Array.from(values);

      if (arrayValues.length === 0) {
        reject(new MyAggregateError([], 'All promises were rejected'));
        return;
      }

      arrayValues.forEach((value, i) => {
        MyPromise.resolve(value).then(
          (val) => {
            resolve(val);
          },
          (reason) => {
            errors[i] = reason;
            rejectedCount++;
            if (rejectedCount === arrayValues.length) {
              const AggregateErrorCtor = (globalThis as any).AggregateError || MyAggregateError;
              reject(new AggregateErrorCtor(errors, 'All promises were rejected'));
            }
          }
        );
      });
    });
  }
}

/**
 * Promise Resolution Procedure
 * @param promise - The promise being resolved
 * @param x - The value being resolved with
 * @param resolve - The fulfillment function
 * @param reject - The rejection function
 */
function resolvePromise<T>(
  promise: MyPromise<T> | any,
  x: any,
  resolve: Resolve<T> | any,
  reject: Reject
) {
  // 2.3.1
  if (promise === x) {
    return reject(new TypeError('Chaining cycle detected for promise'));
  }

  // 2.3.2
  if (x instanceof MyPromise) {
    x.then((y: any) => {
      resolvePromise(promise, y, resolve, reject);
    }, reject);
    return;
  }

  // 2.3.3
  let called = false;
  if (x !== null && (typeof x === 'object' || typeof x === 'function')) {
    try {
      const then = x.then;
      if (typeof then === 'function') {
        then.call(
          x,
          (y: any) => {
            if (called) return;
            called = true;
            resolvePromise(promise, y, resolve, reject);
          },
          (r: any) => {
            if (called) return;
            called = true;
            reject(r);
          }
        );
      } else {
        resolve(x);
      }
    } catch (e) {
      if (called) return;
      called = true;
      reject(e);
    }
  } else {
    // 2.3.4
    resolve(x);
  }
}
