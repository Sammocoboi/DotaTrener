import { useEffect, useState, useRef } from "react";
import {
  View,
  Text,
  ScrollView,
  Pressable,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { API_BASE as API } from "@/lib/api";

type Msg = {
  id: number;
  sender: string;
  text: string;
  created_at: string;
};

function formatTime(iso: string): string {
  const d = new Date(iso);
  const h = d.getHours().toString().padStart(2, "0");
  const m = d.getMinutes().toString().padStart(2, "0");
  return `${h}:${m}`;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diffDays = Math.floor(
    (now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24)
  );
  if (diffDays === 0) return "Сегодня";
  if (diffDays === 1) return "Вчера";
  return d.toLocaleDateString("ru-RU", { day: "numeric", month: "short" });
}

function initials(name: string): string {
  return name
    .split(/\s+/)
    .map((w) => w[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

function shouldShowDate(msgs: Msg[], idx: number): boolean {
  if (idx === 0) return true;
  const prev = new Date(msgs[idx - 1].created_at);
  const cur = new Date(msgs[idx].created_at);
  return prev.toDateString() !== cur.toDateString();
}

function Avatar({ name, size = 40 }: { name: string; size?: number }) {
  return (
    <View
      style={{
        width: size,
        height: size,
        borderRadius: size / 2,
        backgroundColor: colors.orange,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Text
        style={{
          color: "#FFFFFF",
          fontSize: size * 0.38,
          fontWeight: "700",
        }}
      >
        {initials(name)}
      </Text>
    </View>
  );
}

function DateSeparator({ label }: { label: string }) {
  return (
    <View style={{ alignItems: "center", paddingVertical: 12 }}>
      <View
        style={{
          backgroundColor: colors.bgRow,
          borderRadius: 10,
          paddingHorizontal: 12,
          paddingVertical: 4,
        }}
      >
        <Text style={{ color: colors.text40, fontSize: 11, fontWeight: "500" }}>
          {label}
        </Text>
      </View>
    </View>
  );
}

export default function ChatScreen() {
  const params = useLocalSearchParams<{ conv_id: string; token: string }>();
  const conv_id = params.conv_id;
  const token = params.token || getToken();
  const headers = { Authorization: `Token ${token}` };

  const [messages, setMessages] = useState<Msg[]>([]);
  const [currentUser, setCurrentUser] = useState("");
  const [otherUser, setOtherUser] = useState("Собеседник");
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
      setMessages(convRes.data.messages || []);

      const myName = profRes?.data?.user?.username || "";
      setCurrentUser(myName);

      const convData = convRes.data;
      if (convData.other_user) {
        setOtherUser(convData.other_user);
      } else if (convRes.data.messages?.length > 0) {
        const other = convRes.data.messages.find(
          (m: Msg) => m.sender !== myName
        );
        if (other) setOtherUser(other.sender);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [conv_id]);

  useEffect(() => {
    setTimeout(() => scrollRef.current?.scrollToEnd({ animated: false }), 50);
  }, [messages, loading]);

  const send = async () => {
    if (!text.trim()) return;
    setSending(true);
    try {
      const r = await axios.post(
        `${API}/conversations/${conv_id}/`,
        { text: text.trim() },
        { headers }
      );
      setMessages((prev) => [...prev, r.data]);
      setText("");
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
    } catch (e) {
      console.error(e);
    } finally {
      setSending(false);
    }
  };

  const canSend = text.trim().length > 0 && !sending;

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      {/* HEADER */}
      <View
        style={{
          backgroundColor: colors.bgCard,
          borderBottomWidth: 1,
          borderBottomColor: colors.borderSoft,
          paddingTop: Platform.OS === "ios" ? 48 : 12,
          paddingBottom: 12,
          paddingHorizontal: 16,
        }}
      >
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            gap: 12,
          }}
        >
          <Pressable
            onPress={() => router.back()}
            style={({ pressed }) => ({
              width: 36,
              height: 36,
              borderRadius: 18,
              backgroundColor: colors.bgRow,
              alignItems: "center",
              justifyContent: "center",
              opacity: pressed ? 0.7 : 1,
            })}
          >
            <Text style={{ color: colors.orange, fontSize: 16 }}>←</Text>
          </Pressable>

          <Avatar name={otherUser} size={40} />
          <View style={{ flex: 1 }}>
            <Text
              style={{
                color: colors.text,
                fontSize: 16,
                fontWeight: "700",
              }}
              numberOfLines={1}
            >
              {otherUser}
            </Text>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginTop: 2 }}>
              <View
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: colors.green,
                }}
              />
              <Text style={{ color: colors.text40, fontSize: 12 }}>
                В сети
              </Text>
            </View>
          </View>
        </View>
      </View>

      {/* MESSAGES */}
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView
          ref={scrollRef}
          style={{ flex: 1 }}
          contentContainerStyle={{
            paddingHorizontal: 16,
            paddingTop: 12,
            paddingBottom: 8,
          }}
          showsVerticalScrollIndicator={false}
        >
          {loading && (
            <View
              style={{
                flex: 1,
                justifyContent: "center",
                alignItems: "center",
                paddingTop: 80,
              }}
            >
              <ActivityIndicator size="large" color={colors.orange} />
              <Text style={{ color: colors.text60, fontSize: 13, marginTop: 12 }}>
                Загрузка сообщений...
              </Text>
            </View>
          )}

          {!loading && messages.length === 0 && (
            <View
              style={{
                flex: 1,
                justifyContent: "center",
                alignItems: "center",
                paddingTop: 80,
              }}
            >
              <Avatar name={otherUser} size={64} />
              <Text
                style={{
                  color: colors.text,
                  fontSize: 16,
                  fontWeight: "600",
                  marginTop: 16,
                  marginBottom: 4,
                }}
              >
                Начните разговор
              </Text>
              <Text
                style={{
                  color: colors.text60,
                  fontSize: 13,
                  textAlign: "center",
                  paddingHorizontal: 40,
                }}
              >
                Напишите первое сообщение пользователю {otherUser}
              </Text>
            </View>
          )}

          {messages.map((m, idx) => {
            const isMe = m.sender === currentUser;
            const showDate = shouldShowDate(messages, idx);

            return (
              <View key={m.id}>
                {showDate && <DateSeparator label={formatDate(m.created_at)} />}
                <View
                  style={{
                    flexDirection: "row",
                    justifyContent: isMe ? "flex-end" : "flex-start",
                    alignItems: "flex-end",
                    marginBottom: 4,
                    gap: 8,
                  }}
                >
                  {!isMe && <Avatar name={m.sender} size={28} />}

                  <View
                    style={{
                      backgroundColor: isMe ? colors.orange : colors.bgRow,
                      borderRadius: 18,
                      borderBottomRightRadius: isMe ? 4 : 18,
                      borderBottomLeftRadius: isMe ? 18 : 4,
                      paddingVertical: 10,
                      paddingHorizontal: 14,
                      maxWidth: "72%",
                    }}
                  >
                    {!isMe && messages[idx - 1]?.sender === m.sender ? null : (
                      !isMe && (
                        <Text
                          style={{
                            color: colors.orange,
                            fontSize: 11,
                            fontWeight: "700",
                            marginBottom: 3,
                          }}
                        >
                          {m.sender}
                        </Text>
                      )
                    )}

                    <Text
                      style={{
                        color: isMe ? "#FFFFFF" : colors.text,
                        fontSize: 14,
                        lineHeight: 20,
                      }}
                    >
                      {m.text}
                    </Text>

                    <Text
                      style={{
                        color: isMe
                          ? "rgba(255,255,255,0.6)"
                          : colors.text40,
                        fontSize: 10,
                        marginTop: 4,
                        alignSelf: "flex-end",
                      }}
                    >
                      {formatTime(m.created_at)}
                    </Text>
                  </View>
                </View>
              </View>
            );
          })}
        </ScrollView>

        {/* INPUT BAR */}
        <View
          style={{
            backgroundColor: colors.bgCard,
            borderTopWidth: 1,
            borderTopColor: colors.borderSoft,
            paddingHorizontal: 12,
            paddingVertical: 10,
            paddingBottom: Platform.OS === "ios" ? 28 : 10,
          }}
        >
          <View
            style={{
              flexDirection: "row",
              alignItems: "flex-end",
              gap: 10,
            }}
          >
            <View
              style={{
                flex: 1,
                backgroundColor: colors.bgRow,
                borderRadius: 22,
                borderWidth: 1,
                borderColor: colors.border,
                minHeight: 44,
                maxHeight: 100,
                flexDirection: "row",
                alignItems: "flex-end",
                paddingHorizontal: 16,
                paddingVertical: Platform.OS === "web" ? 10 : 12,
              }}
            >
              <TextInput
                style={{
                  flex: 1,
                  color: colors.text,
                  fontSize: 15,
                  lineHeight: 20,
                  padding: 0,
                  ...(Platform.OS === "web"
                    ? { outlineStyle: "none" as any }
                    : {}),
                }}
                placeholder="Написать сообщение..."
                placeholderTextColor={colors.text40}
                value={text}
                onChangeText={setText}
                multiline
                maxLength={2000}
                returnKeyType="send"
                blurOnSubmit={false}
                onSubmitEditing={() => {
                  if (canSend) send();
                }}
              />
            </View>

            <Pressable
              onPress={send}
              disabled={!canSend}
              style={({ pressed }) => ({
                width: 44,
                height: 44,
                borderRadius: 22,
                backgroundColor: canSend ? colors.orange : colors.bgElevated,
                alignItems: "center",
                justifyContent: "center",
                opacity: pressed && canSend ? 0.8 : 1,
              })}
            >
              {sending ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <Text
                  style={{
                    color: canSend ? "#FFFFFF" : colors.text40,
                    fontSize: 20,
                    lineHeight: 22,
                  }}
                >
                  ↑
                </Text>
              )}
            </Pressable>
          </View>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}
