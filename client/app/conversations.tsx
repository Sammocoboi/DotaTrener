import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable } from "react-native";
import { router, useLocalSearchParams, useFocusEffect } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { API_BASE as API } from "@/lib/api";


type ConvItem = {
  id: number;
  other_user: string;
  service_title: string | null;
  last_message: string;
  last_message_at: string;
  unread_count: number;
  is_coach_side: boolean;
};

export default function ConversationsScreen() {
  const params = useLocalSearchParams<{ token: string }>();
  const token = params.token || getToken();
  const headers = { Authorization: `Token ${token}` };
  const [convs, setConvs] = useState<ConvItem[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    if (!token) return;
    setLoading(true);
    axios.get(`${API}/conversations/`, { headers })
      .then(r => setConvs(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useFocusEffect(useCallback(() => { load(); }, [token]));

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
        <Text style={{ color: colors.orange }}>← Назад</Text>
      </Pressable>
      <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginBottom: 16 }}>Сообщения</Text>
      {loading && <Text style={{ color: colors.text60 }}>Загрузка...</Text>}
      {!loading && convs.length === 0 && <Text style={{ color: colors.text60 }}>Нет чатов</Text>}
      {convs.map(c => (
        <Pressable
          key={c.id}
          onPress={() => router.push({ pathname: "chat" as any, params: { conv_id: String(c.id), token: token || "" } })}
          style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 10, borderWidth: 1, borderColor: colors.borderSoft }}
        >
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
            <Text style={{ color: colors.orange, fontSize: 14, fontWeight: "600", flex: 1 }}>{c.other_user}</Text>
            <Text style={{ color: colors.text40, fontSize: 9 }}>{new Date(c.last_message_at).toLocaleString("ru")}</Text>
          </View>
          {c.service_title && <Text style={{ color: colors.purpleLight, fontSize: 10, marginTop: 2 }}>Услуга: {c.service_title}</Text>}
          <Text style={{ color: colors.text60, fontSize: 11, marginTop: 4 }} numberOfLines={1}>
            {c.last_message || "Нет сообщений"}
          </Text>
          {c.unread_count > 0 && (
            <View style={{ position: "absolute", top: 12, right: 12, backgroundColor: colors.orange, borderRadius: 10, minWidth: 20, height: 20, alignItems: "center", justifyContent: "center", paddingHorizontal: 6 }}>
              <Text style={{ color: colors.text, fontSize: 10, fontWeight: "700" }}>{c.unread_count}</Text>
            </View>
          )}
        </Pressable>
      ))}
    </ScrollView>
  );
}
