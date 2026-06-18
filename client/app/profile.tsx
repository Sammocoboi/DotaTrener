import { useEffect, useState, useRef } from "react";
import { View, Text, ScrollView, Pressable, TextInput, Image, Platform, Modal } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import * as WebBrowser from "expo-web-browser";
import axios from "axios";
import { getToken, saveToken, clearToken } from "@/lib/token-storage";
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
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const urlToken = params.token || getToken();
    if (urlToken) {
      setToken(urlToken);
      return;
    }
    if (Platform.OS === "web" && typeof window !== "undefined") {
      const hash = window.location.hash;
      if (hash && hash.length > 1) {
        const urlParams = new URLSearchParams(hash.substring(1));
        const ht = urlParams.get("token");
        const hs = urlParams.get("steam_id");
        if (ht) {
          saveToken(ht, hs || undefined);
          setToken(ht);
          window.history.replaceState({}, "", window.location.pathname);
          return;
        }
      }
    }
    if (!getToken()) {
      router.replace("/login");
    } else {
      setToken(getToken());
    }
  }, []);
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [subStatus, setSubStatus] = useState<{ is_active: boolean; expires_at: string; is_expired: boolean } | null>(null);
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

  const loadAll = (tok: string) => {
    setLoading(true);
    const h = { Authorization: `Token ${tok}` };
    Promise.all([
      axios.get(`${API}/profile/`, { headers: h }),
      axios.get(`${API}/subscription/`, { headers: h }).catch(() => ({ data: { subscription: null } })),
    ])
      .then(([pRes, sRes]) => {
        setProfile(pRes.data);
        setEditName(pRes.data.user.username);
        setSocialLinks(pRes.data.coach?.social_links || {});
        setSubStatus(sRes.data?.subscription || null);
      })
      .catch((e) => setError(e?.response?.data?.error || "Ошибка загрузки"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { if (token) loadAll(token); }, [token]);

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

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/logout/`, {}, { headers });
    } catch {}
    clearToken();
    router.replace("/login");
  };

  const handleUnbindSteam = async () => {
    try {
      await axios.post(`${API}/unbind-steam/`, {}, { headers });
      setProfile((prev) => prev ? {
        ...prev,
        player: { ...prev.player, steam_account_id: null, steam_id_64: null },
        rank: null,
        match_stats: null,
      } : prev);
    } catch (e: any) {
      setError(e?.response?.data?.error || "Ошибка отвязки Steam");
    }
  };

  if (loading) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg }}><Text style={{ color: colors.text60 }}>Загрузка...</Text></View>;
  if (!token) return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 16, backgroundColor: colors.bg }}>
      <Text style={{ color: colors.text60, marginBottom: 12 }}>Войдите в аккаунт</Text>
      <Pressable onPress={() => router.replace("/login")} style={{ backgroundColor: colors.orange, padding: 12, borderRadius: 8 }}>
        <Text style={{ color: colors.text, fontWeight: "600" }}>Войти</Text>
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
              {!profile.player.steam_account_id ? (
                <Pressable
                  onPress={() => {
                    let url = `${API_ROOT}/api/auth/steam/login/?next=profile${token ? `&token=${token}` : ''}`;
                    if (Platform.OS === "web") {
                      const returnUrl = encodeURIComponent(window.location.origin);
                      url += `&return_to=${returnUrl}`;
                      window.location.href = url;
                    } else {
                      WebBrowser.openAuthSessionAsync(url, "client://auth-callback");
                    }
                  }}
                  style={{ backgroundColor: colors.orange, padding: 10, borderRadius: 8, marginTop: 8, alignItems: "center" }}
                >
                  <Text style={{ color: "#FFFFFF", fontSize: 13, fontWeight: "600" }}>Привязать Steam</Text>
                </Pressable>
              ) : null}
            </Section>

            {profile.rank && (
              <Section title="РАНГ">
                <View style={{ flexDirection: "row", alignItems: "center", gap: 10 }}>
                  {rankIconUrl(profile.rank.season_rank) ? (
                    <Image source={{ uri: rankIconUrl(profile.rank.season_rank) }} style={{ width: 56, height: 56 }} />
                  ) : null}
                  <Text style={{ color: colors.text, fontSize: 16, fontWeight: "600" }}>{profile.rank.season_rank_label}</Text>
                </View>
                {profile.rank.leaderboard_rank ? (
                  <Text style={{ color: colors.text60, fontSize: 12, marginTop: 4 }}>Leaderboard: #{profile.rank.leaderboard_rank}</Text>
                ) : null}
              </Section>
            )}

            <Section title="ТРЕНЕР">
              {profile.player.is_coach && profile.coach && subStatus?.is_active ? (
                <>
                  <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 8 }}>
                    <View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: colors.green }} />
                    <Text style={{ color: colors.green, fontSize: 12, fontWeight: "600" }}>Подписка активна</Text>
                  </View>
                  {subStatus.expires_at && (
                    <Row label="Действует до" value={
                      new Date(subStatus.expires_at).toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" })
                    } />
                  )}
                  <Row label="Рейтинг" value={`${profile.coach.rating.toFixed(1)} / 5.0`} />
                  <Row label="Специализация" value={profile.coach.specialization || "—"} />
                  <Pressable
                    onPress={() => router.push({ pathname: "my-services" as any, params: { token } })}
                    style={{ backgroundColor: colors.orange, padding: 10, borderRadius: 6, marginTop: 8, alignItems: "center" }}
                  >
                    <Text style={{ color: "#FFFFFF", fontSize: 12, fontWeight: "600" }}>Мои услуги</Text>
                  </Pressable>
                </>
              ) : (
                <Pressable
                  onPress={() => router.push({ pathname: "subscription" as any, params: { token } })}
                  style={{ backgroundColor: colors.bgRow, padding: 12, borderRadius: 8, borderWidth: 1, borderColor: colors.orange, borderStyle: "dashed" }}
                >
                  <Text style={{ color: colors.text, fontSize: 13, fontWeight: "600", marginBottom: 4 }}>Стань тренером</Text>
                  <Text style={{ color: colors.text60, fontSize: 11 }}>Оформи подписку и начни выкладывать услуги</Text>
                </Pressable>
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
              {profile.player.steam_account_id ? (
                <Pressable
                  onPress={handleUnbindSteam}
                  style={{ backgroundColor: colors.bgRow, padding: 12, borderRadius: 8, marginBottom: 8, borderWidth: 1, borderColor: colors.red }}
                >
                  <Text style={{ color: colors.red }}>Отвязать Steam</Text>
                </Pressable>
              ) : null}
              <Pressable
                onPress={handleLogout}
                style={{ backgroundColor: colors.red, padding: 12, borderRadius: 8, marginTop: 4, alignItems: "center" }}
              >
                <Text style={{ color: "#fff", fontSize: 13, fontWeight: "600" }}>Выйти из аккаунта</Text>
              </Pressable>
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
