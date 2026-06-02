import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, Alert, TextInput } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";

const API = "http://127.0.0.1:8000/api/coaching";

type Service = {
  id: number;
  title: string;
  description: string;
  price: string;
  duration_minutes: number;
  is_active: boolean;
};

type CoachDetail = {
  id: number;
  username: string;
  title: string;
  specialization: string;
  bio: string;
  rating: number;
  mmr_verified: number;
  services: Service[];
};

function rankLabel(v: number): string {
  if (v <= 0) return "Uncalibrated";
  if (v >= 80) return "Immortal";
  const medals = ["", "Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine"];
  const mid = Math.floor(v / 10);
  const star = v % 10;
  return mid >= 1 && mid <= 7 ? `${medals[mid]} ${star}` : `Rank ${v}`;
}

export default function CoachDetailScreen() {
  const { coach_id, token } = useLocalSearchParams<{ coach_id: string; token?: string }>();
  const [coach, setCoach] = useState<CoachDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Service | null>(null);
  const headers = token ? { Authorization: `Token ${token}` } : {};

  const load = () => {
    if (!coach_id) return;
    setLoading(true);
    axios.get(`${API}/coaches/${coach_id}/`)
      .then(r => setCoach(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [coach_id]);

  if (loading) return <View style={{ flex: 1, backgroundColor: "#0B1120", justifyContent: "center", alignItems: "center" }}><Text style={{ color: "#64748B" }}>Загрузка...</Text></View>;
  if (!coach) return <View style={{ flex: 1, backgroundColor: "#0B1120", justifyContent: "center", alignItems: "center" }}><Text style={{ color: "#EF4444" }}>Тренер не найден</Text></View>;

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#0B1120" }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push("/coaches")} style={{ marginBottom: 12 }}>
        <Text style={{ color: "#60A5FA" }}>← Все тренеры</Text>
      </Pressable>

      <Text style={{ color: "#FFF", fontSize: 20, fontWeight: "700" }}>{coach.title || coach.username}</Text>
      <Text style={{ color: "#94A3B8", fontSize: 12, marginTop: 2 }}>{coach.specialization}</Text>

      <View style={{ flexDirection: "row", gap: 12, marginTop: 8, marginBottom: 12 }}>
        <Text style={{ color: "#F59E0B", fontSize: 12 }}>{rankLabel(coach.mmr_verified)}</Text>
        <Text style={{ color: "#22C55E", fontSize: 12 }}>★ {coach.rating.toFixed(1)}</Text>
      </View>

      <Text style={{ color: "#CBD5E1", fontSize: 12, lineHeight: 18, marginBottom: 16 }}>{coach.bio}</Text>

      <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "600", marginBottom: 8 }}>Услуги</Text>

      {coach.services.length === 0 && <Text style={{ color: "#64748B" }}>Нет услуг</Text>}

      {coach.services.filter(s => s.is_active).map(svc => (
        <View key={svc.id} style={{ backgroundColor: "#0F1729", borderRadius: 8, padding: 12, marginBottom: 8, borderWidth: 1, borderColor: "rgba(255,255,255,0.05)" }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
            <Text style={{ color: "#FFF", fontSize: 14, fontWeight: "600", flex: 1 }}>{svc.title}</Text>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
              <Text style={{ color: "#A5B4FC", fontSize: 14, fontWeight: "700"}}>{"$"}{svc.price}</Text>
              <Text style={{ color: "#64748B", fontSize: 10 }}>/{svc.duration_minutes}мин</Text>
            </View>
          </View>
          <Text style={{ color: "#64748B", fontSize: 11, marginTop: 4 }}>{svc.description}</Text>
        </View>
      ))}
    </ScrollView>
  );
}
