import { useEffect, useState, useRef } from "react";
import { View, Text, ScrollView, Pressable, TextInput, Platform } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { API_BASE as API } from "@/lib/api";


type Service = { id: number; title: string; description: string; price: string; duration_minutes: number; video: number | null; video_title: string | null; is_active: boolean };
type Video = { id: number; title: string; file_url: string; duration_seconds: number; price: string; };
type VideoEdit = { title: string; description: string; file_url: string; thumbnail_url: string; duration_seconds: number; price: string; };

export default function MyServicesScreen() {
  const params = useLocalSearchParams<{ token: string }>();
  const token = params.token || getToken();
  const headers = { Authorization: `Token ${token}` };
  const [services, setServices] = useState<Service[]>([]);
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Partial<Service> | null>(null);
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");
  const [tab, setTab] = useState<"services" | "videos">("services");
  const [videoEditing, setVideoEditing] = useState<VideoEdit | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoUploading, setVideoUploading] = useState(false);
  const videoInputRef = useRef<HTMLInputElement | null>(null);

  const load = () => {
    setLoading(true);
    Promise.all([
      axios.get(`${API}/my-services/`, { headers }),
      axios.get(`${API}/my-videos/`, { headers }),
    ])
      .then(([sRes, vRes]) => { setServices(sRes.data); setVideos(vRes.data); })
      .catch(() => setErr("Не удалось загрузить"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { if (token) load(); }, [token]);

  const saveService = async () => {
    if (!editing?.title) return;
    setSaving(true);
    try {
      const payload: any = {
        title: editing.title,
        description: editing.description || "",
        price: editing.price || "0",
        duration_minutes: editing.duration_minutes || 60,
        is_active: editing.is_active ?? true,
      };
      if (editing.video) payload.video = editing.video;
      else payload.video = null;
      if (editing.id) {
        await axios.patch(`${API}/my-services/${editing.id}/`, payload, { headers });
      } else {
        await axios.post(`${API}/my-services/`, payload, { headers });
      }
      setEditing(null);
      load();
    } catch { setErr("Ошибка"); }
    finally { setSaving(false); }
  };

  const deleteService = (id: number) => {
    axios.delete(`${API}/my-services/${id}/`, { headers }).then(load);
  };

  const saveVideo = async () => {
    if (!videoEditing?.title) return;
    setVideoUploading(true);
    setErr("");
    try {
      if (videoFile) {
        const fd = new FormData();
        fd.append("file", videoFile);
        fd.append("title", videoEditing.title);
        fd.append("description", videoEditing.description);
        fd.append("duration_seconds", String(videoEditing.duration_seconds || 0));
        fd.append("price", videoEditing.price || "0");
        await axios.post(`${API}/upload-video/`, fd, { headers: { Authorization: `Token ${token}`, "Content-Type": "multipart/form-data" } });
      } else if (videoEditing.file_url) {
        await axios.post(`${API}/my-videos/`, {
          title: videoEditing.title,
          description: videoEditing.description,
          file_url: videoEditing.file_url,
          duration_seconds: videoEditing.duration_seconds || 0,
          price: videoEditing.price || "0",
        }, { headers });
      } else {
        setErr("Выберите файл или укажите URL");
        setVideoUploading(false);
        return;
      }
      setVideoEditing(null);
      setVideoFile(null);
      load();
    } catch { setErr("Ошибка загрузки видео"); }
    finally { setVideoUploading(false); }
  };

  const deleteVideo = (id: number) => {
    axios.delete(`${API}/my-videos/${id}/`, { headers }).then(load);
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
        <Text style={{ color: colors.orange }}>← Назад</Text>
      </Pressable>

      <View style={{ flexDirection: "row", gap: 8, marginBottom: 16 }}>
        <Pressable onPress={() => { setTab("services"); setEditing(null); }} style={{ backgroundColor: tab === "services" ? colors.orange : colors.bgCard, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 6 }}>
          <Text style={{ color: tab === "services" ? colors.text : colors.text60, fontSize: 12, fontWeight: "600" }}>Услуги</Text>
        </Pressable>
        <Pressable onPress={() => { setTab("videos"); setEditing(null); }} style={{ backgroundColor: tab === "videos" ? colors.orange : colors.bgCard, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 6 }}>
          <Text style={{ color: tab === "videos" ? colors.text : colors.text60, fontSize: 12, fontWeight: "600" }}>Видео</Text>
        </Pressable>
      </View>

      {err ? <Text style={{ color: colors.red, fontSize: 12, marginBottom: 8 }}>{err}</Text> : null}
      {loading && <Text style={{ color: colors.text60 }}>Загрузка...</Text>}

      {tab === "services" && (
        <>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <Text style={{ color: colors.text, fontSize: 18, fontWeight: "700" }}>Услуги</Text>
            <Pressable onPress={() => setEditing({ is_active: true, duration_minutes: 60 })} style={{ backgroundColor: colors.orange, padding: 8, borderRadius: 6 }}>
              <Text style={{ color: colors.text, fontSize: 12, fontWeight: "600" }}>+ Добавить</Text>
            </Pressable>
          </View>
          {!loading && services.length === 0 && <Text style={{ color: colors.text60 }}>Нет услуг</Text>}
          {services.map(s => (
            <View key={s.id} style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 10, borderWidth: 1, borderColor: colors.borderSoft }}>
              <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
                <View style={{ flex: 1 }}>
                  <Text style={{ color: colors.text, fontSize: 14, fontWeight: "600" }}>{s.title}</Text>
                  <Text style={{ color: colors.purpleLight, fontSize: 13, fontWeight: "700", marginTop: 2 }}>{"$"}{s.price}</Text>
                  <Text style={{ color: colors.text40, fontSize: 11, marginTop: 2 }}>{s.duration_minutes} мин · {s.is_active ? "Активна" : "Неактивна"}</Text>
                  {s.video_title && <Text style={{ color: colors.orange, fontSize: 10, marginTop: 2 }}>VIDEO: {s.video_title}</Text>}
                </View>
                <View style={{ gap: 4 }}>
                  <Pressable onPress={() => setEditing(s)} style={{ backgroundColor: colors.bgElevated, padding: 6, borderRadius: 4 }}>
                    <Text style={{ color: colors.orange, fontSize: 11 }}>Изменить</Text>
                  </Pressable>
                  <Pressable onPress={() => deleteService(s.id)} style={{ backgroundColor: colors.bgElevated, padding: 6, borderRadius: 4 }}>
                    <Text style={{ color: colors.red, fontSize: 11 }}>Удалить</Text>
                  </Pressable>
                </View>
              </View>
            </View>
          ))}
        </>
      )}

      {tab === "videos" && (
        <>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <Text style={{ color: colors.text, fontSize: 18, fontWeight: "700" }}>Видео</Text>
            <Pressable onPress={() => setVideoEditing({ title: "", description: "", file_url: "", thumbnail_url: "", duration_seconds: 0, price: "0" })} style={{ backgroundColor: colors.orange, padding: 8, borderRadius: 6 }}>
              <Text style={{ color: colors.text, fontSize: 12, fontWeight: "600" }}>+ Добавить</Text>
            </Pressable>
          </View>
          {!loading && videos.length === 0 && !videoEditing && <Text style={{ color: colors.text60 }}>Нет видео</Text>}
          {videos.map(v => (
            <View key={v.id} style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 10, borderWidth: 1, borderColor: colors.borderSoft }}>
              <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
                <View style={{ flex: 1 }}>
                  <Text style={{ color: colors.text, fontSize: 14, fontWeight: "600" }}>{v.title}</Text>
                  <Text style={{ color: colors.text40, fontSize: 11, marginTop: 2 }}>{Math.floor(v.duration_seconds / 60)} мин · {Number(v.price) > 0 ? `$${v.price}` : "Бесплатно"}</Text>
                </View>
                <Pressable onPress={() => deleteVideo(v.id)} style={{ backgroundColor: colors.bgElevated, padding: 6, borderRadius: 4 }}>
                  <Text style={{ color: colors.red, fontSize: 11 }}>Удалить</Text>
                </Pressable>
              </View>
              <Pressable onPress={() => { if (typeof window !== "undefined") window.open(v.file_url, "_blank"); }} style={{ backgroundColor: colors.bgElevated, padding: 6, borderRadius: 4, marginTop: 6, alignItems: "center" }}>
                <Text style={{ color: colors.orange, fontSize: 11 }}>Открыть</Text>
              </Pressable>
            </View>
          ))}

          {videoEditing && (
            <View style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginTop: 8, borderWidth: 1, borderColor: colors.borderSoft }}>
              <Text style={{ color: colors.text, fontSize: 14, fontWeight: "600", marginBottom: 8 }}>Новое видео</Text>
              <Text style={labelStyle}>Название</Text>
              <TextInput style={inputStyle} value={videoEditing.title} onChangeText={t => setVideoEditing({ ...videoEditing, title: t })} placeholder="Название ролика" placeholderTextColor={colors.text40} />

              {(Platform.OS === "web" && typeof document !== "undefined") && (
                <>
                  <Text style={labelStyle}>Файл видео (макс 600 МБ)</Text>
                  <input
                    ref={videoInputRef}
                    type="file"
                    accept="video/mp4,video/webm,video/ogg,.mov,.mkv"
                    onChange={(e: any) => {
                      const f = e.target.files?.[0];
                      if (f) { setVideoFile(f); setVideoEditing({ ...videoEditing, title: videoEditing.title || f.name.replace(/\.[^.]+$/, "") }); }
                    }}
                    style={{ display: "none" }}
                  />
                  <Pressable onPress={() => videoInputRef.current?.click()} style={{ backgroundColor: colors.bgRow, padding: 10, borderRadius: 6, borderWidth: 1, borderColor: colors.border, marginBottom: 4 }}>
                    <Text style={{ color: videoFile ? colors.orange : colors.text60, fontSize: 12 }}>{videoFile ? videoFile.name : "Выберите видеофайл..."}</Text>
                  </Pressable>
                  <Text style={{ color: colors.text40, fontSize: 10, marginBottom: 6 }}>— или укажите URL —</Text>
                </>
              )}

              <Text style={labelStyle}>URL видео</Text>
              <TextInput style={inputStyle} value={videoEditing.file_url} onChangeText={t => setVideoEditing({ ...videoEditing, file_url: t })} placeholder="https://..." placeholderTextColor={colors.text40} />
              <Text style={labelStyle}>Описание</Text>
              <TextInput style={[inputStyle, { height: 50 }]} value={videoEditing.description} onChangeText={t => setVideoEditing({ ...videoEditing, description: t })} multiline placeholderTextColor={colors.text40} />
              <View style={{ flexDirection: "row", gap: 8 }}>
                <View style={{ flex: 1 }}>
                  <Text style={labelStyle}>Длительность (сек)</Text>
                  <TextInput style={inputStyle} value={String(videoEditing.duration_seconds || "")} onChangeText={t => setVideoEditing({ ...videoEditing, duration_seconds: parseInt(t) || 0 })} keyboardType="number-pad" placeholderTextColor={colors.text40} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={labelStyle}>Цена ($)</Text>
                  <TextInput style={inputStyle} value={videoEditing.price} onChangeText={t => setVideoEditing({ ...videoEditing, price: t })} keyboardType="decimal-pad" placeholderTextColor={colors.text40} />
                </View>
              </View>
              <View style={{ flexDirection: "row", gap: 8, marginTop: 12 }}>
                <Pressable onPress={() => { setVideoEditing(null); setVideoFile(null); }} style={{ flex: 1, backgroundColor: colors.bgElevated, padding: 10, borderRadius: 6, alignItems: "center" }}>
                  <Text style={{ color: colors.text60, fontSize: 12 }}>Отмена</Text>
                </Pressable>
                <Pressable onPress={saveVideo} disabled={videoUploading} style={{ flex: 1, backgroundColor: colors.orange, padding: 10, borderRadius: 6, alignItems: "center" }}>
                  <Text style={{ color: colors.text, fontSize: 12, fontWeight: "600" }}>{videoUploading ? "Загрузка..." : "Сохранить"}</Text>
                </Pressable>
              </View>
            </View>
          )}
        </>
      )}

      {editing && (
        <View style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginTop: 8, borderWidth: 1, borderColor: colors.borderSoft }}>
          <Text style={{ color: colors.text, fontSize: 14, fontWeight: "600", marginBottom: 8 }}>{editing.id ? "Редактировать" : "Новая услуга"}</Text>

          <Text style={labelStyle}>Название</Text>
          <TextInput style={inputStyle} value={editing.title || ""} onChangeText={t => setEditing({ ...editing, title: t })} placeholder="Напр. Разбор матча" placeholderTextColor={colors.text40} />

          <Text style={labelStyle}>Описание</Text>
          <TextInput style={[inputStyle, { height: 60 }]} value={editing.description || ""} onChangeText={t => setEditing({ ...editing, description: t })} multiline placeholderTextColor={colors.text40} />

          <View style={{ flexDirection: "row", gap: 8 }}>
            <View style={{ flex: 1 }}>
              <Text style={labelStyle}>Цена ($)</Text>
              <TextInput style={inputStyle} value={editing.price || ""} onChangeText={t => setEditing({ ...editing, price: t })} keyboardType="decimal-pad" placeholderTextColor={colors.text40} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={labelStyle}>Длительность (мин)</Text>
              <TextInput style={inputStyle} value={String(editing.duration_minutes || "")} onChangeText={t => setEditing({ ...editing, duration_minutes: parseInt(t) || 0 })} keyboardType="number-pad" placeholderTextColor={colors.text40} />
            </View>
          </View>

          <Text style={labelStyle}>Видео (опционально)</Text>
          <View style={{ backgroundColor: colors.bgRow, borderRadius: 6, padding: 8, marginTop: 2 }}>
            <Pressable
              onPress={() => setEditing({ ...editing, video: null })}
              style={{ paddingVertical: 4, backgroundColor: !editing.video ? colors.orange + "30" : "transparent", borderRadius: 4, marginBottom: 2 }}
            >
              <Text style={{ color: !editing.video ? colors.orange : colors.text60, fontSize: 11 }}>Без видео</Text>
            </Pressable>
            {videos.map(v => (
              <Pressable
                key={v.id}
                onPress={() => setEditing({ ...editing, video: v.id })}
                style={{ paddingVertical: 4, backgroundColor: editing.video === v.id ? colors.orange + "30" : "transparent", borderRadius: 4, marginBottom: 2 }}
              >
                <Text style={{ color: editing.video === v.id ? colors.orange : colors.text60, fontSize: 11 }}>{v.title}</Text>
              </Pressable>
            ))}
          </View>

          <View style={{ flexDirection: "row", gap: 8, marginTop: 12 }}>
            <Pressable onPress={() => setEditing(null)} style={{ flex: 1, backgroundColor: colors.bgElevated, padding: 10, borderRadius: 6, alignItems: "center" }}>
              <Text style={{ color: colors.text60, fontSize: 12 }}>Отмена</Text>
            </Pressable>
            <Pressable onPress={saveService} disabled={saving} style={{ flex: 1, backgroundColor: colors.orange, padding: 10, borderRadius: 6, alignItems: "center" }}>
              <Text style={{ color: colors.text, fontSize: 12, fontWeight: "600" }}>{saving ? "Сохранение..." : "Сохранить"}</Text>
            </Pressable>
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const labelStyle = { color: colors.text60, fontSize: 11, marginBottom: 2, marginTop: 6 };
const inputStyle = { backgroundColor: colors.bgRow, color: colors.text, fontSize: 12, padding: 8, borderRadius: 6, borderWidth: 1, borderColor: colors.border };
