import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, TextInput, Image, Linking } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { rankLabel, rankIconUrl } from "@/lib/rank-label";
import { colors } from "@/lib/theme";
import { API_BASE as API } from "@/lib/api";


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
  avatar_url: string;
  title: string;
  specialization: string;
  bio: string;
  rating: number;
  mmr_verified: number;
  social_links: Record<string, string>;
  services: Service[];
};

export default function CoachDetailScreen() {
  const params = useLocalSearchParams<{ coach_id: string; token?: string }>();
  const coach_id = params.coach_id;
  const token = params.token || getToken();
  const [coach, setCoach] = useState<CoachDetail | null>(null);
  const [loading, setLoading] = useState(true);
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

  const openLink = (url: string) => {
    const fullUrl = url.startsWith("http") ? url : `https://${url}`;
    if (typeof window !== "undefined") window.open(fullUrl, "_blank");
  };

  if (loading) return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", alignItems: "center" }}><Text style={{ color: colors.text60 }}>Загрузка...</Text></View>;
  if (!coach) return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", alignItems: "center" }}><Text style={{ color: colors.red }}>Тренер не найден</Text></View>;

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
        <Text style={{ color: colors.orange }}>← Назад</Text>
      </Pressable>

      <View style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: colors.borderSoft }}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 12 }}>
          {coach.avatar_url ? (
            <Image source={{ uri: coach.avatar_url }} style={{ width: 56, height: 56, borderRadius: 28, backgroundColor: colors.bgElevated }} />
          ) : (
            <View style={{ width: 56, height: 56, borderRadius: 28, backgroundColor: colors.bgElevated, alignItems: "center", justifyContent: "center" }}>
              <Text style={{ color: colors.text40, fontSize: 20 }}>?</Text>
            </View>
          )}
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700" }}>{coach.title || coach.username}</Text>
            <Text style={{ color: colors.text60, fontSize: 12, marginTop: 2 }}>{coach.specialization}</Text>
          </View>
        </View>

        <View style={{ flexDirection: "row", gap: 12, marginBottom: 12 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 4, backgroundColor: colors.bgRow, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6 }}>
            {rankIconUrl(coach.mmr_verified) ? <Image source={{ uri: rankIconUrl(coach.mmr_verified) }} style={{ width: 18, height: 18 }} /> : null}
            <Text style={{ color: colors.orange, fontSize: 12 }}>{rankLabel(coach.mmr_verified)}</Text>
          </View>
          <View style={{ backgroundColor: colors.bgRow, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6 }}>
            <Text style={{ color: colors.greenLight, fontSize: 12 }}>★ {coach.rating.toFixed(1)}</Text>
          </View>
        </View>

        <Text style={{ color: colors.text80, fontSize: 12, lineHeight: 18 }}>{coach.bio}</Text>
      </View>

      {Object.keys(coach.social_links).length > 0 && (
        <View style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: colors.borderSoft }}>
          <Text style={{ color: colors.text60, fontSize: 11, fontWeight: "600", letterSpacing: 1, marginBottom: 8 }}>СОЦСЕТИ</Text>
          <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
            {Object.entries(coach.social_links).map(([key, value]) => (
              <Pressable key={key} onPress={() => openLink(value)} style={{ backgroundColor: colors.bgElevated, paddingHorizontal: 10, paddingVertical: 5, borderRadius: 6 }}>
                <Text style={{ color: colors.orange, fontSize: 11 }}>{key}: {value}</Text>
              </Pressable>
            ))}
          </View>
        </View>
      )}

      <Text style={{ color: colors.text60, fontSize: 11, fontWeight: "600", letterSpacing: 1, marginBottom: 10 }}>УСЛУГИ</Text>

      {coach.services.length === 0 && <Text style={{ color: colors.text60 }}>Нет услуг</Text>}

      {coach.services.filter(s => s.is_active).map(svc => (
        <View key={svc.id} style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 10, borderWidth: 1, borderColor: colors.borderSoft }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
            <Text style={{ color: colors.text, fontSize: 14, fontWeight: "600", flex: 1 }}>{svc.title}</Text>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
              <Text style={{ color: colors.purpleLight, fontSize: 14, fontWeight: "700"}}>{"$"}{svc.price}</Text>
              <Text style={{ color: colors.text40, fontSize: 10 }}>/{svc.duration_minutes}мин</Text>
            </View>
          </View>
          <Text style={{ color: colors.text60, fontSize: 11, marginTop: 4 }}>{svc.description}</Text>
          <Pressable
            onPress={() => {
              axios.post(`${API}/conversations/`, { coach_id: coach.id, service_id: svc.id, message: "Здравствуйте! Хочу записаться на эту услугу." }, { headers })
                .then(r => router.push({ pathname: "chat" as any, params: { conv_id: String(r.data.id), token: token || "" } }))
                .catch(() => {});
            }}
            style={{ backgroundColor: colors.orange, padding: 8, borderRadius: 6, marginTop: 8, alignItems: "center" }}
          >
            <Text style={{ color: colors.text, fontSize: 11, fontWeight: "600" }}>Связаться</Text>
          </Pressable>
        </View>
      ))}
    </ScrollView>
  );
}
