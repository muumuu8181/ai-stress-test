
import { MyPromise } from '../src/index';

export const resolved = <T>(value: T) => MyPromise.resolve(value);
export const rejected = (reason: any) => MyPromise.reject(reason);
export const deferred = () => {
  let resolve!: (value: any) => void;
  let reject!: (reason: any) => void;
  const promise = new MyPromise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return {
    promise,
    resolve,
    reject,
  };
};
