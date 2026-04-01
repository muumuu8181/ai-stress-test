import { RouteRecord, Route, RouteParams } from './types';
import { parseQuery } from './utils';

/**
 * Normalizes a path by removing trailing slash (except for '/')
 * @param path - The path to normalize
 */
function normalizePath(path: string): string {
  if (path === '/') return path;
  return path.endsWith('/') ? path.slice(0, -1) : path;
}

/**
 * Converts a path pattern to a regex and extracts param names
 * @param path - The path pattern (e.g., '/users/:id')
 */
function compilePath(path: string): { regex: RegExp; keys: string[] } {
  const keys: string[] = [];
  const regexPath = path.replace(/:([^/]+)/g, (_, key) => {
    keys.push(key);
    return '([^/]+)';
  });
  return {
    regex: new RegExp(`^${regexPath}$`),
    keys,
  };
}

/**
 * Internal route record used for matching
 */
interface MatcherRecord extends RouteRecord {
  fullPath: string;
  regex: RegExp;
  keys: string[];
  children?: MatcherRecord[];
}

/**
 * Matcher for route resolution
 */
export class RouterMatcher {
  private matcherRecords: MatcherRecord[];

  constructor(routes: RouteRecord[]) {
    this.matcherRecords = this.createMatcherRecords(routes);
  }

  /**
   * Recursively transforms RouteRecords to MatcherRecords
   * @param routes - List of route definitions
   * @param parentPath - Parent path for nested routes
   */
  private createMatcherRecords(
    routes: RouteRecord[],
    parentPath: string = ''
  ): MatcherRecord[] {
    const records: MatcherRecord[] = [];

    for (const route of routes) {
      let fullPath = route.path;
      if (route.path === '*') {
        // Leave '*' as is for special matching
      } else if (route.path.startsWith('/')) {
        fullPath = normalizePath(route.path);
      } else {
        fullPath = normalizePath(`${parentPath}/${route.path}`);
      }

      let regex: RegExp;
      let keys: string[];

      if (fullPath === '*') {
        regex = /.*/;
        keys = [];
      } else {
        const compiled = compilePath(fullPath);
        // If the record has children, the regex should not have '$' at the end
        // unless we want to match it as a leaf as well.
        // Actually, many routers match prefixes.
        // Let's use a more flexible regex or try to match children first.
        regex = route.children ? new RegExp(`^${fullPath.replace(/:([^/]+)/g, '([^/]+)')}(/.*)?$`) : compiled.regex;
        keys = compiled.keys;
      }

      const record: MatcherRecord = {
        ...route,
        fullPath,
        regex,
        keys,
      };

      if (route.children) {
        record.children = this.createMatcherRecords(route.children, fullPath);
      }

      records.push(record);
    }

    return records;
  }

  /**
   * Matches a full URL against registered routes
   * @param fullPath - The full URL string
   */
  public match(fullPath: string): Route | null {
    const [pathWithHash, queryString] = fullPath.split('?');
    const [path, hash] = pathWithHash.split('#');
    const normalizedPath = normalizePath(path);
    const query = parseQuery(queryString || '');

    return this.matchRecursive(this.matcherRecords, normalizedPath, query, hash || '');
  }

  /**
   * Recursively finds a matching route record
   */
  private matchRecursive(
    records: MatcherRecord[],
    path: string,
    query: any,
    hash: string,
    matched: RouteRecord[] = []
  ): Route | null {
    for (const record of records) {
      if (record.path === '*') continue; // Special case: wildcard matched last

      const match = path.match(record.regex);
      if (match) {
        const params: RouteParams = {};
        record.keys.forEach((key, index) => {
          params[key] = match[index + 1];
        });

        const currentMatched = [...matched, record];

        if (record.children) {
          const childMatch = this.matchRecursive(
            record.children,
            path,
            query,
            hash,
            currentMatched
          );
          if (childMatch) return childMatch;
        }

        // Return the first match that doesn't have more specific children matching
        return {
          path: record.fullPath,
          fullPath: path + (hash ? '#' + hash : '') + (Object.keys(query).length ? '?' + new URLSearchParams(query).toString() : ''),
          params,
          query,
          hash: hash ? `#${hash}` : '',
          name: record.name,
          meta: record.meta,
          matched: currentMatched,
        };
      }
    }

    // Try to match wildcard if no other matches found
    const wildcard = records.find((r) => r.path === '*');
    if (wildcard) {
      return {
        path: '*',
        fullPath: path + (hash ? '#' + hash : '') + (Object.keys(query).length ? '?' + new URLSearchParams(query).toString() : ''),
        params: {},
        query,
        hash: hash ? `#${hash}` : '',
        name: wildcard.name,
        meta: wildcard.meta,
        matched: [...matched, wildcard],
      };
    }

    return null;
  }
}
