import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, Image } from "react-native";
import { router } from "expo-router";
import axios from "axios";

const API = "http://127.0.0.1:8000/api/coaching";

type CoachItem = {
  id: number;
  username: string;
  title: string;
  specialization: string;
  bio: string;
  rating: number;
  mmr_verified: number;
  service_count: number;
  min_price: number | null;
};

function rankLabel(v: number): string {
  if (v <= 0) return "Uncalibrated";
  if (v >= 80) return "Immortal";
  const medals = ["", "Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine"];
  const mid = Math.floor(v / 10);
  const star = v % 10;
  return mid >= 1 && mid <= 7 ? `${medals[mid]} ${star}` : `Rank ${v}`;
}

export default function CoachesScreen() {
  const [coaches, setCoaches] = useState<CoachItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/coaches/`)
      .then(r => setCoaches(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#0B1120" }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
        <Text style={{ color: "#60A5FA" }}>← Главная</Text>
      </Pressable>

      <Text style={{ color: "#FFF", fontSize: 22, fontWeight: "700", marginBottom: 16 }}>Тренеры</Text>

      {loading && <Text style={{ color: "#64748B" }}>Загрузка...</Text>}
      {!loading && coaches.length === 0 && <Text style={{ color: "#64748B" }}>Нет тренеров</Text>}

      {coaches.map(c => (
        <Pressable
          key={c.id}
          onPress={() => router.push({ pathname: "coach-detail" as any, params: { coach_id: String(c.id) } })}
          style={{ backgroundColor: "#0F1729", borderRadius: 10, padding: 12, marginBottom: 10, borderWidth: 1, borderColor: "rgba(255,255,255,0.05)" }}
        >
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
            <View style={{ flex: 1 }}>
              <Text style={{ color: "#60A5FA", fontSize: 14, fontWeight: "600" }}>{c.title || c.username}</Text>
              <Text style={{ color: "#94A3B8", fontSize: 11, marginTop: 2 }}>{c.specialization}</Text>
              <Text style={{ color: "#64748B", fontSize: 10, marginTop: 4 }} numberOfLines={2}>{c.bio}</Text>
            </View>
            <View style={{ alignItems: "flex-end", marginLeft: 8 }}>
              <Text style={{ color: "#F59E0B", fontSize: 10 }}>{rankLabel(c.mmr_verified)}</Text>
              <Text style={{ color: "#22C55E", fontSize: 11, fontWeight: "600", marginTop: 4 }}>★ {c.rating.toFixed(1)}</Text>
            </View>
          </View>
          <View style={{ flexDirection: "row", marginTop: 8, gap: 8 }}>
            <Text style={{ color: "#64748B", fontSize: 10 }}>{c.service_count} услуг</Text>
            {c.min_price != null && <Text style={{ color: "#A5B4FC", fontSize: 10 }}>от {"$"}{c.min_price.toFixed(0)}</Text>}
          </View>
        </Pressable>
      ))}
    </ScrollView>
  );
}
