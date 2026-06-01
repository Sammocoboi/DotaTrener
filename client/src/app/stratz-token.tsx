import { useState } from "react";
import { View, Text, TextInput, Button, Alert } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";

const API = "http://127.0.0.1:8000/api/coaching";

export default function StratzTokenScreen() {
  const { token } = useLocalSearchParams<{ token: string }>();
  const [stratzToken, setStratzToken] = useState("");
  const [loading, setLoading] = useState(false);

  const save = async () => {
    if (!stratzToken.trim()) return;
    setLoading(true);
    try {
      await axios.post(
        `${API}/set-stratz-token/`,
        { stratz_token: stratzToken.trim() },
        { headers: { Authorization: `Token ${token}` } }
      );
      Alert.alert("OK", "Токен сохранён", [
        { text: "Матчи", onPress: () => router.replace({ pathname: "matches" as any, params: { token } }) },
      ]);
    } catch (e: any) {
      Alert.alert("Ошибка", e?.response?.data?.error || "Не удалось сохранить");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1, padding: 16, justifyContent: "center", gap: 12 }}>
      <Text>Stratz API Token</Text>
      <Text style={{ fontSize: 12, color: "#666" }}>
        1. Войди на stratz.com{"\n"}
        2. Открой stratz.com/api{"\n"}
        3. Скопируй токен и вставь сюда
      </Text>
      <TextInput
        value={stratzToken}
        onChangeText={setStratzToken}
        placeholder="eyJhbGciOiJIUzI1NiIs..."
        style={{ borderWidth: 1, borderColor: "#ccc", padding: 12, borderRadius: 8 }}
      />
      <Button title={loading ? "..." : "Сохранить"} onPress={save} disabled={loading} />
      <Button title="Пропустить" onPress={() => router.replace({ pathname: "matches" as any, params: { token } })} />
    </View>
  );
}
