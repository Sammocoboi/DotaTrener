import { useEffect, useState } from "react";
import { View, Text, FlatList, Pressable, ScrollView, Platform } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import * as WebBrowser from "expo-web-browser";
import axios from "axios";
import { getToken, saveToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { API_BASE as API, API_ROOT } from "@/lib/api";


type Match = {
  match_id: string;
  hero: string;
  result: "win" | "loss";
  side: string;
  duration: number;
  kda: string;
  gpm: number;
  xpm: number;
  created: boolean;
};

export default function MatchesScreen() {
  const params = useLocalSearchParams<{ token: string; steam_id: string }>();
  const token = params.token || getToken();
  const [matches, setMatches] = useState<Match[]>([]);
  const [record, setRecord] = useState({ wins: 0, losses: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMatches = async () => {
    setLoading(true);
    setError(null);
    const tok = token || getToken();
    try {
      const res = await axios.get(`${API}/my-matches/?limit=20`, {
        headers: tok ? { Authorization: `Token ${tok}` } : {},
      });
      setMatches(res.data.matches);
      setRecord({ wins: res.data.wins || 0, losses: res.data.losses || 0 });
    } catch (e: any) {
      setError(e?.response?.data?.error || "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!token && !getToken()) {
      router.replace("/login");
      return;
    }
    fetchMatches();
  }, []);

  if (error) {
    return (
      <View style={{ flex: 1, padding: 16, backgroundColor: colors.bg }}>
        <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
          <Text style={{ color: colors.orange }}>← Назад</Text>
        </Pressable>
        <View style={{ flex: 1, justifyContent: "center", alignItems: "center", gap: 12 }}>
          <Text style={{ color: colors.red }}>{error}</Text>
          <Pressable
            onPress={async () => {
              const url = `${API_ROOT}/api/auth/steam/login/?next=matches`;
              if (Platform.OS === "web") {
                window.location.href = url;
              } else {
                const result = await WebBrowser.openAuthSessionAsync(url, "dotatrener://auth-callback");
                if (result?.type === "success" && result.url) {
                  const params = new URL(result.url).searchParams;
                  const t = params.get("token");
                  const s = params.get("steam_id");
                  if (t) { saveToken(t, s); router.replace("/profile"); }
                }
              }
            }}
            style={{ backgroundColor: colors.orange, padding: 12, borderRadius: 8 }}
          >
            <Text style={{ color: colors.text, fontWeight: "600" }}>Войти через Steam</Text>
          </Pressable>
          <Pressable
            onPress={() => router.push({ pathname: "stratz-token" as any, params: { token: token || "" } })}
            style={{ backgroundColor: colors.bgElevated, padding: 12, borderRadius: 8 }}
          >
            <Text style={{ color: colors.orange, fontWeight: "600" }}>Ввести Stratz токен</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  const winRate = record.wins + record.losses > 0
    ? ((record.wins / (record.wins + record.losses)) * 100).toFixed(0)
    : "—";

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
          <Text style={{ color: colors.orange }}>← Назад</Text>
        </Pressable>

        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700" }}>Мои матчи</Text>
          <View style={{ flexDirection: "row", gap: 12 }}>
            <Text style={{ color: colors.greenLight, fontSize: 13, fontWeight: "600" }}>{record.wins}W</Text>
            <Text style={{ color: colors.redLight, fontSize: 13, fontWeight: "600" }}>{record.losses}L</Text>
            <Text style={{ color: colors.text80, fontSize: 13, fontWeight: "600" }}>{winRate}%</Text>
          </View>
        </View>

        {loading ? (
          <Text style={{ color: colors.text60 }}>Загрузка...</Text>
        ) : matches.length === 0 ? (
          <Text style={{ color: colors.text60 }}>Нет матчей</Text>
        ) : (
          matches.map((item) => {
            const mins = Math.floor(item.duration / 60);
            const secs = item.duration % 60;
            const resColor = item.result === "win" ? colors.green : colors.red;
            const resBg = item.result === "win" ? "rgba(16,185,129,0.1)" : "rgba(239,68,68,0.1)";
            return (
              <Pressable
                key={item.match_id}
                onPress={() =>
                  router.push({
                    pathname: "match-detail" as any,
                    params: { token, match_id: item.match_id },
                  })
                }
                style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 10, borderWidth: 1, borderColor: colors.borderSoft, overflow: "hidden" }}
              >
                <View style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, backgroundColor: resColor, borderTopLeftRadius: 14, borderBottomLeftRadius: 14 }} />
                <View style={{ marginLeft: 4 }}>
                  <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                    <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
                      <View style={{ backgroundColor: resBg, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 4 }}>
                        <Text style={{ color: resColor, fontSize: 11, fontWeight: "700", letterSpacing: 0.5 }}>{item.result === "win" ? "VICTORY" : "DEFEAT"}</Text>
                      </View>
                      <Text style={{ color: colors.text, fontSize: 15, fontWeight: "600" }}>{item.hero}</Text>
                    </View>
                    <Text style={{ color: colors.text40, fontSize: 11 }}>{item.side}</Text>
                  </View>
                  <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
                    <Text style={{ color: colors.text60, fontSize: 12 }}>{item.kda}</Text>
                    <Text style={{ color: colors.text60, fontSize: 12 }}>{mins}:{String(secs).padStart(2, "0")}</Text>
                  </View>
                  <View style={{ flexDirection: "row", gap: 16, marginTop: 4 }}>
                    <Text style={{ color: colors.text40, fontSize: 11 }}>GPM {item.gpm}</Text>
                    <Text style={{ color: colors.text40, fontSize: 11 }}>XPM {item.xpm}</Text>
                  </View>
                </View>
              </Pressable>
            );
          })
        )}
      </ScrollView>
    </View>
  );
}
