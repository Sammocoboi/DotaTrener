import { useEffect, useState } from "react";
import { View, Text, Image, Pressable, ScrollView } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { colors } from "../theme";

const API = "http://127.0.0.1:8000/api/coaching";

type ItemEntry = {
  id: number;
  name: string;
  image: string;
  time: number | null;
};

type SkillEntry = {
  id: number;
  name: string;
  image: string;
};

type Build = {
  build_type: "item" | "skill";
  sequence: (ItemEntry | SkillEntry)[];
  win_rate: number;
  games: number;
  role?: string;
};

type HeroBuilds = {
  hero_id: number;
  hero_name: string;
  hero_image: string;
  item_builds: Build[];
  skill_builds: Build[];
};

function formatTime(minutes: number | null): string {
  if (!minutes) return "";
  return `${minutes} min`;
}

export default function HeroDetailScreen() {
  const { hero_id } = useLocalSearchParams<{ hero_id: string }>();
  const [data, setData] = useState<HeroBuilds | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"items" | "skills">("items");

  useEffect(() => {
    if (!hero_id) return;
    setLoading(true);
    axios
      .get(`${API}/hero/${hero_id}/builds/`)
      .then((res) => setData(res.data))
      .catch((e) => setError(e?.response?.data?.error || "Ошибка загрузки"))
      .finally(() => setLoading(false));
  }, [hero_id]);

  if (loading) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg }}><Text style={{ color: colors.text60 }}>Загрузка...</Text></View>;
  if (error) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg }}><Text style={{ color: colors.red }}>{error}</Text></View>;
  if (!data) return null;

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }} contentContainerStyle={{ padding: 16 }}>
      <Pressable onPress={() => router.push("/")} style={{ marginBottom: 12 }}>
        <Text style={{ color: colors.orange, fontSize: 14 }}>← Назад</Text>
      </Pressable>

      <View style={{ flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 16 }}>
        {data.hero_image ? <Image source={{ uri: data.hero_image }} style={{ width: 56, height: 56, borderRadius: 10 }} /> : null}
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700" }}>{data.hero_name}</Text>
      </View>

      <View style={{ flexDirection: "row", gap: 8, marginBottom: 16 }}>
        <TabButton label="Предметы" active={tab === "items"} onPress={() => setTab("items")} />
        <TabButton label="Скиллы" active={tab === "skills"} onPress={() => setTab("skills")} />
      </View>

      {tab === "items" && (
        <View style={{ gap: 12 }}>
          {data.item_builds.length === 0 && <Text style={{ color: colors.text60 }}>Нет данных</Text>}
          {data.item_builds.map((build, i) => (
            <BuildCard key={i} build={build} />
          ))}
        </View>
      )}

      {tab === "skills" && (
        <View style={{ gap: 12 }}>
          {data.skill_builds.length === 0 && <Text style={{ color: colors.text60 }}>Нет данных</Text>}
          {data.skill_builds.map((build, i) => (
            <SkillBuildCard key={i} build={build} />
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const TabButton = ({ label, active, onPress }: { label: string; active: boolean; onPress: () => void }) => (
  <Pressable
    onPress={onPress}
    style={{
      paddingHorizontal: 16,
      paddingVertical: 8,
      borderRadius: 8,
      backgroundColor: active ? colors.orange : colors.border,
    }}
  >
    <Text style={{ color: active ? colors.text : colors.text60, fontSize: 13, fontWeight: "600" }}>{label}</Text>
  </Pressable>
);

const BuildCard = ({ build }: { build: Build }) => {
  const items = build.sequence as ItemEntry[];
  return (
    <View style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, borderWidth: 1, borderColor: colors.borderSoft }}>
      <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
        <Text style={{ color: colors.text60, fontSize: 12 }}>
          {build.role ? build.role.replace("time_", "Тайминг: ") : "Endgame"}
        </Text>
        <Text style={{ color: colors.greenLight, fontSize: 12, fontWeight: "600" }}>
          {build.win_rate.toFixed(1)}% WR · {build.games} games
        </Text>
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={{ flexDirection: "row", gap: 8 }}>
          {items.map((item, j) => (
            <View key={j} style={{ alignItems: "center", width: 52 }}>
              {item.image ? <Image source={{ uri: item.image }} style={{ width: 44, height: 44, borderRadius: 6 }} /> : <View style={{ width: 44, height: 44, borderRadius: 6, backgroundColor: colors.bgElevated }} />}
              {item.time != null && item.time > 0 ? (
                <Text style={{ color: colors.orange, fontSize: 10, marginTop: 2 }}>{formatTime(item.time)}</Text>
              ) : (
                <Text style={{ color: colors.text40, fontSize: 10, marginTop: 2 }}>—</Text>
              )}
              <Text style={{ color: colors.text80, fontSize: 9, textAlign: "center" }} numberOfLines={1}>{item.name}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
};

const SkillBuildCard = ({ build }: { build: Build }) => {
  const skills = build.sequence as SkillEntry[];
  return (
    <View style={{ backgroundColor: colors.bgCard, borderRadius: 14, padding: 16, borderWidth: 1, borderColor: colors.borderSoft }}>
      <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
        <Text style={{ color: colors.text60, fontSize: 12 }}>Раскачка</Text>
        <Text style={{ color: colors.greenLight, fontSize: 12, fontWeight: "600" }}>
          {build.win_rate.toFixed(1)}% WR · {build.games} games
        </Text>
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={{ flexDirection: "row", gap: 4 }}>
          {skills.map((skill, j) => (
            <View key={j} style={{ alignItems: "center", width: 48 }}>
              {skill.image ? <Image source={{ uri: skill.image }} style={{ width: 40, height: 40, borderRadius: 6 }} /> : <View style={{ width: 40, height: 40, borderRadius: 6, backgroundColor: colors.bgElevated }} />}
              <Text style={{ color: colors.text80, fontSize: 9, textAlign: "center", marginTop: 2 }} numberOfLines={1}>{skill.name}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
};
