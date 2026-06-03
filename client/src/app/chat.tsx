import { useEffect, useState, useRef } from "react";
import { View, Text, ScrollView, Pressable, TextInput } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "./token-storage";
import { colors } from "./theme";

const API = "http://127.0.0.1:8000/api/coaching";

type Msg = {
  id: number;
  sender: string;
  text: string;
  created_at: string;
};

export default function ChatScreen() {
  const params = useLocalSearchParams<{ conv_id: string; token: string }>();
  const conv_id = params.conv_id;
  const token = params.token || getToken();
  const headers = { Authorization: `Token ${token}` };
  const [messages, setMessages] = useState<Msg[]>([]);
  const [currentUser, setCurrentUser] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<ScrollView>(null);

  const load = async () => {
    if (!conv_id) return;
    setLoading(true);
    try {
      const [convRes, profRes] = await Promise.all([
        axios.get(`${API}/conversations/${conv_id}/`, { headers }),
        axios.get(`${API}/profile/`, { headers }).catch(() => null),
      ]);
      setMessages(convRes.data.messages);
      setCurrentUser(profRes?.data?.user?.username || "");
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [conv_id]);

  const send = async () => {
    if (!text.trim()) return;
    setSending(true);
    try {
      const r = await axios.post(`${API}/conversations/${conv_id}/`, { text: text.trim() }, { headers });
      setMessages(prev => [...prev, r.data]);
      setText("");
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
    } catch (e) {
      console.error(e);
    } finally {
      setSending(false);
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <View style={{ padding: 16, borderBottomWidth: 1, borderBottomColor: colors.borderSoft }}>
        <Pressable onPress={() => router.push("/")} style={{ marginBottom: 8 }}>
          <Text style={{ color: colors.orange }}>← Назад</Text>
        </Pressable>
      </View>

      <ScrollView ref={scrollRef} style={{ flex: 1, padding: 16 }} contentContainerStyle={{ flexGrow: 1, justifyContent: "flex-end" }}>
        {loading && <Text style={{ color: colors.text60 }}>Загрузка...</Text>}
        {messages.map(m => {
          const isMe = m.sender === currentUser;
          return (
            <View key={m.id} style={{ alignItems: isMe ? "flex-end" : "flex-start", marginBottom: 8 }}>
              <View style={{ backgroundColor: isMe ? colors.orange : colors.bgRow, borderRadius: 14, padding: 10, maxWidth: "80%" }}>
                <Text style={{ color: colors.text, fontSize: 13 }}>{m.text}</Text>
                <Text style={{ color: colors.text40, fontSize: 9, marginTop: 4 }}>
                  {new Date(m.created_at).toLocaleString("ru")}
                </Text>
              </View>
            </View>
          );
        })}
      </ScrollView>

      <View style={{ flexDirection: "row", padding: 12, gap: 8, borderTopWidth: 1, borderTopColor: colors.borderSoft }}>
        <TextInput
          style={{ flex: 1, backgroundColor: colors.bgRow, color: colors.text, fontSize: 13, padding: 10, borderRadius: 8 }}
          placeholder="Написать сообщение..."
          placeholderTextColor={colors.text40}
          value={text}
          onChangeText={setText}
        />
        <Pressable onPress={send} disabled={sending || !text.trim()} style={{ backgroundColor: text.trim() ? colors.orange : colors.bgElevated, paddingHorizontal: 16, borderRadius: 8, justifyContent: "center" }}>
          <Text style={{ color: text.trim() ? colors.text : colors.text40, fontWeight: "600" }}>{sending ? "..." : "→"}</Text>
        </Pressable>
      </View>
    </View>
  );
}
