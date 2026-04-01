/**
 * Creates a memoized selector function.
 */
export function createSelector<S, R>(
  selectors: Array<(state: S) => any>,
  project: (...args: any[]) => R
): (state: S) => R {
  let lastArgs: any[] | null = null;
  let lastResult: R | null = null;

  return (state: S): R => {
    const currentArgs = selectors.map((sel) => sel(state));

    if (
      lastArgs !== null &&
      currentArgs.length === lastArgs.length &&
      currentArgs.every((val, index) => val === lastArgs![index])
    ) {
      return lastResult as R;
    }

    lastArgs = currentArgs;
    lastResult = project(...currentArgs);
    return lastResult;
  };
}
