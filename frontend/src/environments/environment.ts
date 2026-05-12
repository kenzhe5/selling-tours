export const environment = {
  production: false,
  /**
   * Empty = same origin as the dev server; `/api/*` is proxied to the backend (see proxy.conf.json).
   * Avoids CORS when the UI runs on another localhost port (e.g. preview on 4299).
   */
  apiUrl: '',
};
