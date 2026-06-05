const TOKEN_KEY = "dota_trener_token";
const STEAM_ID_KEY = "dota_trener_steam_id";

function getStorage(): Storage | null {
  if (typeof window !== "undefined" && window.localStorage) {
    return window.localStorage;
  }
  return null;
}

export function saveToken(token: string, steam_id?: string) {
  const storage = getStorage();
  if (storage) {
    storage.setItem(TOKEN_KEY, token);
    if (steam_id) storage.setItem(STEAM_ID_KEY, steam_id);
  }
}

export function getToken(): string | null {
  const storage = getStorage();
  return storage ? storage.getItem(TOKEN_KEY) : null;
}

export function getSteamId(): string | null {
  const storage = getStorage();
  return storage ? storage.getItem(STEAM_ID_KEY) : null;
}

export function clearToken() {
  const storage = getStorage();
  if (storage) {
    storage.removeItem(TOKEN_KEY);
    storage.removeItem(STEAM_ID_KEY);
  }
}
