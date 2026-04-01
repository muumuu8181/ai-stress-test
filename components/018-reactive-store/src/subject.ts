import { Observable, Observer, Subscription, TeardownLogic } from './observable';

/**
 * A Subject is a special type of Observable that allows values to be multicasted to many Observers.
 */
export class Subject<T> extends Observable<T> implements Observer<T> {
  protected observers: Array<Observer<T>> = [];
  protected isClosed = false;

  constructor() {
    super((observer) => {
      this.observers.push(observer);
      return () => {
        const index = this.observers.indexOf(observer);
        if (index > -1) {
          this.observers.splice(index, 1);
        }
      };
    });
  }

  /**
   * Pushes a new value to all subscribers.
   */
  next(value: T): void {
    if (this.isClosed) return;
    const currentObservers = [...this.observers];
    currentObservers.forEach((observer) => observer.next(value));
  }

  /**
   * Pushes an error to all subscribers and closes the Subject.
   */
  error(err: any): void {
    if (this.isClosed) return;
    this.isClosed = true;
    const currentObservers = [...this.observers];
    currentObservers.forEach((observer) => observer.error?.(err));
    this.observers = [];
  }

  /**
   * Signals completion to all subscribers and closes the Subject.
   */
  complete(): void {
    if (this.isClosed) return;
    this.isClosed = true;
    const currentObservers = [...this.observers];
    currentObservers.forEach((observer) => observer.complete?.());
    this.observers = [];
  }
}

/**
 * A BehaviorSubject stores the current value and emits it to new subscribers.
 */
export class BehaviorSubject<T> extends Subject<T> {
  private _currentValue: T;

  constructor(initialValue: T) {
    super();
    this._currentValue = initialValue;

    // Override the constructor-level _subscribe by adding a special logic.
    // However, super() already defined _subscribe. Let's adjust BehaviorSubject to emit current value on subscribe.
  }

  /**
   * Subscribes an observer and immediately emits the current value.
   */
  subscribe(observerOrNext: Partial<Observer<T>> | ((value: T) => void)): Subscription {
    const subscription = super.subscribe(observerOrNext);

    let observer: Partial<Observer<T>>;
    if (typeof observerOrNext === 'function') {
      observer = { next: observerOrNext };
    } else {
      observer = observerOrNext;
    }

    if (!this.isClosed) {
      observer.next?.(this._currentValue);
    }

    return subscription;
  }

  /**
   * Pushes a new value and updates the current value.
   */
  next(value: T): void {
    this._currentValue = value;
    super.next(value);
  }

  /**
   * Returns the current value of the BehaviorSubject.
   */
  getValue(): T {
    return this._currentValue;
  }
}

/**
 * A ReplaySubject caches a specified number of values and emits them to new subscribers.
 */
export class ReplaySubject<T> extends Subject<T> {
  private _buffer: T[] = [];

  constructor(private _bufferSize: number = Infinity) {
    super();
  }

  /**
   * Subscribes an observer and emits cached values.
   */
  subscribe(observerOrNext: Partial<Observer<T>> | ((value: T) => void)): Subscription {
    const subscription = super.subscribe(observerOrNext);

    let observer: Partial<Observer<T>>;
    if (typeof observerOrNext === 'function') {
      observer = { next: observerOrNext };
    } else {
      observer = observerOrNext;
    }

    this._buffer.forEach((v) => observer.next?.(v));

    return subscription;
  }

  /**
   * Pushes a new value and adds it to the buffer.
   */
  next(value: T): void {
    this._buffer.push(value);
    if (this._buffer.length > this._bufferSize) {
      this._buffer.shift();
    }
    super.next(value);
  }
}
