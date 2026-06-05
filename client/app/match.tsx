import { View, Text, Pressable, ScrollView } from "react-native";
import { router } from "expo-router";
import { colors } from "@/lib/theme";

export default function MatchScreen() {
  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
          <Text style={{ color: colors.orange }}>← Назад</Text>
        </Pressable>
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700" }}>Матч</Text>
      </ScrollView>
    </View>
  );
}
