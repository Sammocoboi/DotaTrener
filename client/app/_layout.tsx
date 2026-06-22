import { useEffect, useState } from "react";
import { Stack, router, useSegments } from 'expo-router';
import { Platform, Linking } from "react-native";
import { colors } from '@/lib/theme';
import { initToken, getToken, saveToken } from '@/lib/token-storage';

function handleDeepLink(url: string) {
  if (!url.startsWith("dotatrener://auth-callback")) return;
  const params = new URL(url).searchParams;
  const token = params.get("token");
  const steam_id = params.get("steam_id");
  if (token) {
    saveToken(token, steam_id);
    const next = params.get("next") || "profile";
    router.replace(next as any);
  }
}

function getUrlParams(): Record<string, string> {
  if (Platform.OS !== "web" || typeof window === "undefined") return {};
  const hash = window.location.hash;
  if (hash && hash.length > 1) {
    const params = new URLSearchParams(hash.substring(1));
    const result: Record<string, string> = {};
    params.forEach((v, k) => { result[k] = v; });
    return result;
  }
  const search = window.location.search;
  if (search && search.length > 1) {
    const params = new URLSearchParams(search.substring(1));
    const result: Record<string, string> = {};
    params.forEach((v, k) => { result[k] = v; });
    return result;
  }
  return {};
}

const publicRoutes = new Set(["login", "register", "auth-callback", "steam-link"]);

export default function Layout() {
  const [ready, setReady] = useState(false);
  const segments = useSegments();

  useEffect(() => {
    const sub = Linking.addEventListener("url", (event) => {
      if (event.url) handleDeepLink(event.url);
    });
    initToken().then(() => {
      const urlParams = getUrlParams();
      const urlToken = urlParams.token;
      const urlSteamId = urlParams.steam_id;
      const next = urlParams.next || "profile";

      if (urlToken) {
        saveToken(urlToken, urlSteamId);
        if (Platform.OS === "web") {
          window.history.replaceState({}, "", window.location.pathname);
        }
        setReady(true);
        router.replace("/profile");
        return;
      }

      setReady(true);
    });
    return () => sub.remove();
  }, []);

  useEffect(() => {
    if (!ready) return;
    if (getToken()) return;
    if (publicRoutes.has(segments[0])) return;
    router.replace("/login");
  }, [ready, segments]);

  return <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.bg } }} />;
}
