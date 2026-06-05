import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, TextInput, Image } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { rankIconUrl } from "@/lib/rank-label";
import { API_BASE as API } from "@/lib/api";


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
    avatar_url: string;
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
  const params = useLocalSearchParams<{ token: string }>();
  const token = params.token || getToken();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [registering, setRegistering] = useState(false);
  const [appStatus, setAppStatus] = useState<{ id: number; status: string; message: string; created_at: string; reviewed_at?: string } | null>(null);
  const [appMessage, setAppMessage] = useState("");
  const [editName, setEditName] = useState("");
  const [editAvatar, setEditAvatar] = useState("");
  const [socialLinks, setSocialLinks] = useState<Record<string, string>>({});
  const [newSocialKey, setNewSocialKey] = useState("");
  const [newSocialVal, setNewSocialVal] = useState("");
  const [saving, setSaving] = useState(false);

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
        setEditName(pRes.data.user.username);
        setEditAvatar(pRes.data.player.avatar_url || "");
        setSocialLinks(pRes.data.coach?.social_links || {});
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

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.patch(`${API}/profile/`, { username: editName, avatar_url: editAvatar, social_links: socialLinks }, { headers });
      const res = await axios.get(`${API}/profile/`, { headers });
      setProfile(res.data);
      setSocialLinks(res.data.coach?.social_links || {});
    } catch (e: any) {
      setError(e?.response?.data?.error || "Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  };

  const addSocialLink = () => {
    if (!newSocialKey.trim() || !newSocialVal.trim()) return;
    setSocialLinks(prev => ({ ...prev, [newSocialKey.trim()]: newSocialVal.trim() }));
    setNewSocialKey("");
    setNewSocialVal("");
  };

  const removeSocialLink = (key: string) => {
    setSocialLinks(prev => { const n = { ...prev }; delete n[key]; return n; });
  };

  if (loading) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg }}><Text style={{ color: colors.text60 }}>Загрузка...</Text></View>;
  if (!token) return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 16, backgroundColor: colors.bg }}>
      <Text style={{ color: colors.text60, marginBottom: 8 }}>Войдите через Steam</Text>
      <Pressable onPress={() => (typeof window !== "undefined" ? (window.location.href = "http://127.0.0.1:8000/api/auth/steam/login/?next=profile") : null)} style={{ backgroundColor: colors.orange, padding: 12, borderRadius: 8 }}>
        <Text style={{ color: colors.text, fontWeight: "600" }}>Войти через Steam</Text>
      </Pressable>
    </View>
  );

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <View style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 80, backgroundColor: 'rgba(249,115,22,0.1)' }} />
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
          <Text style={{ color: colors.orange }}>← Назад</Text>
        </Pressable>

        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginBottom: 16 }}>Аккаунт</Text>

        {error && <Text style={{ color: colors.red, fontSize: 12, marginBottom: 8 }}>{error}</Text>}

        {profile && (
          <>
            <Section title="ПРОФИЛЬ">
              <View style={{ flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 12 }}>
                {profile.player.avatar_url ? (
                  <Image source={{ uri: profile.player.avatar_url }} style={{ width: 48, height: 48, borderRadius: 24, backgroundColor: colors.bgElevated }} />
                ) : (
                  <View style={{ width: 48, height: 48, borderRadius: 24, backgroundColor: colors.orange, alignItems: "center", justifyContent: "center" }}>
                    <Text style={{ color: colors.text, fontSize: 18, fontWeight: "700" }}>?</Text>
                  </View>
                )}
                <View style={{ flex: 1 }}>
                  <TextInput
                    style={{ color: colors.text, fontSize: 16, fontWeight: "700", backgroundColor: colors.bgRow, padding: 6, borderRadius: 4 }}
                    value={editName}
                    onChangeText={setEditName}
                  />
                </View>
              </View>
              <TextInput
                style={{ color: colors.text60, fontSize: 11, backgroundColor: colors.bgRow, padding: 6, borderRadius: 4, marginBottom: 8 }}
                placeholder="URL аватарки"
                placeholderTextColor={colors.text40}
                value={editAvatar}
                onChangeText={setEditAvatar}
              />
              <Pressable onPress={handleSave} disabled={saving} style={{ backgroundColor: colors.orange, padding: 8, borderRadius: 6, alignItems: "center" }}>
                <Text style={{ color: colors.text, fontSize: 12, fontWeight: "600" }}>{saving ? "Сохранение..." : "Сохранить"}</Text>
              </Pressable>
            </Section>

            <Section title="STEAM">
              <Row label="Username" value={profile.user.username} />
              <Row label="Steam ID" value={profile.player.steam_account_id ? String(profile.player.steam_account_id) : "Не привязан"} />
            </Section>

            {profile.rank && (
              <Section title="РАНГ">
                <View style={{ flexDirection: "row", alignItems: "center", gap: 10, marginBottom: 8 }}>
                  {rankIconUrl(profile.rank.season_rank) ? (
                    <Image source={{ uri: rankIconUrl(profile.rank.season_rank) }} style={{ width: 48, height: 48 }} />
                  ) : null}
                  <View style={{ flex: 1 }}>
                    <Row label="Ранг" value={profile.rank.season_rank_label} />
                    <Row label="Rank ID" value={String(profile.rank.season_rank)} />
                    {profile.rank.leaderboard_rank && <Row label="Leaderboard" value={`#${profile.rank.leaderboard_rank}`} />}
                  </View>
                </View>
              </Section>
            )}

            <Section title="ТРЕНЕР">
              {profile.player.is_coach && profile.coach ? (
                <>
                  <Row label="Рейтинг" value={`${profile.coach.rating.toFixed(1)} / 5.0`} />
                  <Row label="MMR на проверке" value={String(profile.coach.mmr_verified)} />
                  <Row label="Специализация" value={profile.coach.specialization || "—"} />
                  <Row label="Bio" value={profile.coach.bio || "—"} />
                  <Pressable
                    onPress={() => router.push({ pathname: "my-services" as any, params: { token } })}
                    style={{ backgroundColor: colors.bgElevated, padding: 10, borderRadius: 6, marginTop: 8, alignItems: "center" }}
                  >
                    <Text style={{ color: colors.orange, fontSize: 12, fontWeight: "600" }}>Мои услуги</Text>
                  </Pressable>
                </>
              ) : appStatus ? (
                <>
                  <Text style={{ color: colors.orange, fontSize: 12 }}>Заявка отправлена</Text>
                  <Text style={{ color: colors.text40, fontSize: 11, marginTop: 2 }}>
                    Статус: {
                      appStatus.status === "pending" ? "На рассмотрении" :
                      appStatus.status === "accepted" ? "Принята" :
                      appStatus.status === "rejected" ? "Отклонена" : appStatus.status
                    }
                  </Text>
                  {appStatus.message ? <Text style={{ color: colors.text60, fontSize: 10, marginTop: 4, fontStyle: "italic" }}>"{appStatus.message}"</Text> : null}
                </>
              ) : (
                <>
                  <Text style={{ color: colors.text40, fontSize: 12, marginBottom: 8 }}>Ты ещё не тренер. Отправь заявку!</Text>
                  <TextInput
                    style={{ backgroundColor: colors.bgRow, color: colors.text, fontSize: 12, padding: 8, borderRadius: 6, marginBottom: 8, minHeight: 60, borderWidth: 1, borderColor: colors.border }}
                    placeholder="Расскажи почему хочешь стать тренером (опыт, ранг, специализация)..."
                    placeholderTextColor={colors.text40}
                    multiline
                    value={appMessage}
                    onChangeText={setAppMessage}
                  />
                  <Pressable onPress={handleBecomeCoach} disabled={registering || !appMessage.trim()} style={{ backgroundColor: appMessage.trim() ? colors.green : colors.bgElevated, padding: 12, borderRadius: 8, alignItems: "center" }}>
                    <Text style={{ color: appMessage.trim() ? colors.text : colors.text40, fontWeight: "600" }}>{registering ? "Отправка..." : "Отправить заявку"}</Text>
                  </Pressable>
                </>
              )}
            </Section>

            {profile.player.is_coach && (
              <Section title="СОЦСЕТИ">
                {Object.entries(socialLinks).map(([key, val]) => (
                  <View key={key} style={{ flexDirection: "row", alignItems: "center", marginBottom: 4 }}>
                    <Text style={{ color: colors.orange, fontSize: 11, flex: 1 }}>{key}: {val}</Text>
                    <Pressable onPress={() => removeSocialLink(key)} style={{ padding: 4 }}>
                      <Text style={{ color: colors.red, fontSize: 11 }}>✕</Text>
                    </Pressable>
                  </View>
                ))}
                <View style={{ flexDirection: "row", gap: 4, marginTop: 4 }}>
                  <TextInput
                    style={{ backgroundColor: colors.bgRow, color: colors.text60, fontSize: 11, padding: 6, borderRadius: 4, flex: 1 }}
                    placeholder="telegram"
                    placeholderTextColor={colors.text40}
                    value={newSocialKey}
                    onChangeText={setNewSocialKey}
                  />
                  <TextInput
                    style={{ backgroundColor: colors.bgRow, color: colors.text60, fontSize: 11, padding: 6, borderRadius: 4, flex: 2 }}
                    placeholder="https://t.me/..."
                    placeholderTextColor={colors.text40}
                    value={newSocialVal}
                    onChangeText={setNewSocialVal}
                  />
                  <Pressable onPress={addSocialLink} style={{ backgroundColor: colors.orange, paddingHorizontal: 10, borderRadius: 4, justifyContent: "center" }}>
                    <Text style={{ color: colors.text, fontSize: 11, fontWeight: "600" }}>+</Text>
                  </Pressable>
                </View>
              </Section>
            )}

            <Section title="НАСТРОЙКИ">
              <Pressable
                onPress={() => router.push({ pathname: "conversations" as any, params: { token } })}
                style={{ backgroundColor: colors.bgRow, padding: 12, borderRadius: 8, marginBottom: 8 }}
              >
                <Text style={{ color: colors.orange }}>Сообщения</Text>
              </Pressable>
              <Pressable
                onPress={() => router.push({ pathname: "stratz-token" as any, params: { token } })}
                style={{ backgroundColor: colors.bgRow, padding: 12, borderRadius: 8, marginBottom: 8 }}
              >
                <Text style={{ color: profile.player.stratz_token ? colors.greenLight : colors.text60 }}>
                  Stratz API токен: {profile.player.stratz_token ? "Установлен" : "Не установлен"}
                </Text>
              </Pressable>
              {profile.user.is_staff && (
                <Pressable
                  onPress={() => router.push({ pathname: "admin-applications" as any, params: { token } })}
                  style={{ backgroundColor: colors.bgRow, padding: 12, borderRadius: 8 }}
                >
                  <Text style={{ color: colors.orange }}>Заявки тренеров (админ)</Text>
                </Pressable>
              )}
            </Section>
          </>
        )}
      </ScrollView>
    </View>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: colors.borderSoft, overflow: "hidden" }}>
      {title === "ПРОФИЛЬ" && <View style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 80, backgroundColor: 'rgba(249,115,22,0.1)' }} />}
      <Text style={{ color: colors.text60, fontSize: 11, fontWeight: "600", letterSpacing: 1, marginBottom: 10 }}>{title}</Text>
      {children}
    </View>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 6 }}>
      <Text style={{ color: colors.text40, fontSize: 12 }}>{label}</Text>
      <Text style={{ color: colors.text80, fontSize: 12 }}>{value}</Text>
    </View>
  );
}
