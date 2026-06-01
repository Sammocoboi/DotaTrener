import { useEffect } from "react";
import { View, Text } from "react-native";
import { router, useLocalSearchParams } from "expo-router";

export default function AuthCallback() {
  const { token, steam_id, username } = useLocalSearchParams<{
    token: string;
    steam_id: string;
    username: string;
  }>();

  useEffect(() => {
    if (token) {
      router.replace({
        pathname: "stratz-token" as any,
        params: { token, steam_id: steam_id || "" },
      });
    }
  }, [token]);

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <Text>Вход через Steam...</Text>
    </View>
  );
}
