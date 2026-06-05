import { View, Text, Pressable } from 'react-native';
import { router } from "expo-router";
import { colors } from "@/lib/theme";

export default function Explore() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg, padding: 16 }}>
      <Pressable onPress={() => router.push("/")} style={{ position: "absolute", top: 16, left: 16 }}>
        <Text style={{ color: colors.orange }}>← Назад</Text>
      </Pressable>
      <Text style={{ color: colors.text60, fontSize: 15 }}>Страница исследования</Text>
    </View>
  );
}
