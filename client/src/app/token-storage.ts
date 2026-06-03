const TOKEN_KEY = "dota_trener_token";
const STEAM_ID_KEY = "dota_trener_steam_id";

export function saveToken(token: string, steam_id?: string) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(TOKEN_KEY, token);
    if (steam_id) window.localStorage.setItem(STEAM_ID_KEY, steam_id);
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function getSteamId(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(STEAM_ID_KEY);
}

export function clearToken() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(STEAM_ID_KEY);
  }
}
