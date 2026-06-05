import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, Image } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { rankIconUrl } from "@/lib/rank-label";
import { API_BASE as API } from "@/lib/api";


type Match = {
  match_id: string;
  won: boolean;
  is_radiant: boolean;
  hero_name: string;
  hero_image: string;
  duration: number;
  kills: number;
  deaths: number;
  assists: number;
  gpm: number;
  xpm: number;
  networth: number;
  start_time: number;
};

type BestHero = {
  hero_id: number;
  hero_name: string;
  hero_image: string;
  games: number;
  wins: number;
  win_rate: number;
};

type PlayerProfile = {
  steam_account_id: number;
  nickname: string;
  avatar_url: string;
  season_rank: number;
  win_count: number;
  lose_count: number;
  match_count: number;
  win_rate: number;
  recent_matches: Match[];
  best_heroes: BestHero[];
};

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function timeAgo(unix: number): string {
  const diff = Math.floor(Date.now() / 1000) - unix;
  if (diff < 3600) return `${Math.floor(diff / 60)} мин. назад`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} ч. назад`;
  return `${Math.floor(diff / 86400)} дн. назад`;
}

export default function PlayerScreen() {
  const params = useLocalSearchParams<{ token: string; steam_id: string }>();
  const token = params.token || getToken();
  const steam_id = params.steam_id;
  const [data, setData] = useState<PlayerProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!steam_id) return;
    setLoading(true);
    axios
      .get(`${API}/player/${steam_id}/`, {
        headers: token ? { Authorization: `Token ${token}` } : {},
      })
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [steam_id]);

  if (loading)
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#1a1a2e" }}>
        <Text style={{ color: "#888" }}>Загрузка...</Text>
      </View>
    );
  if (!data)
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#1a1a2e" }}>
        <Text style={{ color: "#888" }}>Игрок не найден</Text>
      </View>
    );

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#1a1a2e" }}>
      <Pressable onPress={() => router.back()} style={{ padding: 16, paddingBottom: 0 }}>
        <Text style={{ color: colors.orange, fontWeight: "600" }}>← Назад</Text>
      </Pressable>

      <View style={{
        flexDirection: "row",
        alignItems: "center",
        padding: 16,
        paddingBottom: 20,
        gap: 16,
      }}>
        <View style={{ position: "relative" }}>
          {data.avatar_url ? (
            <Image source={{ uri: data.avatar_url }} style={{ width: 80, height: 80, borderRadius: 10, borderWidth: 3, borderColor: "#c9a84c" }} />
          ) : (
            <View style={{ width: 80, height: 80, borderRadius: 10, backgroundColor: "#2a2a4a", borderWidth: 3, borderColor: "#555" }} />
          )}
          {data.season_rank > 0 && (
            <Image
              source={{ uri: rankIconUrl(data.season_rank) }}
              style={{ width: 32, height: 32, position: "absolute", bottom: -8, right: -8, borderRadius: 4, borderWidth: 2, borderColor: "#1a1a2e" }}
            />
          )}
        </View>

        <View style={{ flex: 1 }}>
          <Text style={{ color: "#e0e0e0", fontSize: 22, fontWeight: "800" }} numberOfLines={1}>
            {data.nickname}
          </Text>
          <Text style={{ color: "#888", fontSize: 12, marginTop: 2 }}>
            [{String(data.steam_account_id).slice(-5)}]
          </Text>
        </View>
      </View>

      <View style={{
        flexDirection: "row",
        marginHorizontal: 16,
        marginBottom: 16,
        gap: 8,
      }}>
        <View style={{ flex: 1, backgroundColor: "#222240", borderRadius: 10, padding: 14, borderWidth: 1, borderColor: "#333" }}>
          <Text style={{ color: "#e0e0e0", fontSize: 26, fontWeight: "800" }}>{data.match_count.toLocaleString()}</Text>
          <Text style={{ color: "#888", fontSize: 11, marginTop: 2 }}>Матчей</Text>
          <View style={{ flexDirection: "row", gap: 2, marginTop: 8 }}>
            {Array.from({ length: Math.min(50, data.match_count) }).map((_, i) => (
              <View key={i} style={{ width: 3, height: 12, borderRadius: 1, backgroundColor: i < Math.round(data.match_count * data.win_rate / 100) ? "#4caf50" : "#f44336" }} />
            ))}
          </View>
        </View>

        <View style={{ flex: 1, backgroundColor: "#222240", borderRadius: 10, padding: 14, borderWidth: 1, borderColor: "#333" }}>
          <Text style={{ color: "#4caf50", fontSize: 26, fontWeight: "800" }}>{data.win_rate.toFixed(1)}%</Text>
          <Text style={{ color: "#888", fontSize: 11, marginTop: 2 }}>Процент побед</Text>
          <View style={{ flexDirection: "row", marginTop: 8, gap: 4 }}>
            <Text style={{ color: "#4caf50", fontSize: 11 }}>{data.win_count}</Text>
            <Text style={{ color: "#555", fontSize: 11 }}>-</Text>
            <Text style={{ color: "#f44336", fontSize: 11 }}>{data.lose_count}</Text>
          </View>
          <View style={{ height: 4, borderRadius: 2, backgroundColor: "#333", marginTop: 4, overflow: "hidden" }}>
            <View style={{ height: "100%", width: `${data.win_rate}%`, backgroundColor: "#4caf50", borderRadius: 2 }} />
          </View>
        </View>
      </View>

      {data.best_heroes.length > 0 && (
        <>
          <View style={{ marginHorizontal: 16, marginBottom: 8, marginTop: 4 }}>
            <Text style={{ color: "#888", fontSize: 11, fontWeight: "700", letterSpacing: 0.5 }}>ЛУЧШИЕ ГЕРОИ</Text>
          </View>

          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 8, marginLeft: 16 }}>
            {data.best_heroes.map((h) => (
              <View key={h.hero_id} style={{
                backgroundColor: "#222240",
                borderRadius: 10,
                padding: 10,
                marginRight: 10,
                width: 110,
                borderWidth: 1,
                borderColor: "#333",
              }}>
                <Image source={{ uri: h.hero_image }} style={{ width: 60, height: 34, borderRadius: 4, alignSelf: "center", backgroundColor: "#2a2a4a" }} />
                <Text style={{ color: "#ccc", fontSize: 10, fontWeight: "600", marginTop: 6, textAlign: "center" }} numberOfLines={1}>
                  {h.hero_name}
                </Text>
                <Text style={{ color: "#888", fontSize: 9, textAlign: "center", marginTop: 2 }}>
                  {h.games} игр · {h.win_rate}%
                </Text>
                <View style={{ height: 3, borderRadius: 2, backgroundColor: "#333", marginTop: 4, overflow: "hidden" }}>
                  <View style={{ height: "100%", width: `${h.win_rate}%`, backgroundColor: h.win_rate >= 55 ? "#4caf50" : "#c9a84c", borderRadius: 2 }} />
                </View>
              </View>
            ))}
          </ScrollView>
        </>
      )}

      <View style={{ marginHorizontal: 16, marginBottom: 8 }}>
        <Text style={{ color: "#888", fontSize: 11, fontWeight: "700", letterSpacing: 0.5 }}>МАТЧИ</Text>
      </View>

      {data.recent_matches.map((m, i) => (
        <Pressable
          key={i}
          onPress={() => router.push({ pathname: "/match-detail", params: { token, match_id: m.match_id } })}
          style={{
            flexDirection: "row",
            alignItems: "center",
            marginHorizontal: 16,
            marginBottom: 4,
            paddingVertical: 8,
            paddingHorizontal: 10,
            borderRadius: 8,
            backgroundColor: m.won ? "rgba(76,175,80,0.08)" : "rgba(244,67,54,0.08)",
            borderWidth: 1,
            borderColor: m.won ? "rgba(76,175,80,0.2)" : "rgba(244,67,54,0.2)",
          }}
        >
          <View style={{ width: 40, height: 40, borderRadius: 6, overflow: "hidden", backgroundColor: "#2a2a4a", marginRight: 10 }}>
            {m.hero_image ? (
              <Image source={{ uri: m.hero_image }} style={{ width: 40, height: 40 }} />
            ) : (
              <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
                <Text style={{ color: "#555", fontSize: 12 }}>?</Text>
              </View>
            )}
          </View>

          <View style={{ flex: 1 }}>
            <Text style={{ color: "#ccc", fontSize: 12, fontWeight: "600" }} numberOfLines={1}>
              {m.hero_name}
            </Text>
            <Text style={{ color: "#888", fontSize: 10, marginTop: 1 }}>
              {formatDuration(m.duration)} · {timeAgo(m.start_time)}
            </Text>
          </View>

          <View style={{ alignItems: "center", marginHorizontal: 10 }}>
            <Text style={{
              color: m.won ? "#4caf50" : "#f44336",
              fontSize: 14,
              fontWeight: "800",
            }}>
              {m.kills}/{m.deaths}/{m.assists}
            </Text>
          </View>

          <View style={{ alignItems: "flex-end", minWidth: 50 }}>
            <Text style={{ color: "#ccc", fontSize: 11, fontWeight: "700" }}>
              {m.gpm}
            </Text>
            <Text style={{ color: "#888", fontSize: 9 }}>GPM</Text>
          </View>

          <View style={{
            marginLeft: 8,
            paddingHorizontal: 6,
            paddingVertical: 3,
            borderRadius: 4,
            backgroundColor: m.won ? "rgba(76,175,80,0.2)" : "rgba(244,67,54,0.2)",
          }}>
            <Text style={{ color: m.won ? "#4caf50" : "#f44336", fontSize: 10, fontWeight: "700" }}>
              {m.won ? "WIN" : "LOSS"}
            </Text>
          </View>
        </Pressable>
      ))}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}
