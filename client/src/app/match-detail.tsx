import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, Image } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";

const API = "http://127.0.0.1:8000/api/coaching";

type ItemEntry = { id: number; name: string; image: string; time: number | null };
type SkillEntry = { id: number; name: string; image: string };
type Build = { build_type: string; sequence: (ItemEntry | SkillEntry)[]; win_rate: number; games: number; role?: string };
type TalentEntry = { abilityId: number; tier: number; slot: "left" | "right"; name: string; image: string; matchCount: number; win_rate: number; pick_rate: number };

type PlayerData = {
  hero_id: number;
  hero_name: string;
  hero_image: string;
  is_radiant: boolean;
  kills: number;
  deaths: number;
  assists: number;
  gpm: number;
  xpm: number;
  last_hits: number;
  denies: number;
  hero_damage: number;
  tower_damage: number;
  networth: number;
  items: { id: number; name: string; image: string; time: number | null }[];
  abilities: { id: number; name: string; image: string; level: number; time: number | null }[];
  talents: { id: number; name: string; image: string; level: number; time: number | null }[];
};

type MatchDetail = {
  match_id: string;
  duration: number;
  radiant_win: boolean;
  start_time: number;
  players: PlayerData[];
};

type HeroBuilds = {
  hero_id: number;
  hero_name: string;
  hero_image: string;
  item_builds: Build[];
  skill_builds: Build[];
  talent_builds: TalentEntry[];
};

function formatTime(mins: number): string {
  return `${mins} min`;
}

function formatTimePlayer(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function MatchDetailScreen() {
  const { token, match_id } = useLocalSearchParams<{ token: string; match_id: string }>();
  const [data, setData] = useState<MatchDetail | null>(null);
  const [heroBuilds, setHeroBuilds] = useState<Record<number, HeroBuilds>>({});
  const [loading, setLoading] = useState(true);
  const [expandedHero, setExpandedHero] = useState<number | null>(null);

  useEffect(() => {
    if (!match_id) return;
    setLoading(true);
    axios
      .get(`${API}/match/${match_id}/`, {
        headers: token ? { Authorization: `Token ${token}` } : {},
      })
      .then((res) => {
        setData(res.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [match_id]);

  const loadBuilds = (heroId: number) => {
    if (heroBuilds[heroId]) return;
    axios
      .get(`${API}/hero/${heroId}/builds/`)
      .then((r) => setHeroBuilds((prev) => ({ ...prev, [heroId]: r.data })))
      .catch(() => {});
  };

  if (loading) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}><Text style={{ color: "#94A3B8" }}>Загрузка...</Text></View>;
  if (!data) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}><Text style={{ color: "#94A3B8" }}>Матч не найден</Text></View>;

  const radiant = data.players.filter((p) => p.is_radiant);
  const dire = data.players.filter((p) => !p.is_radiant);

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#0B1120" }} contentContainerStyle={{ paddingBottom: 40 }}>
      <View style={{ padding: 16 }}>
        <Pressable onPress={() => router.back()}>
          <Text style={{ color: "#60A5FA", marginBottom: 12 }}>← Назад</Text>
        </Pressable>

        <Text style={{ color: "#FFF", fontSize: 20, fontWeight: "700" }}>Match {data.match_id}</Text>
        <Text style={{ color: "#94A3B8", marginBottom: 16 }}>
          {data.radiant_win ? "Radiant Victory" : "Dire Victory"}
        </Text>

        <TeamBlock label="RADIANT" won={data.radiant_win} players={radiant} heroBuilds={heroBuilds} expandedHero={expandedHero} setExpandedHero={setExpandedHero} loadBuilds={loadBuilds} />
        <View style={{ height: 16 }} />
        <TeamBlock label="DIRE" won={!data.radiant_win} players={dire} heroBuilds={heroBuilds} expandedHero={expandedHero} setExpandedHero={setExpandedHero} loadBuilds={loadBuilds} />
      </View>
    </ScrollView>
  );
}

function TeamBlock({ label, won, players, heroBuilds, expandedHero, setExpandedHero, loadBuilds }: {
  label: string; won: boolean; players: PlayerData[];
  heroBuilds: Record<number, HeroBuilds>; expandedHero: number | null; setExpandedHero: (id: number | null) => void; loadBuilds: (id: number) => void;
}) {
  return (
    <View>
      <Text style={{ color: won ? "#22C55E" : "#EF4444", fontWeight: "700", marginBottom: 8 }}>{label} {won ? "WIN" : "LOSS"}</Text>
      {players.map((p, i) => {
        const isExpanded = expandedHero === p.hero_id;
        const builds = heroBuilds[p.hero_id];
        return (
          <View key={i}>
            <Pressable
              onPress={() => {
                if (!isExpanded) loadBuilds(p.hero_id);
                setExpandedHero(isExpanded ? null : p.hero_id);
              }}
              style={{ flexDirection: "row", alignItems: "center", paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: "rgba(255,255,255,0.05)", gap: 8 }}
            >
              {p.hero_image ? <Image source={{ uri: p.hero_image }} style={{ width: 36, height: 36, borderRadius: 6 }} /> : <View style={{ width: 36, height: 36, borderRadius: 6, backgroundColor: "#1E293B" }} />}
              <View style={{ flex: 1 }}>
                <Text style={{ color: "#60A5FA", fontSize: 13, fontWeight: "600" }}>{p.hero_name || `Hero ${p.hero_id}`}</Text>
                <Text style={{ color: "#94A3B8", fontSize: 11 }}>{p.kills}/{p.deaths}/{p.assists} | LH/DN {p.last_hits}/{p.denies}</Text>
              </View>
              <View style={{ alignItems: "flex-end" }}>
                <Text style={{ color: "#CBD5E1", fontSize: 12 }}>GPM {p.gpm}</Text>
                <Text style={{ color: "#CBD5E1", fontSize: 12 }}>XPM {p.xpm}</Text>
              </View>
              <View style={{ alignItems: "flex-end" }}>
                <Text style={{ color: "#CBD5E1", fontSize: 11 }}>DMG {p.hero_damage}</Text>
                <Text style={{ color: "#CBD5E1", fontSize: 11 }}>TD {p.tower_damage}</Text>
              </View>
              <View style={{ flexDirection: "row", gap: 3, flexWrap: "wrap", maxWidth: 180 }}>
                {p.items.map((item, idx) =>
                  item.image ? <Image key={idx} source={{ uri: item.image }} style={{ width: 30, height: 30, borderRadius: 4 }} /> : <View key={idx} style={{ width: 30, height: 30, borderRadius: 4, backgroundColor: "#1E293B" }} />
                )}
              </View>
            </Pressable>
            {isExpanded && builds && <HeroBuildsSection builds={builds} playerItems={p.items} playerAbilities={p.abilities} playerTalents={p.talents} />}
          </View>
        );
      })}
    </View>
  );
}

function HeroBuildsSection({ builds, playerItems, playerAbilities, playerTalents }: { builds: HeroBuilds; playerItems?: { id: number; name: string; image: string; time: number | null }[]; playerAbilities?: { id: number; name: string; image: string; level: number; time: number | null }[]; playerTalents?: { id: number; name: string; image: string; level: number; time: number | null }[] }) {
  const topItem = builds.item_builds[0];
  const topSkill = builds.skill_builds[0];

  const talentsByTier: Record<number, { left?: TalentEntry; right?: TalentEntry }> = {};
  for (const t of builds.talent_builds ?? []) {
    if (!talentsByTier[t.tier]) talentsByTier[t.tier] = {};
    talentsByTier[t.tier][t.slot] = t;
  }

  const playerTierMap: Record<number, { id: number; name: string; image: string }> = {};
  for (const pt of playerTalents ?? []) {
    const metaTalent = (builds.talent_builds ?? []).find(mt => mt.abilityId === pt.id);
    const tier = metaTalent?.tier ?? 0;
    if (!playerTierMap[tier]) {
      playerTierMap[tier] = { id: pt.id, name: pt.name, image: pt.image };
    } else if (tier === 0) {
      playerTierMap[tier] = { id: pt.id, name: pt.name, image: pt.image };
    }
  }

  return (
    <View style={{ backgroundColor: "#0F1729", borderRadius: 8, padding: 10, marginBottom: 6, marginLeft: 44, borderWidth: 1, borderColor: "rgba(255,255,255,0.04)" }}>
      {topItem && (
        <View style={{ flexDirection: "row", gap: 16, marginBottom: 12 }}>
          <View style={{ flex: 1 }}>
            <Text style={{ color: "#94A3B8", fontSize: 11, marginBottom: 4 }}>
              Мета · {topItem.win_rate.toFixed(1)}% WR · {topItem.games} games
            </Text>
            <View style={{ flexDirection: "row", gap: 4, flexWrap: "wrap" }}>
              {(topItem.sequence as ItemEntry[]).map((item, j) => (
                <View key={j} style={{ alignItems: "center", width: 44 }}>
                  {item.image ? <Image source={{ uri: item.image }} style={{ width: 36, height: 36, borderRadius: 4 }} /> : <View style={{ width: 36, height: 36, borderRadius: 4, backgroundColor: "#1E293B" }} />}
                  {item.time != null && item.time > 0 && <Text style={{ color: "#F59E0B", fontSize: 9, marginTop: 1 }}>{formatTime(item.time)}</Text>}
                  <Text style={{ color: "#CBD5E1", fontSize: 8 }} numberOfLines={1}>{item.name}</Text>
                </View>
              ))}
            </View>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={{ color: "#60A5FA", fontSize: 11, marginBottom: 4, fontWeight: "600" }}>Твой билд</Text>
            <View style={{ flexDirection: "row", gap: 4, flexWrap: "wrap" }}>
              {(playerItems ?? []).map((item, j) => (
                <View key={j} style={{ alignItems: "center", width: 44 }}>
                  {item.image ? <Image source={{ uri: item.image }} style={{ width: 36, height: 36, borderRadius: 4 }} /> : <View style={{ width: 36, height: 36, borderRadius: 4, backgroundColor: "#1E293B" }} />}
                  {item.time != null && item.time > 0 && <Text style={{ color: "#F59E0B", fontSize: 9, marginTop: 1 }}>{formatTimePlayer(item.time)}</Text>}
                  <Text style={{ color: "#CBD5E1", fontSize: 8 }} numberOfLines={1}>{item.name}</Text>
                </View>
              ))}
              {(playerItems ?? []).length === 0 && <Text style={{ color: "#64748B", fontSize: 11 }}>Нет данных</Text>}
            </View>
          </View>
        </View>
      )}
      <View style={{ flexDirection: "row", gap: 16 }}>
        {topSkill && (
          <View style={{ flex: 1 }}>
            <Text style={{ color: "#94A3B8", fontSize: 11, marginBottom: 4 }}>
              Мета раскачка · {topSkill.win_rate.toFixed(1)}% WR · {topSkill.games} games
            </Text>
            <View style={{ flexDirection: "row", gap: 2, flexWrap: "wrap" }}>
              {(topSkill.sequence as SkillEntry[]).map((skill, j) => (
                <View key={j} style={{ alignItems: "center", width: 32 }}>
                  <View style={{ position: "relative" }}>
                    {skill.image ? <Image source={{ uri: skill.image }} style={{ width: 30, height: 30, borderRadius: 4 }} /> : <View style={{ width: 30, height: 30, borderRadius: 4, backgroundColor: "#1E293B" }} />}
                    <View style={{ position: "absolute", top: -4, right: -4, backgroundColor: "#0B1120", borderRadius: 6, width: 14, height: 14, alignItems: "center", justifyContent: "center" }}>
                      <Text style={{ color: "#F59E0B", fontSize: 8, fontWeight: "700" }}>{j + 1}</Text>
                    </View>
                  </View>
                  <Text style={{ color: "#CBD5E1", fontSize: 7, marginTop: 1 }} numberOfLines={1}>{skill.name}</Text>
                </View>
              ))}
            </View>
          </View>
        )}
        {(playerAbilities ?? []).length > 0 && (
          <View style={{ flex: 1 }}>
            <Text style={{ color: "#60A5FA", fontSize: 11, marginBottom: 4, fontWeight: "600" }}>Твоя раскачка</Text>
            <View style={{ flexDirection: "row", gap: 4, flexWrap: "wrap" }}>
              {(playerAbilities ?? []).slice(0, 15).map((ab, j) => (
                <View key={j} style={{ alignItems: "center", width: 36 }}>
                  {ab.image ? <Image source={{ uri: ab.image }} style={{ width: 32, height: 32, borderRadius: 4 }} /> : <View style={{ width: 32, height: 32, borderRadius: 4, backgroundColor: "#1E293B" }} />}
                  <Text style={{ color: "#CBD5E1", fontSize: 8, marginTop: 1 }} numberOfLines={1}>{ab.name}</Text>
                </View>
              ))}
            </View>
          </View>
        )}
      </View>
      <View style={{ flexDirection: "row", gap: 16, marginTop: 8 }}>
        <View style={{ flex: 1 }}>
          <Text style={{ color: "#94A3B8", fontSize: 11, marginBottom: 4 }}>Мета таланты</Text>
          {[10, 15, 20, 25].map(tier => {
            const pair = talentsByTier[tier];
            if (!pair) return null;
            return (
              <View key={tier} style={{ flexDirection: "row", alignItems: "center", marginBottom: 4 }}>
                <Text style={{ color: "#64748B", fontSize: 9, width: 20 }}>{tier}</Text>
                <View style={{ flexDirection: "column", gap: 2, flex: 1 }}>
                  {pair.left && (
                    <View style={{ flexDirection: "row", alignItems: "center", gap: 2 }}>
                      {pair.left.image ? <Image source={{ uri: pair.left.image }} style={{ width: 18, height: 18, borderRadius: 3 }} /> : <View style={{ width: 18, height: 18, borderRadius: 3, backgroundColor: "#1E293B" }} />}
                      <Text style={{ color: "#CBD5E1", fontSize: 7 }} numberOfLines={1}>{pair.left.name}</Text>
                      <Text style={{ color: "#A5B4FC", fontSize: 6 }}>{pair.left.pick_rate}% {pair.left.win_rate}%WR</Text>
                    </View>
                  )}
                  {pair.right && (
                    <View style={{ flexDirection: "row", alignItems: "center", gap: 2 }}>
                      {pair.right.image ? <Image source={{ uri: pair.right.image }} style={{ width: 18, height: 18, borderRadius: 3 }} /> : <View style={{ width: 18, height: 18, borderRadius: 3, backgroundColor: "#1E293B" }} />}
                      <Text style={{ color: "#CBD5E1", fontSize: 7 }} numberOfLines={1}>{pair.right.name}</Text>
                      <Text style={{ color: "#A5B4FC", fontSize: 6 }}>{pair.right.pick_rate}% {pair.right.win_rate}%WR</Text>
                    </View>
                  )}
                </View>
              </View>
            );
          })}
        </View>
        <View style={{ flex: 1 }}>
          <Text style={{ color: "#60A5FA", fontSize: 11, marginBottom: 4, fontWeight: "600" }}>Твои таланты</Text>
          {[10, 15, 20, 25].map(tier => {
            const t = playerTierMap[tier];
            return (
              <View key={tier} style={{ flexDirection: "row", alignItems: "center", marginBottom: 4 }}>
                <Text style={{ color: "#64748B", fontSize: 9, width: 20 }}>{tier}</Text>
                {t ? (
                  <>
                    {t.image ? <Image source={{ uri: t.image }} style={{ width: 18, height: 18, borderRadius: 3 }} /> : <View style={{ width: 18, height: 18, borderRadius: 3, backgroundColor: "#1E293B" }} />}
                    <Text style={{ color: "#CBD5E1", fontSize: 8, marginLeft: 4 }} numberOfLines={1}>{t.name}</Text>
                  </>
                ) : (
                  <Text style={{ color: "#475569", fontSize: 8, fontStyle: "italic", marginLeft: 22 }}>—</Text>
                )}
              </View>
            );
          })}
        </View>
      </View>
    </View>
  );
}
