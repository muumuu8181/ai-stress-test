import { BehaviorSubject } from './subject';
import { Observable } from './observable';

/**
 * Interface for an action that can be dispatched to the Store.
 */
export interface Action {
  type: string;
  payload?: any;
}

/**
 * Type definition for a reducer function.
 */
export type Reducer<S> = (state: S, action: Action) => S;

/**
 * Type definition for a middleware function.
 */
export type Middleware<S> = (store: Store<S>) => (next: (action: Action) => void) => (action: Action) => void;

/**
 * A Reactive State Store that manages state using reducers and notifies subscribers of updates.
 */
export class Store<S> {
  private _state$: BehaviorSubject<S>;
  private _reducer: Reducer<S>;
  private _dispatch: (action: Action) => void;
  private _history: S[] = [];

  /**
   * @param reducer The reducer function.
   * @param initialState The initial state.
   * @param middlewares Optional array of middleware functions.
   */
  constructor(reducer: Reducer<S>, initialState: S, middlewares: Middleware<S>[] = []) {
    this._reducer = reducer;
    this._state$ = new BehaviorSubject<S>(initialState);
    this._history.push(initialState);

    // Basic dispatch
    const basicDispatch = (action: Action) => {
      const currentState = this._state$.getValue();
      const newState = this._reducer(currentState, action);
      if (newState !== currentState) {
        this._history.push(newState);
        this._state$.next(newState);
      }
    };

    // Chain middlewares
    this._dispatch = middlewares
      .reverse()
      .reduce((next, middleware) => middleware(this)(next), basicDispatch as (action: Action) => void);
  }

  /**
   * Dispatches an action to update the state.
   */
  dispatch(action: Action): void {
    this._dispatch(action);
  }

  /**
   * Returns an Observable of the current state.
   */
  get state$(): Observable<S> {
    return this._state$;
  }

  /**
   * Returns the current state value.
   */
  getState(): S {
    return this._state$.getValue();
  }

  /**
   * Returns the history of states (for time travel).
   */
  getHistory(): S[] {
    return [...this._history];
  }

  /**
   * Restores the state to a specific point in history.
   * @param index The index in history to restore.
   */
  restoreState(index: number): void {
    if (index >= 0 && index < this._history.length) {
      const state = this._history[index];
      this._state$.next(state);
    }
  }
}
