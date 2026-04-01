import { describe, it, expect, vi } from 'vitest';
import { Observable } from '../src/observable';
import { Subject, BehaviorSubject, ReplaySubject } from '../src/subject';
import { map, filter, reduce, debounce, throttle } from '../src/operators';
import { merge, combineLatest } from '../src/creation';

describe('Observable', () => {
  it('should emit values', () => {
    const obs = Observable.of(1, 2, 3);
    const results: number[] = [];
    obs.subscribe((v) => results.push(v));
    expect(results).toEqual([1, 2, 3]);
  });

  it('should complete', () => {
    const obs = Observable.of(1);
    const completeSpy = vi.fn();
    obs.subscribe({ complete: completeSpy });
    expect(completeSpy).toHaveBeenCalled();
  });

  it('should handle errors', () => {
    const obs = new Observable((observer) => {
      observer.error('error');
    });
    const errorSpy = vi.fn();
    obs.subscribe({ error: errorSpy });
    expect(errorSpy).toHaveBeenCalledWith('error');
  });

  it('should unsubscribe', () => {
    let nextCount = 0;
    const obs = new Observable<number>((observer) => {
      observer.next(1);
      const id = setTimeout(() => observer.next(2), 10);
      return () => clearTimeout(id);
    });

    const sub = obs.subscribe(() => nextCount++);
    expect(nextCount).toBe(1);
    sub.unsubscribe();

    // Wait to see if next happens
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(nextCount).toBe(1);
        resolve();
      }, 20);
    });
  });
});

describe('Subjects', () => {
  it('Subject should multicast', () => {
    const sub = new Subject<number>();
    const res1: number[] = [];
    const res2: number[] = [];
    sub.subscribe((v) => res1.push(v));
    sub.next(1);
    sub.subscribe((v) => res2.push(v));
    sub.next(2);
    expect(res1).toEqual([1, 2]);
    expect(res2).toEqual([2]);
  });

  it('BehaviorSubject should emit initial value', () => {
    const sub = new BehaviorSubject<number>(0);
    const res: number[] = [];
    sub.subscribe((v) => res.push(v));
    sub.next(1);
    expect(res).toEqual([0, 1]);
    expect(sub.getValue()).toBe(1);
  });

  it('ReplaySubject should replay values', () => {
    const sub = new ReplaySubject<number>(2);
    sub.next(1);
    sub.next(2);
    sub.next(3);
    const res: number[] = [];
    sub.subscribe((v) => res.push(v));
    expect(res).toEqual([2, 3]);
  });
});

describe('Operators', () => {
  it('map should transform values', () => {
    const results: number[] = [];
    const errorSpy = vi.fn();
    Observable.of(1, 2, 3)
      .pipe(map((x) => x * 2))
      .subscribe({
        next: (v) => results.push(v),
        error: errorSpy
      });
    expect(results).toEqual([2, 4, 6]);

    const s = new Subject<number>();
    s.pipe(map(x => x)).subscribe({ error: errorSpy });
    s.error('err');
    expect(errorSpy).toHaveBeenCalledWith('err');
  });

  it('filter should filter values', () => {
    const results: number[] = [];
    const errorSpy = vi.fn();
    Observable.of(1, 2, 3, 4)
      .pipe(filter((x) => x % 2 === 0))
      .subscribe({
        next: (v) => results.push(v),
        error: errorSpy
      });
    expect(results).toEqual([2, 4]);

    const s = new Subject<number>();
    s.pipe(filter(x => true)).subscribe({ error: errorSpy });
    s.error('err');
    expect(errorSpy).toHaveBeenCalledWith('err');
  });

  it('reduce should accumulate values', () => {
    const results: number[] = [];
    Observable.of(1, 2, 3)
      .pipe(reduce((acc, val) => acc + val, 0))
      .subscribe((v) => results.push(v));
    expect(results).toEqual([6]);
  });

  it('debounce should debounce emissions', async () => {
    const sub = new Subject<number>();
    const results: number[] = [];
    sub.pipe(debounce(20)).subscribe((v) => results.push(v));

    sub.next(1);
    await new Promise((r) => setTimeout(r, 10));
    sub.next(2);
    await new Promise((r) => setTimeout(r, 30));
    sub.next(3);
    sub.complete();

    expect(results).toEqual([2, 3]);
  });

  it('throttle should throttle emissions', async () => {
    const sub = new Subject<number>();
    const results: number[] = [];
    sub.pipe(throttle(20)).subscribe((v) => results.push(v));

    sub.next(1);
    await new Promise((r) => setTimeout(r, 10));
    sub.next(2);
    await new Promise((r) => setTimeout(r, 15)); // 25ms total
    sub.next(3);

    expect(results).toEqual([1, 3]);
  });
});

describe('Creation Functions', () => {
  it('merge should merge observables', () => {
    const s1 = new Subject<number>();
    const s2 = new Subject<number>();
    const results: number[] = [];
    merge(s1, s2).subscribe((v) => results.push(v));
    s1.next(1);
    s2.next(2);
    s1.next(3);
    expect(results).toEqual([1, 2, 3]);
  });

  it('combineLatest should combine latest values', () => {
    const s1 = new Subject<number>();
    const s2 = new Subject<string>();
    const results: any[] = [];
    combineLatest(s1, s2).subscribe((v) => results.push(v));
    s1.next(1);
    s2.next('a');
    s1.next(2);
    s2.next('b');
    expect(results).toEqual([[1, 'a'], [2, 'a'], [2, 'b']]);
  });

  it('merge should handle error', () => {
    const s1 = new Subject<number>();
    const errorSpy = vi.fn();
    merge(s1).subscribe({ error: errorSpy });
    s1.error('oops');
    expect(errorSpy).toHaveBeenCalledWith('oops');
  });

  it('combineLatest should handle error', () => {
    const s1 = new Subject<number>();
    const errorSpy = vi.fn();
    combineLatest(s1).subscribe({ error: errorSpy });
    s1.error('oops');
    expect(errorSpy).toHaveBeenCalledWith('oops');
  });
});
