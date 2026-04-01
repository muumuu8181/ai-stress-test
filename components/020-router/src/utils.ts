import { RouteQuery } from './types';

/**
 * Parses query string into an object
 * @param query - The query string (e.g., 'a=1&b=2')
 */
export function parseQuery(query: string): RouteQuery {
  const res: RouteQuery = {};
  query = query.trim().replace(/^(\?|#|&)/, '');

  if (!query) return res;

  query.split('&').forEach((param) => {
    const parts = param.replace(/\+/g, ' ').split('=');
    const key = decodeURIComponent(parts.shift() || '');
    const val = parts.length > 0 ? decodeURIComponent(parts.join('=')) : null;

    if (res[key] === undefined) {
      res[key] = val;
    } else if (Array.isArray(res[key])) {
      (res[key] as (string | null)[]).push(val);
    } else {
      res[key] = [res[key] as string, val];
    }
  });

  return res;
}

/**
 * Serializes query object into a string
 * @param query - The query object
 */
export function stringifyQuery(query: RouteQuery): string {
  const res = Object.keys(query)
    .map((key) => {
      const val = query[key];

      if (val === undefined) return '';

      if (val === null) return encodeURIComponent(key);

      if (Array.isArray(val)) {
        return val
          .map((v) =>
            v === null
              ? encodeURIComponent(key)
              : `${encodeURIComponent(key)}=${encodeURIComponent(v)}`
          )
          .join('&');
      }

      return `${encodeURIComponent(key)}=${encodeURIComponent(val)}`;
    })
    .filter((x) => x.length > 0)
    .join('&');

  return res ? `?${res}` : '';
}
