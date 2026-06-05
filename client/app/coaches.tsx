import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, Image } from "react-native";
import { router } from "expo-router";
import axios from "axios";
import { rankLabel, rankIconUrl } from "@/lib/rank-label";
import { colors } from "@/lib/theme";
import { API_BASE as API } from "@/lib/api";


type CoachItem = {
  id: number;
  username: string;
  avatar_url: string;
  title: string;
  specialization: string;
  bio: string;
  rating: number;
  mmr_verified: number;
  service_count?: number;
  min_price?: number;
};

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
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
        <Text style={{ color: colors.orange }}>← Назад</Text>
      </Pressable>

      <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginBottom: 16 }}>Тренеры</Text>

      {loading && <Text style={{ color: colors.text60 }}>Загрузка...</Text>}
      {!loading && coaches.length === 0 && <Text style={{ color: colors.text60 }}>Нет тренеров</Text>}

      {coaches.map(c => (
        <Pressable
          key={c.id}
          onPress={() => router.push({ pathname: "coach-detail" as any, params: { coach_id: String(c.id) } })}
          style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 10, borderWidth: 1, borderColor: colors.borderSoft }}
        >
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
            <View style={{ flexDirection: "row", alignItems: "center", flex: 1, gap: 12 }}>
              {c.avatar_url ? (
                <Image source={{ uri: c.avatar_url }} style={{ width: 40, height: 40, borderRadius: 20, backgroundColor: colors.bgElevated }} />
              ) : (
                <View style={{ width: 40, height: 40, borderRadius: 20, backgroundColor: colors.bgElevated, alignItems: "center", justifyContent: "center" }}>
                  <Text style={{ color: colors.text40, fontSize: 14 }}>?</Text>
                </View>
              )}
              <View style={{ flex: 1 }}>
                <Text style={{ color: colors.orange, fontSize: 14, fontWeight: "600" }}>{c.title || c.username}</Text>
                <Text style={{ color: colors.text60, fontSize: 11, marginTop: 2 }}>{c.specialization}</Text>
                <Text style={{ color: colors.text40, fontSize: 10, marginTop: 4 }} numberOfLines={2}>{c.bio}</Text>
              </View>
            </View>
            <View style={{ alignItems: "flex-end", marginLeft: 8 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
                {rankIconUrl(c.mmr_verified) ? <Image source={{ uri: rankIconUrl(c.mmr_verified) }} style={{ width: 20, height: 20 }} /> : null}
                <Text style={{ color: colors.orange, fontSize: 10 }}>{rankLabel(c.mmr_verified)}</Text>
              </View>
              <Text style={{ color: colors.green, fontSize: 11, fontWeight: "600", marginTop: 4 }}>★ {c.rating.toFixed(1)}</Text>
            </View>
          </View>
          <View style={{ flexDirection: "row", marginTop: 8, gap: 8 }}>
            <Text style={{ color: colors.text40, fontSize: 10 }}>{c.service_count} услуг</Text>
            {c.min_price != null && <Text style={{ color: colors.purpleLight, fontSize: 10 }}>от {"$"}{c.min_price.toFixed(0)}</Text>}
          </View>
        </Pressable>
      ))}
    </ScrollView>
  );
}
