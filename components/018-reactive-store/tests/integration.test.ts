import { describe, it, expect } from 'vitest';
import { Store, Action, Middleware } from '../src/store';
import { map, filter, debounce } from '../src/operators';
import { createSelector } from '../src/selector';

interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

interface TodoState {
  todos: Todo[];
  filter: 'all' | 'completed' | 'active';
}

const todoReducer = (state: TodoState, action: Action): TodoState => {
  switch (action.type) {
    case 'addTodo':
      return {
        ...state,
            todos: [...state.todos, { id: action.payload.id, text: action.payload.text, completed: false }],
      };
    case 'toggleTodo':
      return {
        ...state,
        todos: state.todos.map((todo) =>
          todo.id === action.payload ? { ...todo, completed: !todo.completed } : todo
        ),
      };
    case 'setFilter':
      return { ...state, filter: action.payload };
    default:
      return state;
  }
};

describe('Integration Test', () => {
  it('should flow data correctly through store, middleware, and selectors', async () => {
    const initialState: TodoState = {
      todos: [],
      filter: 'all',
    };

    const actionHistory: Action[] = [];
    const logger: Middleware<TodoState> = (store) => (next) => (action) => {
      actionHistory.push(action);
      next(action);
    };

    const store = new Store(todoReducer, initialState, [logger]);

    const selectTodos = (s: TodoState) => s.todos;
    const selectFilter = (s: TodoState) => s.filter;
    const selectVisibleTodos = createSelector([selectTodos, selectFilter], (todos, filter) => {
      switch (filter) {
        case 'completed':
          return todos.filter((t) => t.completed);
        case 'active':
          return todos.filter((t) => !t.completed);
        default:
          return todos;
      }
    });

    const visibleResults: Todo[][] = [];
    store.state$
      .pipe(map((s) => selectVisibleTodos(s)))
      .subscribe((v) => visibleResults.push(v));

    store.dispatch({ type: 'addTodo', payload: { id: 1, text: 'Learn RxJS' } });
    store.dispatch({ type: 'addTodo', payload: { id: 2, text: 'Build Store' } });

    const todoId1 = store.getState().todos[0].id;
    const todoId2 = store.getState().todos[1].id;
    store.dispatch({ type: 'toggleTodo', payload: todoId1 });
    store.dispatch({ type: 'toggleTodo', payload: todoId2 });
    store.dispatch({ type: 'setFilter', payload: 'completed' });

    expect(visibleResults.length).toBe(6); // initial + 5 actions
    expect(visibleResults[5].length).toBe(2);
    expect(visibleResults[5][0].text).toBe('Learn RxJS');
    expect(visibleResults[5][0].completed).toBe(true);

    expect(actionHistory.length).toBe(5);

    // Time travel
    store.restoreState(0);
    expect(store.getState().todos.length).toBe(0);
    expect(visibleResults[visibleResults.length - 1].length).toBe(0);
  });
});
