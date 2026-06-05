import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, Image } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { API_BASE as API } from "@/lib/api";


type ItemEntry = { id: number; name: string; image: string; time: number | null };
type SkillEntry = { id: number; name: string; image: string };
type Build = { build_type: string; sequence: (ItemEntry | SkillEntry)[]; win_rate: number; games: number; role?: string };
type TalentEntry = { abilityId: number; tier: number; slot: "left" | "right"; name: string; image: string; matchCount: number; win_rate: number; pick_rate: number };

type PlayerData = {
  steam_account_id: number;
  hero_id: number;
  hero_name: string;
  hero_image: string;
  is_radiant: boolean;
  is_me: boolean;
  nickname: string;
  avatar_url: string;
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

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function MatchDetailScreen() {
  const params = useLocalSearchParams<{ token: string; match_id: string }>();
  const token = params.token || getToken();
  const match_id = params.match_id;
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
        const me = res.data.players?.find((p: PlayerData) => p.is_me);
        if (me) {
          setExpandedHero(me.hero_id);
          loadBuilds(me.hero_id);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [match_id]);

  const loadBuilds = (heroId: number) => {
    if (heroBuilds[heroId]) return;
    axios.get(`${API}/hero/${heroId}/builds/`).then((r) => setHeroBuilds((prev) => ({ ...prev, [heroId]: r.data }))).catch(() => {});
  };

  if (loading) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg }}><Text style={{ color: colors.text60 }}>Загрузка...</Text></View>;
  if (!data) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg }}><Text style={{ color: colors.text60 }}>Матч не найден</Text></View>;

  const radiant = data.players.filter((p) => p.is_radiant).sort((a, b) => b.networth - a.networth);
  const dire = data.players.filter((p) => !p.is_radiant).sort((a, b) => b.networth - a.networth);

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }}>
      <View style={{
        backgroundColor: data.radiant_win ? "rgba(16,185,129,0.06)" : "rgba(239,68,68,0.06)",
        borderBottomWidth: 1, borderBottomColor: colors.border,
        padding: 16, paddingTop: 12,
      }}>
        <Pressable onPress={() => router.back()} style={{ marginBottom: 8 }}>
          <Text style={{ color: colors.orange, fontWeight: "600" }}>← Назад</Text>
        </Pressable>
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
          <Text style={{ color: colors.text, fontSize: 18, fontWeight: "800" }}>Противостояние</Text>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 10 }}>
            <View style={{ backgroundColor: colors.bgCard, borderWidth: 1, borderColor: colors.border, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 }}>
              <Text style={{ color: colors.text60, fontSize: 11, fontWeight: "600" }}>{formatDuration(data.duration)}</Text>
            </View>
            <Text style={{ color: colors.text40, fontSize: 9, letterSpacing: 0.5 }}>{new Date(data.start_time * 1000).toLocaleDateString("ru")}</Text>
          </View>
        </View>
      </View>

      <TeamBlock label="RADIANT" won={data.radiant_win} players={radiant} heroBuilds={heroBuilds} expandedHero={expandedHero} setExpandedHero={setExpandedHero} loadBuilds={loadBuilds} token={token} />
      <TeamBlock label="DIRE" won={!data.radiant_win} players={dire} heroBuilds={heroBuilds} expandedHero={expandedHero} setExpandedHero={setExpandedHero} loadBuilds={loadBuilds} token={token} />
    </ScrollView>
  );
}

function getPosition(networth: number, players: PlayerData[]): number {
  const sorted = [...players].sort((a, b) => b.networth - a.networth);
  return sorted.findIndex((p) => p.networth === networth) + 1;
}

const ROLE_ICONS: Record<number, string> = {
  1: "https://cdn.stratz.com/images/dota2/role/pos1.png",
  2: "https://cdn.stratz.com/images/dota2/role/pos2.png",
  3: "https://cdn.stratz.com/images/dota2/role/pos3.png",
  4: "https://cdn.stratz.com/images/dota2/role/pos4.png",
  5: "https://cdn.stratz.com/images/dota2/role/pos5.png",
};

function TeamBlock({ label, won, players, heroBuilds, expandedHero, setExpandedHero, loadBuilds, token }: {
  label: string; won: boolean; players: PlayerData[];
  heroBuilds: Record<number, HeroBuilds>; expandedHero: number | null; setExpandedHero: (id: number | null) => void; loadBuilds: (id: number) => void; token: string;
}) {
  const isRadiant = label === "RADIANT";
  const totalGPM = players.reduce((s, p) => s + p.gpm, 0);
  const totalXPM = players.reduce((s, p) => s + p.xpm, 0);

  return (
    <View style={{ marginHorizontal: 12, marginBottom: 16 }}>
      <View style={{
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "space-between",
        paddingHorizontal: 12,
        paddingVertical: 8,
        marginBottom: 8,
      }}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
          <Text style={{ color: isRadiant ? colors.green : colors.red, fontWeight: "800", fontSize: 16, letterSpacing: 0.5 }}>
            {isRadiant ? "Свет" : "Тьма"}
          </Text>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
            <Text style={{ color: colors.text60, fontSize: 11 }}>+{(totalXPM / 1000).toFixed(1)}тыс XP</Text>
            <View style={{ width: 4, height: 4, borderRadius: 2, backgroundColor: colors.text40 }} />
            <Text style={{ color: colors.text60, fontSize: 11 }}>+{(totalGPM / 1000).toFixed(1)}тыс</Text>
          </View>
        </View>
        <Text style={{ color: isRadiant ? colors.green : colors.red, fontSize: 11, fontWeight: "700", letterSpacing: 0.5 }}>
          {won ? "ПОБЕДА" : "ПОРАЖЕНИЕ"}
        </Text>
      </View>

      <View style={{ flexDirection: "row", gap: 4 }}>
        {players.map((p, i) => {
          const isExpanded = expandedHero === p.hero_id;
          const builds = heroBuilds[p.hero_id];
          const pos = getPosition(p.networth, players);

          return (
            <View key={i} style={{ flex: 1 }}>
              <Pressable
                onPress={() => { if (!isExpanded) loadBuilds(p.hero_id); setExpandedHero(isExpanded ? null : p.hero_id); }}
                style={{
                  borderRadius: 8,
                  overflow: "hidden",
                  borderWidth: p.is_me ? 2 : 1,
                  borderColor: p.is_me ? colors.orange : colors.borderSoft,
                  backgroundColor: colors.bgCard,
                }}
              >
                <View style={{ height: 120, position: "relative" }}>
                  {p.hero_image ? (
                    <Image source={{ uri: p.hero_image }} style={{ width: "100%", height: "100%" }} />
                  ) : (
                    <View style={{ flex: 1, backgroundColor: colors.bgElevated }} />
                  )}

                  <View style={{
                    position: "absolute",
                    bottom: 4,
                    left: 4,
                    backgroundColor: "rgba(0,0,0,0.7)",
                    paddingHorizontal: 3,
                    paddingVertical: 2,
                    borderRadius: 4,
                  }}>
                    <Image source={{ uri: ROLE_ICONS[pos] }} style={{ width: 16, height: 16 }} />
                  </View>
                </View>

                <View style={{ padding: 6 }}>
                  <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                    <Text style={{ color: colors.text, fontSize: 11, fontWeight: "700" }}>
                      {p.kills}/{p.deaths}/{p.assists}
                    </Text>
                    <View style={{ flexDirection: "row", alignItems: "center", gap: 2 }}>
                      <Image source={{ uri: "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/icons/gold.png" }} style={{ width: 10, height: 10 }} />
                      <Text style={{ color: colors.text, fontSize: 10 }}>{(p.networth / 1000).toFixed(1)}к</Text>
                    </View>
                  </View>

                  <Pressable
                    onPress={() => p.steam_account_id && router.push({ pathname: "/player", params: { steam_id: p.steam_account_id, token } })}
                    style={{ flexDirection: "row", alignItems: "center", gap: 4 }}
                  >
                    {p.avatar_url ? (
                      <Image source={{ uri: p.avatar_url }} style={{ width: 18, height: 18, borderRadius: 9 }} />
                    ) : (
                      <View style={{ width: 18, height: 18, borderRadius: 9, backgroundColor: colors.bgElevated }} />
                    )}
                    <Text style={{ color: colors.text80, fontSize: 9, flex: 1 }} numberOfLines={1}>
                      {p.nickname || `Hero ${p.hero_id}`}
                    </Text>
                  </Pressable>
                </View>
              </Pressable>

              {isExpanded && builds && (
                <View style={{ marginTop: 4 }}>
                  <HeroBuildsSection builds={builds} playerItems={p.items} playerAbilities={p.abilities} playerTalents={p.talents} />
                </View>
              )}
            </View>
          );
        })}
      </View>
    </View>
  );
}

function formatTime(mins: number): string {
  return `${mins} min`;
}

function formatTimePlayer(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
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
    if (!playerTierMap[tier]) playerTierMap[tier] = { id: pt.id, name: pt.name, image: pt.image };
    else if (tier === 0) playerTierMap[tier] = { id: pt.id, name: pt.name, image: pt.image };
  }

  return (
    <View style={{ backgroundColor: colors.bgRow, padding: 12, borderRadius: 8, borderWidth: 1, borderColor: colors.borderSoft }}>
      {topItem && (
        <View style={{ flexDirection: "row", gap: 12, marginBottom: 10 }}>
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.text60, fontSize: 10, marginBottom: 4, letterSpacing: 0.3 }}>Мета · {topItem.win_rate.toFixed(1)}% WR · {topItem.games} games</Text>
            <View style={{ flexDirection: "row", gap: 3, flexWrap: "wrap" }}>
              {(topItem.sequence as ItemEntry[]).map((item, j) => (
                <View key={j} style={{ alignItems: "center", width: 40 }}>
                  {item.image ? <Image source={{ uri: item.image }} style={{ width: 32, height: 32, borderRadius: 4 }} /> : <View style={{ width: 32, height: 32, borderRadius: 4, backgroundColor: colors.bgElevated }} />}
                  {item.time != null && item.time > 0 && <Text style={{ color: colors.orange, fontSize: 8, marginTop: 1 }}>{formatTime(item.time)}</Text>}
                </View>
              ))}
            </View>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.orange, fontSize: 10, marginBottom: 4, fontWeight: "600" }}>Твой билд</Text>
            <View style={{ flexDirection: "row", gap: 3, flexWrap: "wrap" }}>
              {(playerItems ?? []).map((item, j) => (
                <View key={j} style={{ alignItems: "center", width: 40 }}>
                  {item.image ? <Image source={{ uri: item.image }} style={{ width: 32, height: 32, borderRadius: 4 }} /> : <View style={{ width: 32, height: 32, borderRadius: 4, backgroundColor: colors.bgElevated }} />}
                  {item.time != null && item.time > 0 && <Text style={{ color: colors.orange, fontSize: 8, marginTop: 1 }}>{formatTimePlayer(item.time)}</Text>}
                </View>
              ))}
              {(playerItems ?? []).length === 0 && <Text style={{ color: colors.text40, fontSize: 10 }}>Нет данных</Text>}
            </View>
          </View>
        </View>
      )}
      <View style={{ flexDirection: "row", gap: 12 }}>
        {topSkill && (
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.text60, fontSize: 10, marginBottom: 4, letterSpacing: 0.3 }}>Мета скиллы · {topSkill.win_rate.toFixed(1)}% WR</Text>
            <View style={{ flexDirection: "row", gap: 2, flexWrap: "wrap" }}>
              {(topSkill.sequence as SkillEntry[]).map((skill, j) => (
                <View key={j} style={{ alignItems: "center", width: 28 }}>
                  <View style={{ position: "relative" }}>
                    {skill.image ? <Image source={{ uri: skill.image }} style={{ width: 26, height: 26, borderRadius: 3 }} /> : <View style={{ width: 26, height: 26, borderRadius: 3, backgroundColor: colors.bgElevated }} />}
                    <View style={{ position: "absolute", top: -3, right: -3, backgroundColor: colors.bg, borderRadius: 5, width: 12, height: 12, alignItems: "center", justifyContent: "center" }}>
                      <Text style={{ color: colors.orange, fontSize: 7, fontWeight: "700" }}>{j + 1}</Text>
                    </View>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}
        {(playerAbilities ?? []).length > 0 && (
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.orange, fontSize: 10, marginBottom: 4, fontWeight: "600" }}>Твои скиллы</Text>
            <View style={{ flexDirection: "row", gap: 3, flexWrap: "wrap" }}>
              {(playerAbilities ?? []).slice(0, 15).map((ab, j) => (
                <View key={j} style={{ alignItems: "center", width: 30 }}>
                  {ab.image ? <Image source={{ uri: ab.image }} style={{ width: 26, height: 26, borderRadius: 3 }} /> : <View style={{ width: 26, height: 26, borderRadius: 3, backgroundColor: colors.bgElevated }} />}
                </View>
              ))}
            </View>
          </View>
        )}
      </View>
      <View style={{ flexDirection: "row", gap: 12, marginTop: 8 }}>
        <View style={{ flex: 1 }}>
          <Text style={{ color: colors.text60, fontSize: 10, marginBottom: 4, letterSpacing: 0.3 }}>Мета таланты</Text>
          {[10, 15, 20, 25].map(tier => {
            const pair = talentsByTier[tier];
            if (!pair) return null;
            return (
              <View key={tier} style={{ flexDirection: "row", alignItems: "center", marginBottom: 3 }}>
                <Text style={{ color: colors.text40, fontSize: 8, width: 16 }}>{tier}</Text>
                <View style={{ flex: 1 }}>
                  {pair.left && (
                    <View style={{ flexDirection: "row", alignItems: "center", gap: 2 }}>
                      {pair.left.image ? <Image source={{ uri: pair.left.image }} style={{ width: 16, height: 16, borderRadius: 2 }} /> : <View style={{ width: 16, height: 16, borderRadius: 2, backgroundColor: colors.bgElevated }} />}
                      <Text style={{ color: colors.text80, fontSize: 7 }} numberOfLines={1}>{pair.left.name}</Text>
                      <Text style={{ color: colors.purpleLight, fontSize: 6 }}>{pair.left.pick_rate}% {pair.left.win_rate}%</Text>
                    </View>
                  )}
                  {pair.right && (
                    <View style={{ flexDirection: "row", alignItems: "center", gap: 2 }}>
                      {pair.right.image ? <Image source={{ uri: pair.right.image }} style={{ width: 16, height: 16, borderRadius: 2 }} /> : <View style={{ width: 16, height: 16, borderRadius: 2, backgroundColor: colors.bgElevated }} />}
                      <Text style={{ color: colors.text80, fontSize: 7 }} numberOfLines={1}>{pair.right.name}</Text>
                      <Text style={{ color: colors.purpleLight, fontSize: 6 }}>{pair.right.pick_rate}% {pair.right.win_rate}%</Text>
                    </View>
                  )}
                </View>
              </View>
            );
          })}
        </View>
        <View style={{ flex: 1 }}>
          <Text style={{ color: colors.orange, fontSize: 10, marginBottom: 4, fontWeight: "600" }}>Твои таланты</Text>
          {[10, 15, 20, 25].map(tier => {
            const t = playerTierMap[tier];
            return (
              <View key={tier} style={{ flexDirection: "row", alignItems: "center", marginBottom: 3 }}>
                <Text style={{ color: colors.text40, fontSize: 8, width: 16 }}>{tier}</Text>
                {t ? (
                  <View style={{ flexDirection: "row", alignItems: "center", gap: 2 }}>
                    {t.image ? <Image source={{ uri: t.image }} style={{ width: 16, height: 16, borderRadius: 2 }} /> : <View style={{ width: 16, height: 16, borderRadius: 2, backgroundColor: colors.bgElevated }} />}
                    <Text style={{ color: colors.text80, fontSize: 7 }} numberOfLines={1}>{t.name}</Text>
                  </View>
                ) : (
                  <Text style={{ color: colors.text40, fontSize: 7, fontStyle: "italic", marginLeft: 18 }}>—</Text>
                )}
              </View>
            );
          })}
        </View>
      </View>
    </View>
  );
}
