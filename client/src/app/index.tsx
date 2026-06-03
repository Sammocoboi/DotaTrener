import { useEffect, useState } from "react";
import { router } from "expo-router";
import { View, Text, Pressable, ScrollView } from "react-native";
import axios from "axios";
import { getToken } from "./token-storage";
import { colors } from "./theme";

const API = "http://127.0.0.1:8000/api/coaching";

export default function HomeScreen() {
  const token = getToken();
  const [stats, setStats] = useState<{ wins: number; losses: number; winRate: number } | null>(null);

  useEffect(() => {
    if (!token) return;
    axios
      .get(`${API}/profile/`, { headers: { Authorization: `Token ${token}` } })
      .then((res) => {
        const ms = res.data.match_stats;
        if (ms) {
          setStats({ wins: ms.win_count, losses: ms.lose_count, winRate: ms.win_rate });
        }
      })
      .catch(() => {});
  }, []);

  const navItems = [
    { label: "Герои", route: "./heroes/Hero", color: colors.orange },
    { label: "Мета Героев", route: "./heroes/HeroMeta", color: colors.purple },
    { label: "Тренеры", route: "coaches", color: colors.green },
    { label: "Мои матчи", route: "matches", color: colors.orange },
    { label: "Аккаунт", route: "profile", color: colors.orange },
    { label: "Сообщения", route: "conversations", color: colors.purpleLight },
    { label: "Привязать Steam", route: "steam-link", color: colors.text60 },
  ];

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }} contentContainerStyle={{ padding: 16 }}>
      <View style={{ alignItems: "center", marginTop: 16, marginBottom: 24 }}>
        <Text style={{ color: colors.text, fontSize: 28, fontWeight: "800", letterSpacing: 1 }}>DOTA TRENER</Text>
        <Text style={{ color: colors.text60, fontSize: 13, marginTop: 4, letterSpacing: 0.5 }}>Твой персональный коуч</Text>
      </View>

      <View style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: colors.borderSoft }}>
        <Text style={{ color: colors.text60, fontSize: 11, fontWeight: "600", letterSpacing: 1, marginBottom: 8 }}>РЕКОМЕНДАЦИИ ПО ГЕРОЯМ</Text>
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
          <Text style={{ color: colors.text80, fontSize: 14 }}>Анализ последних матчей</Text>
          <Pressable onPress={() => router.push("./heroes/HeroMeta")} style={{ backgroundColor: colors.orange, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 }}>
            <Text style={{ color: colors.text, fontSize: 12, fontWeight: "600" }}>Смотреть</Text>
          </Pressable>
        </View>
      </View>

      <View style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, marginBottom: 16, borderWidth: 1, borderColor: colors.borderSoft }}>
        <Text style={{ color: colors.text60, fontSize: 11, fontWeight: "600", letterSpacing: 1, marginBottom: 8 }}>СВОДКА МАТЧЕЙ</Text>
        <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
          <View style={{ alignItems: "center", flex: 1 }}>
            <Text style={{ color: colors.green, fontSize: 20, fontWeight: "700" }}>{stats ? stats.wins : "—"}</Text>
            <Text style={{ color: colors.text40, fontSize: 10, marginTop: 2, letterSpacing: 0.5 }}>ПОБЕД</Text>
          </View>
          <View style={{ alignItems: "center", flex: 1 }}>
            <Text style={{ color: colors.red, fontSize: 20, fontWeight: "700" }}>{stats ? stats.losses : "—"}</Text>
            <Text style={{ color: colors.text40, fontSize: 10, marginTop: 2, letterSpacing: 0.5 }}>ПОРАЖЕНИЙ</Text>
          </View>
          <View style={{ alignItems: "center", flex: 1 }}>
            <Text style={{ color: colors.text80, fontSize: 20, fontWeight: "700" }}>{stats ? `${stats.winRate}%` : "0%"}</Text>
            <Text style={{ color: colors.text40, fontSize: 10, marginTop: 2, letterSpacing: 0.5 }}>ВИНРЕЙТ</Text>
          </View>
        </View>
      </View>

      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
        {navItems.map((item) => (
          <Pressable
            key={item.route}
            onPress={() => router.push(item.route as any)}
            style={{ width: "48%", backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, borderWidth: 1, borderColor: colors.borderSoft, marginBottom: 4 }}
          >
            <Text style={{ color: item.color, fontSize: 15, fontWeight: "700", marginBottom: 2 }}>{item.label}</Text>
            <Text style={{ color: colors.text40, fontSize: 11, letterSpacing: 0.5 }}>ПЕРЕЙТИ →</Text>
          </Pressable>
        ))}
      </View>
    </ScrollView>
  );
}
