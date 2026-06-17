import { useState } from "react";
import { View, Text, TextInput, Pressable, Alert } from "react-native";
import { router } from "expo-router";
import { colors } from "@/lib/theme";
import { API_ROOT } from "@/lib/api";
import { saveToken } from "@/lib/token-storage";

export default function RegisterScreen() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!email.trim() || !username.trim() || !password) {
      Alert.alert("Ошибка", "Заполните все поля");
      return;
    }
    if (password.length < 6) {
      Alert.alert("Ошибка", "Пароль минимум 6 символов");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_ROOT}/api/auth/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          username: username.trim(),
          password,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        Alert.alert("Ошибка", data.error || "Не удалось зарегистрироваться");
        return;
      }
      saveToken(data.token, data.steam_id || null);
      router.replace("/profile");
    } catch {
      Alert.alert("Ошибка", "Нет соединения с сервером");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", padding: 32 }}>
      <Text style={{ color: colors.text, fontSize: 28, fontWeight: "800", letterSpacing: 1, marginBottom: 8, textAlign: "center" }}>
        РЕГИСТРАЦИЯ
      </Text>
      <Text style={{ color: colors.text60, fontSize: 14, marginBottom: 36, textAlign: "center" }}>
        Создай аккаунт DotaTrener
      </Text>

      <View style={{ gap: 14 }}>
        <TextInput
          placeholder="Email"
          placeholderTextColor={colors.text40}
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
          style={{
            backgroundColor: colors.bgCard,
            borderRadius: 12,
            borderWidth: 1,
            borderColor: colors.border,
            paddingHorizontal: 16,
            paddingVertical: 14,
            fontSize: 15,
            color: colors.text,
          }}
        />
        <TextInput
          placeholder="Имя пользователя"
          placeholderTextColor={colors.text40}
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
          style={{
            backgroundColor: colors.bgCard,
            borderRadius: 12,
            borderWidth: 1,
            borderColor: colors.border,
            paddingHorizontal: 16,
            paddingVertical: 14,
            fontSize: 15,
            color: colors.text,
          }}
        />
        <TextInput
          placeholder="Пароль (минимум 6 символов)"
          placeholderTextColor={colors.text40}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          style={{
            backgroundColor: colors.bgCard,
            borderRadius: 12,
            borderWidth: 1,
            borderColor: colors.border,
            paddingHorizontal: 16,
            paddingVertical: 14,
            fontSize: 15,
            color: colors.text,
          }}
        />
      </View>

      <Pressable
        onPress={handleRegister}
        disabled={loading}
        style={({ pressed }) => ({
          backgroundColor: pressed ? colors.orangeDark : colors.orange,
          paddingVertical: 16,
          borderRadius: 12,
          alignItems: "center",
          marginTop: 24,
          opacity: loading ? 0.6 : 1,
        })}
      >
        <Text style={{ color: "#FFFFFF", fontSize: 16, fontWeight: "700" }}>
          {loading ? "Регистрация..." : "Зарегистрироваться"}
        </Text>
      </Pressable>

      <Pressable
        onPress={() => router.replace("/login")}
        style={{ marginTop: 20, alignItems: "center" }}
      >
        <Text style={{ color: colors.text60, fontSize: 14 }}>
          Уже есть аккаунт? <Text style={{ color: colors.orange, fontWeight: "600" }}>Войти</Text>
        </Text>
      </Pressable>
    </View>
  );
}
