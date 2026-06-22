import { useState } from "react";
import { View, Text, TextInput, Pressable, Alert, Platform } from "react-native";
import { router } from "expo-router";
import * as WebBrowser from "expo-web-browser";
import { colors } from "@/lib/theme";
import { API_ROOT } from "@/lib/api";
import { saveToken } from "@/lib/token-storage";

export default function LoginScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email.trim() || !password) {
      Alert.alert("Ошибка", "Введите email и пароль");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_ROOT}/api/auth/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        Alert.alert("Ошибка", data.error || "Неверный email или пароль");
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

  const handleSteamLogin = async () => {
    if (Platform.OS === "web") {
      const returnUrl = encodeURIComponent(window.location.origin);
      const url = `${API_ROOT}/api/auth/steam/login/?next=profile&return_to=${returnUrl}`;
      window.location.href = url;
    } else {
      const url = `${API_ROOT}/api/auth/steam/login/?next=profile`;
      await WebBrowser.openAuthSessionAsync(url, "dotatrener://auth-callback");
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", padding: 32 }}>
      <Text style={{ color: colors.text, fontSize: 28, fontWeight: "800", letterSpacing: 1, marginBottom: 8, textAlign: "center" }}>
        DOTA TRENER
      </Text>
      <Text style={{ color: colors.text60, fontSize: 14, marginBottom: 36, textAlign: "center" }}>
        Твой персональный коуч
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
          placeholder="Пароль"
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
        onPress={handleLogin}
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
          {loading ? "Вход..." : "Войти"}
        </Text>
      </Pressable>

      <Pressable
        onPress={handleSteamLogin}
        style={({ pressed }) => ({
          backgroundColor: colors.bgCard,
          borderWidth: 1,
          borderColor: colors.border,
          paddingVertical: 14,
          borderRadius: 12,
          alignItems: "center",
          marginTop: 12,
          opacity: pressed ? 0.7 : 1,
        })}
      >
        <Text style={{ color: colors.text80, fontSize: 14, fontWeight: "600" }}>
          Войти через Steam
        </Text>
      </Pressable>

      <Pressable
        onPress={() => router.replace("/register")}
        style={{ marginTop: 20, alignItems: "center" }}
      >
        <Text style={{ color: colors.text60, fontSize: 14 }}>
          Нет аккаунта? <Text style={{ color: colors.orange, fontWeight: "600" }}>Зарегистрироваться</Text>
        </Text>
      </Pressable>
    </View>
  );
}
