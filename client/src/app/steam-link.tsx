import { useEffect, useState } from "react";
import { View, Text, Button, Platform } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import * as WebBrowser from "expo-web-browser";

const API = "http://127.0.0.1:8000";

export default function SteamLink() {
  const { token, steam_id } = useLocalSearchParams<{ token: string; steam_id: string }>();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token && steam_id) {
      router.replace({ pathname: "matches" as any, params: { token, steam_id } });
    }
  }, [token]);

  const loginWithSteam = async () => {
    if (Platform.OS === "web") {
      window.location.href = `${API}/api/auth/steam/login/`;
      return;
    }
    setLoading(true);
    try {
      await WebBrowser.openBrowserAsync(`${API}/api/auth/steam/login/`);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1, padding: 16, justifyContent: "center", alignItems: "center", gap: 16 }}>
      <Text>Войдите через Steam для синхронизации матчей</Text>
      <Button
        title={loading ? "Открываю Steam..." : "Войти через Steam"}
        onPress={loginWithSteam}
        disabled={loading}
      />
    </View>
  );
}
