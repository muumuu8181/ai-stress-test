import { describe, it, expect, vi } from 'vitest';
import { Store, Action, Middleware } from '../src/store';
import { createSelector } from '../src/selector';

interface CounterState {
  count: number;
}

const counterReducer = (state: CounterState, action: Action): CounterState => {
  switch (action.type) {
    case 'increment':
      return { count: state.count + 1 };
    case 'decrement':
      return { count: state.count - 1 };
    default:
      return state;
  }
};

describe('Store', () => {
  it('should initialize with initial state', () => {
    const store = new Store(counterReducer, { count: 0 });
    expect(store.getState()).toEqual({ count: 0 });
  });

  it('should update state on dispatch', () => {
    const store = new Store(counterReducer, { count: 0 });
    store.dispatch({ type: 'increment' });
    expect(store.getState()).toEqual({ count: 1 });
  });

  it('should notify subscribers of state updates', () => {
    const store = new Store(counterReducer, { count: 0 });
    const results: number[] = [];
    store.state$.subscribe((s) => results.push(s.count));
    store.dispatch({ type: 'increment' });
    store.dispatch({ type: 'increment' });
    expect(results).toEqual([0, 1, 2]);
  });

  it('should use middleware', () => {
    const log: Action[] = [];
    const logger: Middleware<CounterState> = (store) => (next) => (action) => {
      log.push(action);
      next(action);
    };

    const store = new Store(counterReducer, { count: 0 }, [logger]);
    store.dispatch({ type: 'increment' });
    expect(log).toEqual([{ type: 'increment' }]);
    expect(store.getState()).toEqual({ count: 1 });
  });

  it('should maintain history and allow restoration', () => {
    const store = new Store(counterReducer, { count: 0 });
    store.dispatch({ type: 'increment' });
    store.dispatch({ type: 'increment' });
    expect(store.getHistory()).toEqual([{ count: 0 }, { count: 1 }, { count: 2 }]);

    store.restoreState(1);
    expect(store.getState()).toEqual({ count: 1 });
    expect(store.getCurrentIndex()).toBe(1);

    // Dispatching new action after restoration should truncate history
    store.dispatch({ type: 'increment' });
    expect(store.getState()).toEqual({ count: 2 });
    expect(store.getHistory()).toEqual([{ count: 0 }, { count: 1 }, { count: 2 }]);
    expect(store.getCurrentIndex()).toBe(2);
  });
});

describe('Selectors', () => {
  it('should select state and memoize result', () => {
    const selectCount = (state: CounterState) => state.count;
    const project = vi.fn((count) => count * 2);
    const selector = createSelector([selectCount], project);

    const state1 = { count: 1 };
    const state2 = { count: 1 };
    const state3 = { count: 2 };

    expect(selector(state1)).toBe(2);
    expect(selector(state2)).toBe(2);
    expect(project).toHaveBeenCalledTimes(1);

    expect(selector(state3)).toBe(4);
    expect(project).toHaveBeenCalledTimes(2);
  });

  it('should handle multiple selectors', () => {
    interface State {
      a: number;
      b: number;
    }
    const selectA = (s: State) => s.a;
    const selectB = (s: State) => s.b;
    const project = vi.fn((a, b) => a + b);
    const selector = createSelector([selectA, selectB], project);

    const state = { a: 1, b: 2 };
    expect(selector(state)).toBe(3);
    expect(selector({ a: 1, b: 2 })).toBe(3);
    expect(project).toHaveBeenCalledTimes(1);
    expect(selector({ a: 2, b: 2 })).toBe(4);
    expect(project).toHaveBeenCalledTimes(2);
  });
});
