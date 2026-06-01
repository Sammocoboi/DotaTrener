import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, Image } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";

const API = "http://127.0.0.1:8000/api/coaching";

type PlayerData = {
  hero_id: number;
  hero_name: string;
  hero_image: string;
  is_radiant: boolean;
  kills: number;
  deaths: number;
  assists: number;
  gpm: number;
  xpm: number;
  last_hits: number;
  denies: number;
  hero_damage: number;
  tower_damage: number;
  networth: number;
  items: { id: number; name: string; image: string }[];
};

type MatchDetail = {
  match_id: string;
  duration: number;
  radiant_win: boolean;
  start_time: number;
  players: PlayerData[];
};

export default function MatchDetailScreen() {
  const { token, match_id } = useLocalSearchParams<{ token: string; match_id: string }>();
  const [data, setData] = useState<MatchDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!match_id) return;
    setLoading(true);
    axios
      .get(`${API}/match/${match_id}/`, {
        headers: token ? { Authorization: `Token ${token}` } : {},
      })
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [match_id]);

  if (loading) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}><Text>Загрузка...</Text></View>;
  if (!data) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}><Text>Матч не найден</Text></View>;

  const mins = Math.floor(data.duration / 60);
  const secs = data.duration % 60;
  const radiant = data.players.filter((p) => p.is_radiant);
  const dire = data.players.filter((p) => !p.is_radiant);

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#0B1120" }}>
      <View style={{ padding: 16 }}>
        <Pressable onPress={() => router.back()}>
          <Text style={{ color: "#60A5FA", marginBottom: 12 }}>← Назад</Text>
        </Pressable>

        <Text style={{ color: "#FFF", fontSize: 20, fontWeight: "700" }}>
          Match {data.match_id}
        </Text>
        <Text style={{ color: "#94A3B8", marginBottom: 16 }}>
          {mins}:{String(secs).padStart(2, "0")} |{" "}
          {data.radiant_win ? "Radiant Victory" : "Dire Victory"}
        </Text>

        <TeamBlock label="RADIANT" won={data.radiant_win} players={radiant} />
        <View style={{ height: 16 }} />
        <TeamBlock label="DIRE" won={!data.radiant_win} players={dire} />
      </View>
    </ScrollView>
  );
}

function TeamBlock({ label, won, players }: { label: string; won: boolean; players: PlayerData[] }) {
  return (
    <View>
      <Text style={{ color: won ? "#22C55E" : "#EF4444", fontWeight: "700", marginBottom: 8 }}>
        {label} {won ? "WIN" : "LOSS"}
      </Text>
      {players.map((p, i) => (
        <View key={i} style={{ flexDirection: "row", alignItems: "center", paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: "rgba(255,255,255,0.05)", gap: 8 }}>
          {p.hero_image ? (
            <Image source={{ uri: p.hero_image }} style={{ width: 36, height: 36, borderRadius: 6 }} />
          ) : (
            <View style={{ width: 36, height: 36, borderRadius: 6, backgroundColor: "#1E293B" }} />
          )}
          <View style={{ flex: 1 }}>
            <Text style={{ color: "#FFF", fontSize: 13, fontWeight: "600" }}>
              {p.hero_name || `Hero ${p.hero_id}`}
            </Text>
            <Text style={{ color: "#94A3B8", fontSize: 11 }}>
              {p.kills}/{p.deaths}/{p.assists} | LH/DN {p.last_hits}/{p.denies}
            </Text>
          </View>
          <View style={{ alignItems: "flex-end" }}>
            <Text style={{ color: "#CBD5E1", fontSize: 12 }}>GPM {p.gpm}</Text>
            <Text style={{ color: "#CBD5E1", fontSize: 12 }}>XPM {p.xpm}</Text>
          </View>
          <View style={{ alignItems: "flex-end" }}>
            <Text style={{ color: "#CBD5E1", fontSize: 11 }}>DMG {p.hero_damage}</Text>
            <Text style={{ color: "#CBD5E1", fontSize: 11 }}>TD {p.tower_damage}</Text>
          </View>
          <View style={{ flexDirection: "row", gap: 4, flexWrap: "wrap" }}>
            {p.items.map((item, idx) =>
              item.image ? (
                <Image key={idx} source={{ uri: item.image }} style={{ width: 32, height: 32, borderRadius: 4 }} />
              ) : (
                <View key={idx} style={{ width: 32, height: 32, borderRadius: 4, backgroundColor: "#1E293B" }} />
              )
            )}
          </View>
        </View>
      ))}
    </View>
  );
}
