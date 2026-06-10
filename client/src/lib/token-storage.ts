import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "dota_trener_token";
const STEAM_ID_KEY = "dota_trener_steam_id";

let _token: string | null = null;
let _steamId: string | null = null;

function isWeb(): boolean {
  try {
    return typeof window !== "undefined" && window.localStorage !== undefined;
  } catch {
    return false;
  }
}

export async function initToken() {
  if (isWeb()) {
    _token = window.localStorage.getItem(TOKEN_KEY);
    _steamId = window.localStorage.getItem(STEAM_ID_KEY);
  } else {
    try {
      _token = await SecureStore.getItemAsync(TOKEN_KEY);
      _steamId = await SecureStore.getItemAsync(STEAM_ID_KEY);
    } catch {}
  }
}

export function saveToken(token: string, steam_id?: string) {
  _token = token;
  if (steam_id) _steamId = steam_id;
  if (isWeb()) {
    window.localStorage.setItem(TOKEN_KEY, token);
    if (steam_id) window.localStorage.setItem(STEAM_ID_KEY, steam_id);
  } else {
    SecureStore.setItemAsync(TOKEN_KEY, token);
    if (steam_id) SecureStore.setItemAsync(STEAM_ID_KEY, steam_id);
  }
}

export function getToken(): string | null {
  return _token;
}

export function getSteamId(): string | null {
  return _steamId;
}

export function clearToken() {
  _token = null;
  _steamId = null;
  if (isWeb()) {
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(STEAM_ID_KEY);
  } else {
    SecureStore.deleteItemAsync(TOKEN_KEY);
    SecureStore.deleteItemAsync(STEAM_ID_KEY);
  }
}
