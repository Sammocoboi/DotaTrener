import { useState } from "react";
import { View, Text, TextInput, Pressable } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "./token-storage";
import { colors } from "./theme";

const API = "http://127.0.0.1:8000/api/coaching";

export default function StratzTokenScreen() {
  const params = useLocalSearchParams<{ token: string }>();
  const token = params.token || getToken();
  const [stratzToken, setStratzToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const save = async () => {
    if (!stratzToken.trim()) return;
    setLoading(true);
    setErr("");
    try {
      await axios.post(
        `${API}/set-stratz-token/`,
        { stratz_token: stratzToken.trim() },
        { headers: { Authorization: `Token ${token}` } }
      );
      router.replace({ pathname: "matches" as any, params: { token } });
    } catch (e: any) {
      setErr(e?.response?.data?.error || "Не удалось сохранить");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1, padding: 16, backgroundColor: colors.bg }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 16 }}>
        <Text style={{ color: colors.orange }}>← Назад</Text>
      </Pressable>
      <View style={{ flex: 1, justifyContent: "center", gap: 16 }}>
        <Text style={{ color: colors.text, fontSize: 18, fontWeight: "700" }}>Stratz API Token</Text>
        <Text style={{ color: colors.text60, fontSize: 12, lineHeight: 18 }}>
          1. Войди на stratz.com{"\n"}
          2. Открой stratz.com/api{"\n"}
          3. Скопируй токен и вставь сюда
        </Text>
        <TextInput
          value={stratzToken}
          onChangeText={setStratzToken}
          placeholder="eyJhbGciOiJIUzI1NiIs..."
          placeholderTextColor={colors.text40}
          style={{ backgroundColor: colors.bgElevated, color: colors.text, borderWidth: 1, borderColor: colors.border, padding: 12, borderRadius: 8, fontSize: 13 }}
        />
        {err ? <Text style={{ color: colors.red, fontSize: 12 }}>{err}</Text> : null}
        <Pressable
          onPress={save}
          disabled={loading || !stratzToken.trim()}
          style={{ backgroundColor: stratzToken.trim() ? colors.orange : colors.bgElevated, padding: 14, borderRadius: 8, alignItems: "center" }}
        >
          <Text style={{ color: stratzToken.trim() ? colors.text : colors.text40, fontWeight: "700" }}>{loading ? "..." : "Сохранить"}</Text>
        </Pressable>
        <Pressable
          onPress={() => router.replace({ pathname: "matches" as any, params: { token } })}
          style={{ backgroundColor: colors.bgRow, padding: 14, borderRadius: 8, alignItems: "center" }}
        >
          <Text style={{ color: colors.orange, fontWeight: "600" }}>Пропустить</Text>
        </Pressable>
      </View>
    </View>
  );
}
