import { useEffect, useState } from "react";
import { Stack, router } from 'expo-router';
import { Platform } from "react-native";
import { colors } from '@/lib/theme';
import { initToken, getToken, saveToken } from '@/lib/token-storage';

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

export default function Layout() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
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

      if (!getToken()) {
        router.replace("/login");
      }
      setReady(true);
    });
  }, []);

  return <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.bg } }} />;
}
