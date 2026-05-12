export const environment = {
  production: true,
  /**
   * Empty = same origin (SPA served by FastAPI — see repo root Dockerfile / STATIC_DIR).
   * If the UI is hosted separately, set the public API base URL before `ng build` (no trailing slash).
   */
  apiUrl: '',
};
