import { useEffect, useState } from "react";
import { View, Text, FlatList, Button, Pressable } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";

const API = "http://127.0.0.1:8000/api/coaching";

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
  const { token, steam_id } = useLocalSearchParams<{ token: string; steam_id: string }>();
  const [matches, setMatches] = useState<Match[]>([]);
  const [record, setRecord] = useState({ wins: 0, losses: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMatches = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API}/my-matches/?limit=20`, {
        headers: token ? { Authorization: `Token ${token}` } : {},
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
    fetchMatches();
  }, []);

  if (error) {
    return (
      <View style={{ flex: 1, padding: 16, justifyContent: "center", alignItems: "center", gap: 12 }}>
        <Text>{error}</Text>
        <Button title="Войти через Steam" onPress={() => router.push("steam-link" as any)} />
        <Button title="Ввести Stratz токен" onPress={() => router.push({ pathname: "stratz-token" as any, params: { token: token || "" } })} />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 18, fontWeight: "700", marginBottom: 4 }}>Мои матчи</Text>
      <Text style={{ color: "#666", marginBottom: 12 }}>
        {record.wins}W / {record.losses}L
      </Text>
      {loading ? (
        <Text>Загрузка...</Text>
      ) : (
        <FlatList
          data={matches}
          keyExtractor={(item) => item.match_id}
          renderItem={({ item }) => {
            const mins = Math.floor(item.duration / 60);
            const secs = item.duration % 60;
            const color = item.result === "win" ? "#22C55E" : "#EF4444";
            return (
              <Pressable
                onPress={() =>
                  router.push({
                    pathname: "match-detail" as any,
                    params: { token, match_id: item.match_id },
                  })
                }
                style={{
                  paddingVertical: 10,
                  borderBottomWidth: 1,
                  borderBottomColor: "#eee",
                }}
              >
                <Text style={{ fontWeight: "bold", color }}>
                  {item.result.toUpperCase()} - {item.hero}
                </Text>
                <Text style={{ fontSize: 13 }}>
                  {item.side} | {mins}:{String(secs).padStart(2, "0")} | {item.kda} | GPM {item.gpm} | XPM {item.xpm}
                </Text>
              </Pressable>
            );
          }}
        />
      )}
    </View>
  );
}
