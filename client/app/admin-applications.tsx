import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { API_BASE as API } from "@/lib/api";


type Application = {
  id: number;
  user_id: number;
  username: string;
  message: string;
  status: string;
  created_at: string;
};

export default function AdminApplications() {
  const params = useLocalSearchParams<{ token: string }>();
  const token = params.token || getToken();
  const headers = token ? { Authorization: `Token ${token}` } : {};
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    axios
      .get(`${API}/applications/?status=pending`, { headers })
      .then((res) => setApps(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [token]);

  const handleAction = async (appId: number, action: "accept" | "reject") => {
    setActionLoading(appId);
    try {
      await axios.post(`${API}/applications/`, { application_id: appId, action }, { headers });
      setApps((prev) => prev.filter((a) => a.id !== appId));
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
        <Text style={{ color: colors.orange }}>← Назад</Text>
      </Pressable>

      <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginBottom: 16 }}>
        Заявки тренеров
      </Text>

      {loading ? (
        <Text style={{ color: colors.text60 }}>Загрузка...</Text>
      ) : apps.length === 0 ? (
        <Text style={{ color: colors.text60 }}>Нет pending заявок</Text>
      ) : (
        apps.map((app) => (
          <View key={app.id} style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: colors.borderSoft }}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
              <Text style={{ color: colors.orange, fontWeight: "600", fontSize: 13 }}>{app.username}</Text>
              <Text style={{ color: colors.text40, fontSize: 10 }}>{new Date(app.created_at).toLocaleString("ru")}</Text>
            </View>
            <View style={{ backgroundColor: colors.bgRow, borderRadius: 8, padding: 10, marginBottom: 12 }}>
              <Text style={{ color: colors.text60, fontSize: 12, fontStyle: "italic" }}>"{app.message || "—"}"</Text>
            </View>
            <View style={{ flexDirection: "row", gap: 8 }}>
              <Pressable
                onPress={() => handleAction(app.id, "accept")}
                disabled={actionLoading === app.id}
                style={{ flex: 1, backgroundColor: colors.green, padding: 10, borderRadius: 6, alignItems: "center" }}
              >
                <Text style={{ color: colors.text, fontWeight: "600", fontSize: 12 }}>
                  {actionLoading === app.id ? "..." : "Принять"}
                </Text>
              </Pressable>
              <Pressable
                onPress={() => handleAction(app.id, "reject")}
                disabled={actionLoading === app.id}
                style={{ flex: 1, backgroundColor: colors.red, padding: 10, borderRadius: 6, alignItems: "center" }}
              >
                <Text style={{ color: colors.text, fontWeight: "600", fontSize: 12 }}>
                  {actionLoading === app.id ? "..." : "Отклонить"}
                </Text>
              </Pressable>
            </View>
          </View>
        ))
      )}
    </ScrollView>
  );
}
