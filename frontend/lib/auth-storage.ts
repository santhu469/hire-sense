// SPA-style token storage: kept in localStorage so a page reload survives
// without re-authenticating. Read only ever happens in client components
// (this module touches `window`/`localStorage`, never called during SSR).

const ACCESS_TOKEN_KEY = "hiresense.access_token";
const REFRESH_TOKEN_KEY = "hiresense.refresh_token";

export function getStoredTokens(): { accessToken: string; refreshToken: string } | null {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!accessToken || !refreshToken) return null;
  return { accessToken, refreshToken };
}

export function storeTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}
