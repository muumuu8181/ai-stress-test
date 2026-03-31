
import { describe, it, expect, vi } from 'vitest';
import { MyPromise } from '../src/index';

describe('MyPromise Core and Instance Methods', () => {
  it('should resolve a value', async () => {
    const promise = new MyPromise<number>((resolve) => {
      resolve(42);
    });
    const result = await new Promise((resolve) => {
        promise.then(resolve);
    });
    expect(result).toBe(42);
  });

  it('should reject a reason', async () => {
    const promise = new MyPromise((_, reject) => {
      reject('error');
    });
    const result = await new Promise((resolve) => {
        promise.then(null, resolve);
    });
    expect(result).toBe('error');
  });

  it('should support chaining then', async () => {
    const result = await new Promise((resolve) => {
        new MyPromise<number>((res) => res(1))
            .then((v) => v + 1)
            .then((v) => v * 2)
            .then(resolve);
    });
    expect(result).toBe(4);
  });

  it('should handle catch', async () => {
    const result = await new Promise((resolve) => {
        MyPromise.reject('fail')
            .catch((err) => {
                return 'recovered ' + err;
            })
            .then(resolve);
    });
    expect(result).toBe('recovered fail');
  });

  it('should handle finally on resolve', async () => {
    const onFinally = vi.fn();
    const result = await new Promise((resolve) => {
        MyPromise.resolve(100)
            .finally(onFinally)
            .then(resolve);
    });
    expect(result).toBe(100);
    expect(onFinally).toHaveBeenCalled();
  });

  it('should handle finally on reject', async () => {
    const onFinally = vi.fn();
    const result = await new Promise((resolve) => {
        MyPromise.reject('err')
            .finally(onFinally)
            .catch(resolve);
    });
    expect(result).toBe('err');
    expect(onFinally).toHaveBeenCalled();
  });
});

describe('MyPromise Static Methods', () => {
  it('Promise.all: resolves with all values', async () => {
    const values = [1, MyPromise.resolve(2), new MyPromise((res) => setTimeout(() => res(3), 10))];
    const result = await new Promise((resolve) => {
        MyPromise.all(values).then(resolve);
    });
    expect(result).toEqual([1, 2, 3]);
  });

  it('Promise.all: rejects if any fail', async () => {
    const values = [1, MyPromise.reject('fail'), 3];
    const result = await new Promise((resolve) => {
        MyPromise.all(values).catch(resolve);
    });
    expect(result).toBe('fail');
  });

  it('Promise.race: resolves with first value', async () => {
    const values = [
        new MyPromise((res) => setTimeout(() => res(1), 20)),
        new MyPromise((res) => setTimeout(() => res(2), 10))
    ];
    const result = await new Promise((resolve) => {
        MyPromise.race(values).then(resolve);
    });
    expect(result).toBe(2);
  });

  it('Promise.allSettled: resolves with all status objects', async () => {
    const values = [MyPromise.resolve(1), MyPromise.reject('fail')];
    const result = await new Promise((resolve) => {
        MyPromise.allSettled(values).then(resolve);
    });
    expect(result).toEqual([
        { status: 'fulfilled', value: 1 },
        { status: 'rejected', reason: 'fail' }
    ]);
  });

  it('Promise.any: resolves with first success', async () => {
    const values = [MyPromise.reject('fail'), MyPromise.resolve('win')];
    const result = await new Promise((resolve) => {
        MyPromise.any(values).then(resolve);
    });
    expect(result).toBe('win');
  });

  it('Promise.any: rejects if all fail', async () => {
    const values = [MyPromise.reject('fail1'), MyPromise.reject('fail2')];
    const result = await new Promise((resolve) => {
        MyPromise.any(values).catch(resolve);
    });
    expect((result as Error).message).toBe('All promises were rejected');
  });

  it('Promise.all: empty array', async () => {
    const result = await new Promise((resolve) => {
        MyPromise.all([]).then(resolve);
    });
    expect(result).toEqual([]);
  });

  it('Promise.race: empty array (remains pending)', async () => {
    const p = MyPromise.race([]);
    let resolved = false;
    p.then(() => { resolved = true; });
    await new Promise(res => setTimeout(res, 50));
    expect(resolved).toBe(false);
  });

  it('Promise.allSettled: empty array', async () => {
    const result = await MyPromise.allSettled([]);
    expect(result).toEqual([]);
  });

  it('Promise.any: empty array (rejects)', async () => {
    try {
        await MyPromise.any([]);
    } catch (e) {
        expect((e as Error).message).toBe('All promises were rejected');
    }
  });

  it('resolvePromise: with thenable that calls both resolve and reject', async () => {
    const thenable = {
        then: (onFulfilled: any, onRejected: any) => {
            onFulfilled(1);
            onRejected(2);
        }
    };
    const p = new MyPromise(resolve => resolve(thenable));
    const val = await p;
    expect(val).toBe(1);
  });

  it('constructor: resolve with a foreign thenable', async () => {
    const foreign = {
        then: (onFulfilled: any) => {
            setTimeout(() => onFulfilled('foreign'), 10);
        }
    };
    const p = new MyPromise(resolve => resolve(foreign as any));
    const val = await p;
    expect(val).toBe('foreign');
  });

  it('static resolve: with a foreign thenable', async () => {
    const foreign = {
        then: (_: any, onRejected: any) => {
            onRejected('fail');
        }
    };
    const p = MyPromise.resolve(foreign as any);
    try {
        await p;
    } catch (e) {
        expect(e).toBe('fail');
    }
  });

  it('resolvePromise: with then that throws after resolve', async () => {
    const thenable = {
        then: (onFulfilled: any) => {
            onFulfilled(1);
            throw new Error('ignored');
        }
    };
    const p = new MyPromise(resolve => resolve(thenable));
    const val = await p;
    expect(val).toBe(1);
  });

  it('resolvePromise: with non-object/non-function x', async () => {
    const p = new MyPromise(resolve => resolve(42 as any));
    const val = await p;
    expect(val).toBe(42);
  });

  it('resolvePromise: with then property that throws', async () => {
    const x = {};
    Object.defineProperty(x, 'then', {
        get: () => { throw 'error in then getter'; }
    });
    const p = new MyPromise(resolve => resolve(x as any));
    try {
        await p;
    } catch (e) {
        expect(e).toBe('error in then getter');
    }
  });
});
