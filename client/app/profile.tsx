import { useEffect, useState, useRef } from "react";
import { View, Text, ScrollView, Pressable, TextInput, Image, Platform, Modal } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { rankIconUrl } from "@/lib/rank-label";
import { API_BASE as API, API_ROOT } from "@/lib/api";


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

const CROP_SIZE = 256;

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
  const [socialLinks, setSocialLinks] = useState<Record<string, string>>({});
  const [newSocialKey, setNewSocialKey] = useState("");
  const [newSocialVal, setNewSocialVal] = useState("");
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [cropVisible, setCropVisible] = useState(false);
  const [cropImage, setCropImage] = useState<string | null>(null);
  const cropImgRef = useRef<HTMLImageElement | null>(null);
  const cropDragRef = useRef({ dragging: false, startX: 0, startY: 0, imgStartX: 0, imgStartY: 0 });
  const cropOffsetRef = useRef({ x: 0, y: 0 });
  const cropImgRenderedRef = useRef({ w: 0, h: 0 });

  const headers = token ? { Authorization: `Token ${token}` } : {};

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setCropImage(url);
    cropOffsetRef.current = { x: 0, y: 0 };
    setCropVisible(true);
  };

  const handleCropConfirm = async () => {
    if (!cropImage || !token) return;
    const off = cropOffsetRef.current;
    setCropVisible(false);
    setUploading(true);
    try {
      const img = new window.Image();
      img.crossOrigin = "anonymous";
      await new Promise<void>((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = reject;
        img.src = cropImage;
      });

      const scale = Math.max(CROP_SIZE / img.naturalWidth, CROP_SIZE / img.naturalHeight);
      const sw = CROP_SIZE / scale;
      const sh = CROP_SIZE / scale;
      const sx = (img.naturalWidth - sw) / 2 - off.x / scale;
      const sy = (img.naturalHeight - sh) / 2 - off.y / scale;

      const canvas = document.createElement("canvas");
      canvas.width = CROP_SIZE;
      canvas.height = CROP_SIZE;
      const ctx = canvas.getContext("2d")!;
      ctx.drawImage(img, sx, sy, sw, sh, 0, 0, CROP_SIZE, CROP_SIZE);

      const blob = await new Promise<Blob>((resolve) => canvas.toBlob((b) => resolve(b!), "image/jpeg", 0.9));
      const file = new File([blob], "avatar.jpg", { type: "image/jpeg" });

      const formData = new FormData();
      formData.append("file", file);
      const res = await axios.post(`${API}/upload-avatar/`, formData, {
        headers: { Authorization: `Token ${token}`, "Content-Type": "multipart/form-data" },
      });
      setProfile((prev) => prev ? { ...prev, player: { ...prev.player, avatar_url: res.data.url } } : prev);
      URL.revokeObjectURL(cropImage);
    } catch (err: any) {
      setError(err?.response?.data?.error || "Ошибка загрузки");
    } finally {
      setUploading(false);
      setCropImage(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

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
        setSocialLinks(pRes.data.coach?.social_links || {});
        setAppStatus(aRes.data?.application || null);
      })
      .catch((e) => setError(e?.response?.data?.error || "Ошибка загрузки"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadAll(); }, [token]);

  useEffect(() => {
    if (!cropVisible) return;
    const onMove = (e: MouseEvent) => {
      const d = cropDragRef.current;
      if (!d.dragging) return;
      const dx = e.clientX - d.startX;
      const dy = e.clientY - d.startY;
      const rw = cropImgRenderedRef.current.w;
      const rh = cropImgRenderedRef.current.h;
      const maxOffset = Math.max(0, (rw - CROP_SIZE) / 2);
      const maxOffsetY = Math.max(0, (rh - CROP_SIZE) / 2);
      const nx = Math.max(-maxOffset, Math.min(maxOffset, d.imgStartX + dx));
      const ny = Math.max(-maxOffsetY, Math.min(maxOffsetY, d.imgStartY + dy));
      cropOffsetRef.current = { x: nx, y: ny };
      const el = cropImgRef.current;
      if (el) {
        el.style.transform = `translate(calc(-50% + ${nx}px), calc(-50% + ${ny}px))`;
      }
    };
    const onUp = () => { cropDragRef.current.dragging = false; };
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
    return () => {
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup", onUp);
    };
  }, [cropVisible]);

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
      await axios.patch(`${API}/profile/`, { username: editName, social_links: socialLinks }, { headers });
      const res = await axios.get(`${API}/profile/`, { headers });
      setProfile(res.data);
      setSocialLinks(res.data.coach?.social_links || {});
    } catch (e: any) {
      setError(e?.response?.data?.error || "Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  };

  const addSocialLink = async () => {
    if (!newSocialKey.trim() || !newSocialVal.trim()) return;
    const updated = { ...socialLinks, [newSocialKey.trim()]: newSocialVal.trim() };
    setSocialLinks(updated);
    setNewSocialKey("");
    setNewSocialVal("");
    try {
      await axios.patch(`${API}/profile/`, { social_links: updated }, { headers });
      const res = await axios.get(`${API}/profile/`, { headers });
      setSocialLinks(res.data.coach?.social_links || {});
    } catch (e: any) {
      setError(e?.response?.data?.error || "Ошибка сохранения соцсетей");
    }
  };

  const removeSocialLink = async (key: string) => {
    const updated = { ...socialLinks };
    delete updated[key];
    setSocialLinks(updated);
    try {
      await axios.patch(`${API}/profile/`, { social_links: updated }, { headers });
      const res = await axios.get(`${API}/profile/`, { headers });
      setSocialLinks(res.data.coach?.social_links || {});
    } catch (e: any) {
      setError(e?.response?.data?.error || "Ошибка сохранения соцсетей");
    }
  };

  if (loading) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg }}><Text style={{ color: colors.text60 }}>Загрузка...</Text></View>;
  if (!token) return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 16, backgroundColor: colors.bg }}>
      <Text style={{ color: colors.text60, marginBottom: 8 }}>Войдите через Steam</Text>
      <Pressable onPress={() => (typeof window !== "undefined" ? (window.location.href = `${API_ROOT}/api/auth/steam/login/?next=profile`) : null)} style={{ backgroundColor: colors.orange, padding: 12, borderRadius: 8 }}>
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
                <Pressable onPress={() => Platform.OS === "web" && fileInputRef.current?.click()}>
                  {profile.player.avatar_url ? (
                    <Image source={{ uri: profile.player.avatar_url }} style={{ width: 64, height: 64, borderRadius: 32, backgroundColor: colors.bgElevated }} />
                  ) : (
                    <View style={{ width: 64, height: 64, borderRadius: 32, backgroundColor: colors.orange, alignItems: "center", justifyContent: "center" }}>
                      <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700" }}>?</Text>
                    </View>
                  )}
                </Pressable>
                {Platform.OS === "web" && (
                  <input
                    ref={fileInputRef as any}
                    type="file"
                    accept="image/*"
                    style={{ display: "none" }}
                    onChange={handleFileSelect}
                  />
                )}
                <View style={{ flex: 1 }}>
                  <TextInput
                    style={{ color: colors.text, fontSize: 16, fontWeight: "700", backgroundColor: colors.bgRow, padding: 6, borderRadius: 4 }}
                    value={editName}
                    onChangeText={setEditName}
                  />
                  <Pressable onPress={() => Platform.OS === "web" && fileInputRef.current?.click()} style={{ marginTop: 6, backgroundColor: colors.bgElevated, padding: 6, borderRadius: 6, alignItems: "center" }}>
                    <Text style={{ color: colors.orange, fontSize: 11, fontWeight: "600" }}>{uploading ? "Загрузка..." : "Загрузить аватарку"}</Text>
                  </Pressable>
                </View>
              </View>
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

      <Modal visible={cropVisible} transparent animationType="fade">
        <View style={{ flex: 1, backgroundColor: "rgba(0,0,0,0.85)", justifyContent: "center", alignItems: "center" }}>
          <Text style={{ color: "#fff", fontSize: 14, marginBottom: 12 }}>Перетащите фото, затем нажмите «Обрезать»</Text>
          <div style={{
            width: "min(80vw, 400px)", height: "min(80vw, 400px)",
            backgroundColor: "#000", position: "relative", cursor: "grab",
          }}>
            {cropImage && (
              <img
                ref={cropImgRef}
                src={cropImage}
                onLoad={(e) => {
                  const el = e.target as HTMLImageElement;
                  const s = Math.max(CROP_SIZE / el.naturalWidth, CROP_SIZE / el.naturalHeight);
                  const rw = el.naturalWidth * s;
                  const rh = el.naturalHeight * s;
                  cropImgRenderedRef.current = { w: rw, h: rh };
                  el.style.width = `${rw}px`;
                  el.style.height = `${rh}px`;
                  el.style.position = "absolute";
                  el.style.left = "50%";
                  el.style.top = "50%";
                  el.style.transform = "translate(-50%, -50%)";
                  el.style.userSelect = "none";
                  el.style.pointerEvents = "auto";
                  cropOffsetRef.current = { x: 0, y: 0 };
                }}
                onMouseDown={(e: any) => {
                  e.preventDefault();
                  cropDragRef.current = { dragging: true, startX: e.clientX, startY: e.clientY, imgStartX: cropOffsetRef.current.x, imgStartY: cropOffsetRef.current.y };
                }}
                draggable={false}
              />
            )}
            <div style={{
              position: "absolute", inset: 0, pointerEvents: "none",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <div style={{
                width: CROP_SIZE, height: CROP_SIZE, borderRadius: "50%",
                boxShadow: "0 0 0 9999px rgba(0,0,0,0.6)",
                border: `2px solid ${colors.orange}`,
              }} />
            </div>
          </div>
          <View style={{ flexDirection: "row", gap: 12, marginTop: 16 }}>
            <Pressable onPress={() => { setCropVisible(false); setCropImage(null); }} style={{ backgroundColor: "#444", paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8 }}>
              <Text style={{ color: "#fff", fontSize: 13 }}>Отмена</Text>
            </Pressable>
            <Pressable onPress={handleCropConfirm} style={{ backgroundColor: colors.orange, paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8 }}>
              <Text style={{ color: "#fff", fontSize: 13, fontWeight: "600" }}>Обрезать</Text>
            </Pressable>
          </View>
        </View>
      </Modal>
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
