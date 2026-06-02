import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, TextInput } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";

const API = "http://127.0.0.1:8000/api/coaching";

type ProfileData = {
  user: { id: number; username: string; date_joined: string };
  player: {
    steam_account_id: number | null;
    steam_id_64: number | null;
    stratz_token: boolean;
    current_mmr: number;
    peak_mmr: number;
    favorite_role: string | null;
    is_coach: boolean;
  };
  coach: {
    specialization: string;
    bio: string;
    rating: number;
    mmr_verified: number;
    mmr_verified_at: string | null;
  } | null;
  rank: {
    season_rank: number;
    leaderboard_rank: number | null;
    season_rank_label: string;
    is_immortal: boolean;
  } | null;
};

export default function ProfileScreen() {
  const { token } = useLocalSearchParams<{ token: string }>();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [registering, setRegistering] = useState(false);
  const [appStatus, setAppStatus] = useState<{ id: number; status: string; message: string; created_at: string; reviewed_at?: string } | null>(null);
  const [appMessage, setAppMessage] = useState("");

  const headers = token ? { Authorization: `Token ${token}` } : {};

  const loadAll = () => {
    if (!token) return;
    setLoading(true);
    Promise.all([
      axios.get(`${API}/profile/`, { headers }),
      axios.get(`${API}/my-application/`, { headers }).catch(() => ({ data: { application: null } })),
    ])
      .then(([pRes, aRes]) => {
        setProfile(pRes.data);
        setAppStatus(aRes.data?.application || null);
      })
      .catch((e) => setError(e?.response?.data?.error || "Ошибка загрузки"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadAll(); }, [token]);

  const handleBecomeCoach = async () => {
    setRegistering(true);
    try {
      const res = await axios.post(`${API}/become-coach/`, { message: appMessage }, { headers });
      if (res.data.ok) {
        setAppStatus(res.data.application);
        setAppMessage("");
      }
    } catch (e: any) {
      setError(e?.response?.data?.error || "Ошибка регистрации тренером");
    } finally {
      setRegistering(false);
    }
  };

  if (loading) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#0B1120" }}><Text style={{ color: "#94A3B8" }}>Загрузка...</Text></View>;
  if (!token) return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 16, backgroundColor: "#0B1120" }}>
      <Text style={{ color: "#94A3B8", marginBottom: 8 }}>Войдите через Steam</Text>
      <Pressable onPress={() => (typeof window !== "undefined" ? (window.location.href = "http://127.0.0.1:8000/api/auth/steam/login/") : null)} style={{ backgroundColor: "#3B82F6", padding: 12, borderRadius: 8 }}>
        <Text style={{ color: "#FFF", fontWeight: "600" }}>Войти через Steam</Text>
      </Pressable>
    </View>
  );

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#0B1120" }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
        <Text style={{ color: "#60A5FA" }}>← Главная</Text>
      </Pressable>

      <Text style={{ color: "#FFF", fontSize: 22, fontWeight: "700", marginBottom: 16 }}>Аккаунт</Text>

      {error && <Text style={{ color: "#EF4444", fontSize: 12, marginBottom: 8 }}>{error}</Text>}

      {profile && (
        <>
          <Section title="Steam">
            <Row label="Username" value={profile.user.username} />
            <Row label="Steam ID" value={profile.player.steam_account_id ? String(profile.player.steam_account_id) : "Не привязан"} />
          </Section>

          {profile.rank && (
            <Section title="Ранг">
              <Row label="Ранг" value={profile.rank.season_rank_label} />
              <Row label="Rank ID" value={String(profile.rank.season_rank)} />
              {profile.rank.leaderboard_rank && <Row label="Leaderboard" value={`#${profile.rank.leaderboard_rank}`} />}
            </Section>
          )}

          <Section title="Тренер">
            {profile.player.is_coach && profile.coach ? (
              <>
                <Row label="Рейтинг" value={`${profile.coach.rating.toFixed(1)} / 5.0`} />
                <Row label="MMR на проверке" value={String(profile.coach.mmr_verified)} />
                <Row label="Специализация" value={profile.coach.specialization || "—"} />
                <Row label="Bio" value={profile.coach.bio || "—"} />
                <Pressable
                  onPress={() => router.push({ pathname: "my-services" as any, params: { token } })}
                  style={{ backgroundColor: "#1E293B", padding: 10, borderRadius: 6, marginTop: 8, alignItems: "center" }}
                >
                  <Text style={{ color: "#60A5FA", fontSize: 12, fontWeight: "600" }}>Мои услуги</Text>
                </Pressable>
              </>
            ) : appStatus ? (
              <>
                <Text style={{ color: "#F59E0B", fontSize: 12 }}>Заявка отправлена</Text>
                <Text style={{ color: "#64748B", fontSize: 11, marginTop: 2 }}>
                  Статус: {
                    appStatus.status === "pending" ? "На рассмотрении" :
                    appStatus.status === "accepted" ? "Принята" :
                    appStatus.status === "rejected" ? "Отклонена" : appStatus.status
                  }
                </Text>
                {appStatus.message ? <Text style={{ color: "#94A3B8", fontSize: 10, marginTop: 4, fontStyle: "italic" }}>"{appStatus.message}"</Text> : null}
              </>
            ) : (
              <>
                <Text style={{ color: "#64748B", fontSize: 12, marginBottom: 8 }}>Ты ещё не тренер. Отправь заявку!</Text>
                <TextInput
                  style={{ backgroundColor: "#1E293B", color: "#CBD5E1", fontSize: 12, padding: 8, borderRadius: 6, marginBottom: 8, minHeight: 60, borderWidth: 1, borderColor: "rgba(255,255,255,0.08)" }}
                  placeholder="Расскажи почему хочешь стать тренером (опыт, ранг, специализация)..."
                  placeholderTextColor="#475569"
                  multiline
                  value={appMessage}
                  onChangeText={setAppMessage}
                />
                <Pressable onPress={handleBecomeCoach} disabled={registering || !appMessage.trim()} style={{ backgroundColor: appMessage.trim() ? "#059669" : "#1E293B", padding: 12, borderRadius: 8, alignItems: "center" }}>
                  <Text style={{ color: appMessage.trim() ? "#FFF" : "#475569", fontWeight: "600" }}>{registering ? "Отправка..." : "Отправить заявку"}</Text>
                </Pressable>
              </>
            )}
          </Section>

          <Section title="Настройки">
            <Pressable
              onPress={() => router.push({ pathname: "stratz-token" as any, params: { token } })}
              style={{ backgroundColor: "#1E293B", padding: 12, borderRadius: 8, marginBottom: 8 }}
            >
              <Text style={{ color: profile.player.stratz_token ? "#22C55E" : "#94A3B8" }}>
                Stratz API токен: {profile.player.stratz_token ? "Установлен" : "Не установлен"}
              </Text>
            </Pressable>
            {profile.user.is_staff && (
              <Pressable
                onPress={() => router.push({ pathname: "admin-applications" as any, params: { token } })}
                style={{ backgroundColor: "#1E293B", padding: 12, borderRadius: 8 }}
              >
                <Text style={{ color: "#F59E0B" }}>Заявки тренеров (админ)</Text>
              </Pressable>
            )}
          </Section>
        </>
      )}
    </ScrollView>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={{ backgroundColor: "#0F1729", borderRadius: 8, padding: 12, marginBottom: 12 }}>
      <Text style={{ color: "#94A3B8", fontSize: 13, fontWeight: "600", marginBottom: 8 }}>{title}</Text>
      {children}
    </View>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 4 }}>
      <Text style={{ color: "#64748B", fontSize: 12 }}>{label}</Text>
      <Text style={{ color: "#CBD5E1", fontSize: 12 }}>{value}</Text>
    </View>
  );
}
