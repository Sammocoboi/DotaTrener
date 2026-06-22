import { useEffect, useState } from "react";
import { View, Text, Pressable, Platform } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import * as WebBrowser from "expo-web-browser";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { API_ROOT as API } from "@/lib/api";


export default function SteamLink() {
  const params = useLocalSearchParams<{ token: string; steam_id: string; next: string }>();
  const token = params.token || getToken();
  const steam_id = params.steam_id;
  const next = params.next || "matches";
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token && steam_id) {
      router.replace({ pathname: "matches" as any, params: { token, steam_id } });
    }
  }, [token]);

  const loginWithSteam = async () => {
    const url = `${API}/api/auth/steam/login/${next ? `?next=${next}` : ""}`;
    if (Platform.OS === "web") {
      window.location.href = url;
      return;
    }
    setLoading(true);
    try {
      const result = await WebBrowser.openAuthSessionAsync(url, "dotatrener://auth-callback");
      if (result?.type === "success" && result.url) {
        const params = new URL(result.url).searchParams;
        const t = params.get("token");
        const s = params.get("steam_id");
        if (t) {
          await saveToken(t, s);
          router.replace({ pathname: "matches" as any, params: { token: t, steam_id: s || "" } });
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1, padding: 16, backgroundColor: colors.bg }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 16 }}>
        <Text style={{ color: colors.orange }}>← Назад</Text>
      </Pressable>
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", gap: 16 }}>
        <Text style={{ color: colors.text80, fontSize: 15, textAlign: "center" }}>Войдите через Steam для синхронизации матчей</Text>
        <Pressable
          onPress={loginWithSteam}
          disabled={loading}
          style={{ backgroundColor: colors.orange, paddingHorizontal: 24, paddingVertical: 14, borderRadius: 10 }}
        >
          <Text style={{ color: colors.text, fontWeight: "700", fontSize: 15 }}>
            {loading ? "Открываю Steam..." : "Войти через Steam"}
          </Text>
        </Pressable>
      </View>
    </View>
  );
}
