import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, TextInput } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { API_BASE as API } from "@/lib/api";


type Service = { id: number; title: string; description: string; price: string; duration_minutes: number; is_active: boolean };

export default function MyServicesScreen() {
  const params = useLocalSearchParams<{ token: string }>();
  const token = params.token || getToken();
  const headers = { Authorization: `Token ${token}` };
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Partial<Service> | null>(null);
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");

  const load = () => {
    setLoading(true);
    axios.get(`${API}/my-services/`, { headers })
      .then(r => setServices(r.data))
      .catch(() => setErr("Не удалось загрузить услуги"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { if (token) load(); }, [token]);

  const saveService = async () => {
    if (!editing?.title) return;
    setSaving(true);
    try {
      const payload = {
        title: editing.title,
        description: editing.description || "",
        price: editing.price || "0",
        duration_minutes: editing.duration_minutes || 60,
        is_active: editing.is_active ?? true,
      };
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

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
        <Text style={{ color: colors.orange }}>← Назад</Text>
      </Pressable>

      <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700" }}>Мои услуги</Text>
        <Pressable onPress={() => setEditing({ is_active: true, duration_minutes: 60 })} style={{ backgroundColor: colors.orange, padding: 8, borderRadius: 6 }}>
          <Text style={{ color: colors.text, fontSize: 12, fontWeight: "600" }}>+ Добавить</Text>
        </Pressable>
      </View>

      {err ? <Text style={{ color: colors.red, fontSize: 12, marginBottom: 8 }}>{err}</Text> : null}
      {loading && <Text style={{ color: colors.text60 }}>Загрузка...</Text>}

      {!loading && services.length === 0 && <Text style={{ color: colors.text60 }}>Нет услуг. Нажми "+ Добавить" чтобы создать.</Text>}

      {services.map(s => (
        <View key={s.id} style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 10, borderWidth: 1, borderColor: colors.borderSoft }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
            <View style={{ flex: 1 }}>
              <Text style={{ color: colors.text, fontSize: 14, fontWeight: "600" }}>{s.title}</Text>
              <Text style={{ color: colors.purpleLight, fontSize: 13, fontWeight: "700", marginTop: 2 }}>{"$"}{s.price}</Text>
              <Text style={{ color: colors.text40, fontSize: 11, marginTop: 2 }}>{s.duration_minutes} мин · {s.is_active ? "Активна" : "Неактивна"}</Text>
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
