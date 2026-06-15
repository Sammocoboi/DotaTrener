import { useEffect, useState, useRef, useCallback } from "react";
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

/* ─── Dark chat palette (STRATZ-inspired) ─── */
const chat = {
  bg: "#0F1923",
  bgSurface: "#162231",
  bgBubble: "#1C2D3F",
  bgBubbleMe: "#EA580C",
  bgInput: "#162231",
  border: "#243447",
  text: "#E2E8F0",
  textSecondary: "#94A3B8",
  textMuted: "#64748B",
  orange: "#F97316",
  orangeDark: "#EA580C",
  green: "#10B981",
  sendBg: "#F97316",
  sendDisabled: "#1C2D3F",
  typing: "#64748B",
};

/* ─── Types ─── */
type Msg = {
  id: number;
  sender: string;
  text: string;
  created_at: string;
};

/* ─── Helpers ─── */
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
  return d.toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "short",
  });
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

/* ─── Sub-components ─── */

function Avatar({ name, size = 40 }: { name: string; size?: number }) {
  return (
    <View
      style={{
        width: size,
        height: size,
        borderRadius: size / 2,
        backgroundColor: chat.orangeDark,
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

function TypingIndicator() {
  return (
    <View
      style={{
        flexDirection: "row",
        alignItems: "center",
        paddingLeft: 56,
        paddingVertical: 8,
        gap: 6,
      }}
    >
      <View
        style={{
          backgroundColor: chat.bgBubble,
          borderRadius: 16,
          paddingHorizontal: 14,
          paddingVertical: 10,
          flexDirection: "row",
          alignItems: "center",
          gap: 4,
        }}
      >
        {[0, 1, 2].map((i) => (
          <View
            key={i}
            style={{
              width: 6,
              height: 6,
              borderRadius: 3,
              backgroundColor: chat.typing,
              opacity: 0.5 + i * 0.15,
            }}
          />
        ))}
      </View>
    </View>
  );
}

function DateSeparator({ label }: { label: string }) {
  return (
    <View
      style={{
        alignItems: "center",
        paddingVertical: 12,
      }}
    >
      <View
        style={{
          backgroundColor: chat.bgSurface,
          borderRadius: 10,
          paddingHorizontal: 12,
          paddingVertical: 4,
        }}
      >
        <Text style={{ color: chat.textMuted, fontSize: 11, fontWeight: "500" }}>
          {label}
        </Text>
      </View>
    </View>
  );
}

/* ─── Main screen ─── */

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
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<ScrollView>(null);
  const inputRef = useRef<TextInput>(null);

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

      // Determine the other user from messages
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

      // Simulate typing indicator from other side
      setIsTyping(true);
      setTimeout(() => setIsTyping(false), 2000 + Math.random() * 2000);
    } catch (e) {
      console.error(e);
    } finally {
      setSending(false);
    }
  };

  const canSend = text.trim().length > 0 && !sending;

  return (
    <View style={{ flex: 1, backgroundColor: chat.bg }}>
      {/* ─── HEADER ─── */}
      <View
        style={{
          backgroundColor: chat.bgSurface,
          borderBottomWidth: 1,
          borderBottomColor: chat.border,
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
          {/* Back button */}
          <Pressable
            onPress={() => router.back()}
            style={({ pressed }) => ({
              width: 36,
              height: 36,
              borderRadius: 18,
              backgroundColor: chat.bgBubble,
              alignItems: "center",
              justifyContent: "center",
              opacity: pressed ? 0.7 : 1,
            })}
          >
            <Text style={{ color: chat.text, fontSize: 16 }}>←</Text>
          </Pressable>

          {/* Avatar + name */}
          <Avatar name={otherUser} size={40} />
          <View style={{ flex: 1 }}>
            <Text
              style={{
                color: chat.text,
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
                  backgroundColor: chat.green,
                }}
              />
              <Text style={{ color: chat.textMuted, fontSize: 12 }}>
                В сети
              </Text>
            </View>
          </View>

          {/* Optional: service badge */}
          <View
            style={{
              backgroundColor: chat.bgBubble,
              borderRadius: 8,
              paddingHorizontal: 10,
              paddingVertical: 4,
            }}
          >
            <Text style={{ color: chat.orange, fontSize: 11, fontWeight: "600" }}>
              Чат
            </Text>
          </View>
        </View>
      </View>

      {/* ─── MESSAGES ─── */}
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={Platform.OS === "ios" ? 0 : 0}
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
              <ActivityIndicator size="large" color={chat.orange} />
              <Text
                style={{ color: chat.textMuted, fontSize: 13, marginTop: 12 }}
              >
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
              <View
                style={{
                  width: 64,
                  height: 64,
                  borderRadius: 32,
                  backgroundColor: chat.bgBubble,
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: 16,
                }}
              >
                <Avatar name={otherUser} size={64} />
              </View>
              <Text
                style={{
                  color: chat.text,
                  fontSize: 16,
                  fontWeight: "600",
                  marginBottom: 4,
                }}
              >
                Начните разговор
              </Text>
              <Text
                style={{
                  color: chat.textMuted,
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
                {showDate && (
                  <DateSeparator label={formatDate(m.created_at)} />
                )}
                <View
                  style={{
                    flexDirection: "row",
                    justifyContent: isMe ? "flex-end" : "flex-start",
                    alignItems: "flex-end",
                    marginBottom: 4,
                    gap: 8,
                  }}
                >
                  {/* Other user avatar */}
                  {!isMe && <Avatar name={m.sender} size={28} />}

                  {/* Bubble */}
                  <View
                    style={{
                      backgroundColor: isMe
                        ? chat.bgBubbleMe
                        : chat.bgBubble,
                      borderRadius: isMe ? 18 : 18,
                      borderBottomRightRadius: isMe ? 4 : 18,
                      borderBottomLeftRadius: isMe ? 18 : 4,
                      paddingVertical: 10,
                      paddingHorizontal: 14,
                      maxWidth: "72%",
                    }}
                  >
                    {/* Sender label in group chats */}
                    {!isMe && messages[idx - 1]?.sender === m.sender ? null : (
                      !isMe && (
                        <Text
                          style={{
                            color: chat.orange,
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
                        color: isMe ? "#FFFFFF" : chat.text,
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
                          : chat.textMuted,
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

          {isTyping && <TypingIndicator />}
        </ScrollView>

        {/* ─── INPUT BAR ─── */}
        <View
          style={{
            backgroundColor: chat.bgSurface,
            borderTopWidth: 1,
            borderTopColor: chat.border,
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
            {/* Text input */}
            <View
              style={{
                flex: 1,
                backgroundColor: chat.bgBubble,
                borderRadius: 22,
                borderWidth: 1,
                borderColor: chat.border,
                minHeight: 44,
                maxHeight: 100,
                flexDirection: "row",
                alignItems: "flex-end",
                paddingHorizontal: 16,
                paddingVertical: Platform.OS === "web" ? 10 : 12,
              }}
            >
              <TextInput
                ref={inputRef}
                style={{
                  flex: 1,
                  color: chat.text,
                  fontSize: 15,
                  lineHeight: 20,
                  padding: 0,
                  ...(Platform.OS === "web"
                    ? { outlineStyle: "none" as any }
                    : {}),
                }}
                placeholder="Написать сообщение..."
                placeholderTextColor={chat.textMuted}
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

            {/* Send button */}
            <Pressable
              onPress={send}
              disabled={!canSend}
              style={({ pressed }) => ({
                width: 44,
                height: 44,
                borderRadius: 22,
                backgroundColor: canSend ? chat.sendBg : chat.sendDisabled,
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
                    color: canSend ? "#FFFFFF" : chat.textMuted,
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
