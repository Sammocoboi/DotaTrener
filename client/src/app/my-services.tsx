import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, TextInput, Alert } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";

const API = "http://127.0.0.1:8000/api/coaching";

type Service = { id: number; title: string; description: string; price: string; duration_minutes: number; is_active: boolean };

export default function MyServicesScreen() {
  const { token } = useLocalSearchParams<{ token: string }>();
  const headers = { Authorization: `Token ${token}` };
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Partial<Service> | null>(null);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    axios.get(`${API}/my-services/`, { headers })
      .then(r => setServices(r.data))
      .catch(() => Alert.alert("Ошибка", "Не удалось загрузить услуги"))
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
    } catch { Alert.alert("Ошибка"); }
    finally { setSaving(false); }
  };

  const deleteService = (id: number) => {
    Alert.alert("Удалить?", "", [
      { text: "Отмена" },
      { text: "Удалить", style: "destructive", onPress: () => {
        axios.delete(`${API}/my-services/${id}/`, { headers }).then(load);
      }},
    ]);
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#0B1120" }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push({ pathname: "profile" as any, params: { token } })} style={{ marginBottom: 12 }}>
        <Text style={{ color: "#60A5FA" }}>← Профиль</Text>
      </Pressable>

      <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <Text style={{ color: "#FFF", fontSize: 20, fontWeight: "700" }}>Мои услуги</Text>
        <Pressable onPress={() => setEditing({ is_active: true, duration_minutes: 60 })} style={{ backgroundColor: "#3B82F6", padding: 8, borderRadius: 6 }}>
          <Text style={{ color: "#FFF", fontSize: 12, fontWeight: "600" }}>+ Добавить</Text>
        </Pressable>
      </View>

      {loading && <Text style={{ color: "#64748B" }}>Загрузка...</Text>}

      {!loading && services.length === 0 && <Text style={{ color: "#64748B" }}>Нет услуг. Нажми "+ Добавить" чтобы создать.</Text>}

      {services.map(s => (
        <View key={s.id} style={{ backgroundColor: "#0F1729", borderRadius: 8, padding: 12, marginBottom: 8 }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
            <View style={{ flex: 1 }}>
              <Text style={{ color: "#FFF", fontSize: 14, fontWeight: "600" }}>{s.title}</Text>
              <Text style={{ color: "#A5B4FC", fontSize: 13, fontWeight: "700", marginTop: 2 }}>{"$"}{s.price}</Text>
              <Text style={{ color: "#64748B", fontSize: 11, marginTop: 2 }}>{s.duration_minutes} мин · {s.is_active ? "Активна" : "Неактивна"}</Text>
            </View>
            <View style={{ gap: 4 }}>
              <Pressable onPress={() => setEditing(s)} style={{ backgroundColor: "#1E293B", padding: 6, borderRadius: 4 }}>
                <Text style={{ color: "#60A5FA", fontSize: 11 }}>Изменить</Text>
              </Pressable>
              <Pressable onPress={() => deleteService(s.id)} style={{ backgroundColor: "#1E293B", padding: 6, borderRadius: 4 }}>
                <Text style={{ color: "#EF4444", fontSize: 11 }}>Удалить</Text>
              </Pressable>
            </View>
          </View>
        </View>
      ))}

      {editing && (
        <View style={{ backgroundColor: "#131B31", borderRadius: 10, padding: 14, marginTop: 8 }}>
          <Text style={{ color: "#FFF", fontSize: 14, fontWeight: "600", marginBottom: 8 }}>{editing.id ? "Редактировать" : "Новая услуга"}</Text>

          <Text style={label}>Название</Text>
          <TextInput style={input} value={editing.title || ""} onChangeText={t => setEditing({ ...editing, title: t })} placeholder="Напр. Разбор матча" placeholderTextColor="#475569" />

          <Text style={label}>Описание</Text>
          <TextInput style={[input, { height: 60 }]} value={editing.description || ""} onChangeText={t => setEditing({ ...editing, description: t })} multiline placeholderTextColor="#475569" />

          <View style={{ flexDirection: "row", gap: 8 }}>
            <View style={{ flex: 1 }}>
              <Text style={label}>Цена ($)</Text>
              <TextInput style={input} value={editing.price || ""} onChangeText={t => setEditing({ ...editing, price: t })} keyboardType="decimal-pad" placeholderTextColor="#475569" />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={label}>Длительность (мин)</Text>
              <TextInput style={input} value={String(editing.duration_minutes || "")} onChangeText={t => setEditing({ ...editing, duration_minutes: parseInt(t) || 0 })} keyboardType="number-pad" placeholderTextColor="#475569" />
            </View>
          </View>

          <View style={{ flexDirection: "row", gap: 8, marginTop: 12 }}>
            <Pressable onPress={() => setEditing(null)} style={{ flex: 1, backgroundColor: "#1E293B", padding: 10, borderRadius: 6, alignItems: "center" }}>
              <Text style={{ color: "#94A3B8", fontSize: 12 }}>Отмена</Text>
            </Pressable>
            <Pressable onPress={saveService} disabled={saving} style={{ flex: 1, backgroundColor: "#3B82F6", padding: 10, borderRadius: 6, alignItems: "center" }}>
              <Text style={{ color: "#FFF", fontSize: 12, fontWeight: "600" }}>{saving ? "Сохранение..." : "Сохранить"}</Text>
            </Pressable>
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const label: any = { color: "#94A3B8", fontSize: 11, marginBottom: 2, marginTop: 6 };
const input: any = { backgroundColor: "#1E293B", color: "#CBD5E1", fontSize: 12, padding: 8, borderRadius: 6, borderWidth: 1, borderColor: "rgba(255,255,255,0.08)" };
