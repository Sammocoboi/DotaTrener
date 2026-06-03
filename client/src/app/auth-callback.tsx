import { useEffect } from "react";
import { View, Text } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { colors } from "./theme";

export default function AuthCallback() {
  const { token, steam_id, username, next } = useLocalSearchParams<{
    token: string;
    steam_id: string;
    username: string;
    next: string;
  }>();

  useEffect(() => {
    if (token) {
      saveToken(token, steam_id);
      const target = next || "profile";
      router.replace({
        pathname: target as any,
        params: { token, steam_id: steam_id || "" },
      });
    }
  }, [token]);

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg }}>
      <Text style={{ color: colors.text60 }}>Вход через Steam...</Text>
    </View>
  );
}

import { saveToken } from "./token-storage";
