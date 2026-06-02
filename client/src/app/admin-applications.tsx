import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable } from "react-native";
import { useLocalSearchParams } from "expo-router";
import axios from "axios";

const API = "http://127.0.0.1:8000/api/coaching";

type Application = {
  id: number;
  user_id: number;
  username: string;
  message: string;
  status: string;
  created_at: string;
};

export default function AdminApplications() {
  const { token } = useLocalSearchParams<{ token: string }>();
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
    <ScrollView style={{ flex: 1, backgroundColor: "#0B1120", padding: 16 }}>
      <Text style={{ color: "#F1F5F9", fontSize: 20, fontWeight: "700", marginBottom: 16 }}>
        Заявки тренеров
      </Text>

      {loading ? (
        <Text style={{ color: "#64748B" }}>Загрузка...</Text>
      ) : apps.length === 0 ? (
        <Text style={{ color: "#64748B" }}>Нет pending заявок</Text>
      ) : (
        apps.map((app) => (
          <View key={app.id} style={{ backgroundColor: "#1E293B", borderRadius: 8, padding: 12, marginBottom: 12 }}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 6 }}>
              <Text style={{ color: "#60A5FA", fontWeight: "600", fontSize: 13 }}>{app.username}</Text>
              <Text style={{ color: "#64748B", fontSize: 10 }}>{new Date(app.created_at).toLocaleString("ru")}</Text>
            </View>
            <View style={{ backgroundColor: "rgba(255,255,255,0.05)", borderRadius: 4, padding: 8, marginBottom: 10 }}>
              <Text style={{ color: "#94A3B8", fontSize: 12, fontStyle: "italic" }}>"{app.message || "—"}"</Text>
            </View>
            <View style={{ flexDirection: "row", gap: 8 }}>
              <Pressable
                onPress={() => handleAction(app.id, "accept")}
                disabled={actionLoading === app.id}
                style={{ flex: 1, backgroundColor: "#059669", padding: 10, borderRadius: 6, alignItems: "center" }}
              >
                <Text style={{ color: "#FFF", fontWeight: "600", fontSize: 12 }}>
                  {actionLoading === app.id ? "..." : "Принять"}
                </Text>
              </Pressable>
              <Pressable
                onPress={() => handleAction(app.id, "reject")}
                disabled={actionLoading === app.id}
                style={{ flex: 1, backgroundColor: "#DC2626", padding: 10, borderRadius: 6, alignItems: "center" }}
              >
                <Text style={{ color: "#FFF", fontWeight: "600", fontSize: 12 }}>
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
