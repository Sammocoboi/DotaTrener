import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, Image, FlatList } from "react-native";
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

function formatTimePlayer(seconds: number): string {
  const m = Math.floor(seconds / 60);
  return `${m}:${String(Math.abs(seconds % 60)).padStart(2, "0")}`;
}

function formatDamage(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}к`;
  return String(n);
}

export default function MatchDetailScreen() {
  const params = useLocalSearchParams<{ token: string; match_id: string }>();
  const token = params.token || getToken() || "";
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
  const radiantByHeroDamage = [...radiant].sort((a, b) => b.hero_damage - a.hero_damage);
  const direByHeroDamage = [...dire].sort((a, b) => b.hero_damage - a.hero_damage);

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }}>
      <View style={{
        backgroundColor: data.radiant_win ? "rgba(16,185,129,0.06)" : "rgba(239,68,68,0.06)",
        borderBottomWidth: 1, borderBottomColor: colors.border,
        padding: 12, paddingTop: 10,
      }}>
        <Pressable onPress={() => router.back()} style={{ marginBottom: 6 }}>
          <Text style={{ color: colors.orange, fontWeight: "600", fontSize: 13 }}>← Назад</Text>
        </Pressable>
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
          <Text style={{ color: colors.text, fontSize: 17, fontWeight: "800" }}>Противостояние</Text>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
            <View style={{ backgroundColor: colors.bgCard, borderWidth: 1, borderColor: colors.border, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 }}>
              <Text style={{ color: colors.text60, fontSize: 10, fontWeight: "600" }}>{formatDuration(data.duration)}</Text>
            </View>
            <Text style={{ color: colors.text40, fontSize: 9 }}>{new Date(data.start_time * 1000).toLocaleDateString("ru")}</Text>
          </View>
        </View>
      </View>

      <TeamBlock label="RADIANT" won={data.radiant_win} players={radiant} heroBuilds={heroBuilds} expandedHero={expandedHero} setExpandedHero={setExpandedHero} loadBuilds={loadBuilds} token={token} />
      <TeamBlock label="DIRE" won={!data.radiant_win} players={dire} heroBuilds={heroBuilds} expandedHero={expandedHero} setExpandedHero={setExpandedHero} loadBuilds={loadBuilds} token={token} />

      <NetworthGraph radiant={radiant} dire={dire} />

      <DamageBar label="Урон по героям" icon="⚔" color1={colors.green} color2={colors.red} players1={radiantByHeroDamage} players2={direByHeroDamage} getValue={(p) => p.hero_damage} />

      <DamageBar label="Урон по вышкам" icon="🏰" color1={colors.green} color2={colors.red} players1={radiant.sort((a, b) => b.tower_damage - a.tower_damage)} players2={dire.sort((a, b) => b.tower_damage - a.tower_damage)} getValue={(p) => p.tower_damage} />

      <BuildsSection allPlayers={[...radiant, ...dire]} heroBuilds={heroBuilds} loadBuilds={loadBuilds} token={token} />
    </ScrollView>
  );
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
  const totalXPM = players.reduce((s, p) => s + p.xpm, 0);
  const totalGPM = players.reduce((s, p) => s + p.gpm, 0);

  return (
    <View style={{ marginHorizontal: 8, marginBottom: 12 }}>
      <View style={{
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "space-between",
        paddingHorizontal: 8,
        paddingVertical: 6,
        marginBottom: 6,
      }}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
          <Text style={{ color: isRadiant ? colors.green : colors.red, fontWeight: "800", fontSize: 15 }}>
            {isRadiant ? "Свет" : "Тьма"}
          </Text>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
            <Text style={{ color: colors.text60, fontSize: 10 }}>+{(totalXPM / 1000).toFixed(1)}тыс XP</Text>
            <View style={{ width: 3, height: 3, borderRadius: 1.5, backgroundColor: colors.text40 }} />
            <Text style={{ color: colors.text60, fontSize: 10 }}>+{(totalGPM / 1000).toFixed(1)}тыс</Text>
          </View>
        </View>
        <Text style={{ color: isRadiant ? colors.green : colors.red, fontSize: 10, fontWeight: "700", letterSpacing: 0.5 }}>
          {won ? "ПОБЕДА" : "ПОРАЖЕНИЕ"}
        </Text>
      </View>

      <FlatList
        data={players}
        horizontal={true}
        showsHorizontalScrollIndicator={false}
        keyExtractor={(item, i) => `${item.hero_id}-${i}`}
        contentContainerStyle={{ gap: 4 }}
        renderItem={({ item: p }) => {
          const isExpanded = expandedHero === p.hero_id;
          const builds = heroBuilds[p.hero_id];
          return (
            <View style={{ width: 140 }}>
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
                <View style={{ height: 80, position: "relative" }}>
                  {p.hero_image ? (
                    <Image source={{ uri: p.hero_image }} style={{ width: "100%", height: "100%" }} resizeMode="cover" />
                  ) : (
                    <View style={{ flex: 1, backgroundColor: colors.bgElevated }} />
                  )}
                  <View style={{
                    position: "absolute", bottom: 3, left: 3,
                    backgroundColor: "rgba(0,0,0,0.7)",
                    paddingHorizontal: 2, paddingVertical: 1, borderRadius: 3,
                  }}>
                    <Image source={{ uri: ROLE_ICONS[players.indexOf(p) + 1] }} style={{ width: 14, height: 14 }} />
                  </View>
                </View>

                <View style={{ padding: 5 }}>
                  <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 2 }}>
                    <Text style={{ color: colors.text, fontSize: 10, fontWeight: "700" }}>
                      {p.kills}/{p.deaths}/{p.assists}
                    </Text>
                    <View style={{ flexDirection: "row", alignItems: "center", gap: 2 }}>
                      <Image source={{ uri: "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/icons/gold.png" }} style={{ width: 9, height: 9 }} />
                      <Text style={{ color: colors.text, fontSize: 9 }}>{(p.networth / 1000).toFixed(1)}к</Text>
                    </View>
                  </View>
                  <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 3 }}>
                    <Text style={{ color: colors.red, fontSize: 9 }}>⚔ {formatDamage(p.hero_damage)}</Text>
                    <Text style={{ color: colors.text60, fontSize: 9 }}>🏰 {formatDamage(p.tower_damage)}</Text>
                  </View>
                  <Pressable
                    onPress={() => p.steam_account_id && router.push({ pathname: "/player", params: { steam_id: p.steam_account_id, token } })}
                    style={{ flexDirection: "row", alignItems: "center", gap: 3 }}
                  >
                    {p.avatar_url ? (
                      <Image source={{ uri: p.avatar_url }} style={{ width: 16, height: 16, borderRadius: 8 }} />
                    ) : (
                      <View style={{ width: 16, height: 16, borderRadius: 8, backgroundColor: colors.bgElevated }} />
                    )}
                    <Text style={{ color: colors.text80, fontSize: 8, flex: 1 }} numberOfLines={1}>
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
        }}
      />
    </View>
  );
}

function NetworthGraph({ radiant, dire }: { radiant: PlayerData[]; dire: PlayerData[] }) {
  const rTotal = radiant.reduce((s, p) => s + p.networth, 0);
  const dTotal = dire.reduce((s, p) => s + p.networth, 0);
  const max = Math.max(rTotal, dTotal, 1);
  const rPct = (rTotal / max) * 100;
  const dPct = (dTotal / max) * 100;
  const advantage = rTotal - dTotal;
  const winner = advantage > 0 ? "radiant" : advantage < 0 ? "dire" : null;

  return (
    <View style={{ marginHorizontal: 8, marginBottom: 16 }}>
      <Text style={{ color: colors.text, fontSize: 14, fontWeight: "700", marginBottom: 8 }}>Нетворс</Text>
      <View style={{ backgroundColor: colors.bgCard, borderRadius: 10, padding: 12, borderWidth: 1, borderColor: colors.borderSoft }}>
        <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
            <View style={{ width: 10, height: 10, borderRadius: 2, backgroundColor: colors.green }} />
            <Text style={{ color: colors.text, fontSize: 11, fontWeight: "600" }}>Свет</Text>
          </View>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: winner === "radiant" ? colors.green : winner === "dire" ? colors.red : colors.text60, fontSize: 10, fontWeight: "700" }}>
              {advantage > 0 ? "+" : ""}{formatDamage(Math.abs(advantage))} {advantage > 0 ? "Свет" : advantage < 0 ? "Тьма" : ""}
            </Text>
          </View>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Text style={{ color: colors.text, fontSize: 11, fontWeight: "600" }}>Тьма</Text>
            <View style={{ width: 10, height: 10, borderRadius: 2, backgroundColor: colors.red }} />
          </View>
        </View>

        <View style={{ height: 8, flexDirection: "row", borderRadius: 4, overflow: "hidden", marginBottom: 4 }}>
          <View style={{ width: `${rPct}%`, backgroundColor: colors.green, borderTopLeftRadius: 4, borderBottomLeftRadius: 4 }} />
          <View style={{ width: `${dPct}%`, backgroundColor: colors.red, borderTopRightRadius: 4, borderBottomRightRadius: 4 }} />
        </View>

        <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
          <Text style={{ color: colors.green, fontSize: 10, fontWeight: "600" }}>{formatDamage(rTotal)}</Text>
          <Text style={{ color: colors.red, fontSize: 10, fontWeight: "600" }}>{formatDamage(dTotal)}</Text>
        </View>

        <View style={{ flexDirection: "row", marginTop: 8, gap: 8 }}>
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.text60, fontSize: 9, marginBottom: 4 }}>Свет</Text>
            {radiant.map((p, i) => {
              const pct = (p.networth / max) * 100;
              return (
                <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: 4, marginBottom: 3 }}>
                  <View style={{ width: 22, height: 22, borderRadius: 4, overflow: "hidden" }}>
                    {p.hero_image ? <Image source={{ uri: p.hero_image }} style={{ width: 22, height: 22 }} /> : <View style={{ width: 22, height: 22, backgroundColor: colors.bgElevated }} />}
                  </View>
                  <View style={{ flex: 1, height: 6, backgroundColor: colors.bgElevated, borderRadius: 3, overflow: "hidden" }}>
                    <View style={{ width: `${pct}%`, height: "100%", backgroundColor: colors.green, borderRadius: 3 }} />
                  </View>
                  <Text style={{ color: colors.text60, fontSize: 8, width: 36, textAlign: "right" }}>{(p.networth / 1000).toFixed(1)}к</Text>
                </View>
              );
            })}
          </View>
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.text60, fontSize: 9, marginBottom: 4, textAlign: "right" }}>Тьма</Text>
            {dire.map((p, i) => {
              const pct = (p.networth / max) * 100;
              return (
                <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: 4, marginBottom: 3 }}>
                  <Text style={{ color: colors.text60, fontSize: 8, width: 36 }}>{(p.networth / 1000).toFixed(1)}к</Text>
                  <View style={{ flex: 1, height: 6, backgroundColor: colors.bgElevated, borderRadius: 3, overflow: "hidden" }}>
                    <View style={{ width: `${pct}%`, height: "100%", backgroundColor: colors.red, borderRadius: 3 }} />
                  </View>
                  <View style={{ width: 22, height: 22, borderRadius: 4, overflow: "hidden" }}>
                    {p.hero_image ? <Image source={{ uri: p.hero_image }} style={{ width: 22, height: 22 }} /> : <View style={{ width: 22, height: 22, backgroundColor: colors.bgElevated }} />}
                  </View>
                </View>
              );
            })}
          </View>
        </View>
      </View>
    </View>
  );
}

function DamageBar({ label, icon, color1, color2, players1, players2, getValue }: {
  label: string; icon: string; color1: string; color2: string;
  players1: PlayerData[]; players2: PlayerData[];
  getValue: (p: PlayerData) => number;
}) {
  const max = Math.max(...players1.map(getValue), ...players2.map(getValue), 1);

  return (
    <View style={{ marginHorizontal: 8, marginBottom: 16 }}>
      <Text style={{ color: colors.text, fontSize: 14, fontWeight: "700", marginBottom: 8 }}>{icon} {label}</Text>
      <View style={{ backgroundColor: colors.bgCard, borderRadius: 10, padding: 12, borderWidth: 1, borderColor: colors.borderSoft }}>
        <View style={{ flexDirection: "row", gap: 8 }}>
          <View style={{ flex: 1 }}>
            {players1.map((p, i) => {
              const val = getValue(p);
              const pct = (val / max) * 100;
              return (
                <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: 4, marginBottom: 3 }}>
                  <View style={{ width: 22, height: 22, borderRadius: 4, overflow: "hidden" }}>
                    {p.hero_image ? <Image source={{ uri: p.hero_image }} style={{ width: 22, height: 22 }} /> : <View style={{ width: 22, height: 22, backgroundColor: colors.bgElevated }} />}
                  </View>
                  <View style={{ flex: 1, height: 6, backgroundColor: colors.bgElevated, borderRadius: 3, overflow: "hidden" }}>
                    <View style={{ width: `${pct}%`, height: "100%", backgroundColor: color1, borderRadius: 3 }} />
                  </View>
                  <Text style={{ color: colors.text60, fontSize: 8, width: 40, textAlign: "right" }}>{formatDamage(val)}</Text>
                </View>
              );
            })}
          </View>
          <View style={{ flex: 1 }}>
            {players2.map((p, i) => {
              const val = getValue(p);
              const pct = (val / max) * 100;
              return (
                <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: 4, marginBottom: 3 }}>
                  <Text style={{ color: colors.text60, fontSize: 8, width: 40 }}>{formatDamage(val)}</Text>
                  <View style={{ flex: 1, height: 6, backgroundColor: colors.bgElevated, borderRadius: 3, overflow: "hidden" }}>
                    <View style={{ width: `${pct}%`, height: "100%", backgroundColor: color2, borderRadius: 3 }} />
                  </View>
                  <View style={{ width: 22, height: 22, borderRadius: 4, overflow: "hidden" }}>
                    {p.hero_image ? <Image source={{ uri: p.hero_image }} style={{ width: 22, height: 22 }} /> : <View style={{ width: 22, height: 22, backgroundColor: colors.bgElevated }} />}
                  </View>
                </View>
              );
            })}
          </View>
        </View>
      </View>
    </View>
  );
}

function getSkillOrder(abilities: { id: number; name: string; image: string; level: number; time: number | null }[]): string {
  const nonTalents = abilities.filter(a => a.time != null && a.time >= 0);
  if (nonTalents.length === 0) return "";
  const groups: Record<number, number> = {};
  for (const a of nonTalents) {
    groups[a.id] = (groups[a.id] || 0) + 1;
  }
  const sorted = Object.entries(groups).sort((a, b) => b[1] - a[1]);
  return sorted.map(([_, count]) => count).join("-");
}

function BuildsSection({ allPlayers, heroBuilds, loadBuilds, token }: {
  allPlayers: PlayerData[]; heroBuilds: Record<number, HeroBuilds>; loadBuilds: (id: number) => void; token: string;
}) {
  useEffect(() => {
    allPlayers.forEach(p => loadBuilds(p.hero_id));
  }, []);

  const radiant = allPlayers.filter(p => p.is_radiant);
  const dire = allPlayers.filter(p => !p.is_radiant);

  return (
    <View style={{ marginHorizontal: 8, marginBottom: 24 }}>
      <Text style={{ color: colors.text, fontSize: 14, fontWeight: "700", marginBottom: 8 }}>Сборки</Text>

      <View style={{ flexDirection: "row", gap: 8 }}>
        <View style={{ flex: 1 }}>
          {radiant.map((p, i) => (
            <PlayerBuildCard key={i} player={p} builds={heroBuilds[p.hero_id]} token={token} />
          ))}
        </View>
        <View style={{ flex: 1 }}>
          {dire.map((p, i) => (
            <PlayerBuildCard key={i} player={p} builds={heroBuilds[p.hero_id]} token={token} />
          ))}
        </View>
      </View>
    </View>
  );
}

function PlayerBuildCard({ player, builds, token }: { player: PlayerData; builds?: HeroBuilds; token: string }) {
  const skillOrder = getSkillOrder(player.abilities);
  const itemsWithTime = player.items.filter(it => it.time != null && it.time >= 0).sort((a, b) => (a.time || 0) - (b.time || 0));

  return (
    <View style={{ backgroundColor: colors.bgCard, borderRadius: 8, borderWidth: 1, borderColor: colors.borderSoft, padding: 8, marginBottom: 6 }}>
      <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 6 }}>
        <View style={{ width: 32, height: 32, borderRadius: 6, overflow: "hidden" }}>
          {player.hero_image ? <Image source={{ uri: player.hero_image }} style={{ width: 32, height: 32 }} /> : <View style={{ width: 32, height: 32, backgroundColor: colors.bgElevated }} />}
        </View>
        <View style={{ flex: 1 }}>
          <Pressable onPress={() => player.steam_account_id && router.push({ pathname: "/player", params: { steam_id: player.steam_account_id, token } })}>
            <Text style={{ color: colors.text, fontSize: 10, fontWeight: "600" }} numberOfLines={1}>{player.nickname || player.hero_name}</Text>
          </Pressable>
          {skillOrder ? <Text style={{ color: colors.text60, fontSize: 9 }}>{skillOrder} прокачка</Text> : null}
        </View>
      </View>

      <View style={{ flexDirection: "row", gap: 2, flexWrap: "wrap", marginBottom: 6 }}>
        {player.abilities.filter(a => a.time != null && a.time >= 0).slice(0, 18).map((ab, j) => (
          <View key={j} style={{ width: 22, height: 22 }}>
            {ab.image ? <Image source={{ uri: ab.image }} style={{ width: 22, height: 22, borderRadius: 3 }} /> : <View style={{ width: 22, height: 22, borderRadius: 3, backgroundColor: colors.bgElevated }} />}
          </View>
        ))}
      </View>

      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 2 }}>
        {itemsWithTime.map((item, j) => (
          <View key={j} style={{ alignItems: "center", width: 30 }}>
            {item.image ? <Image source={{ uri: item.image }} style={{ width: 24, height: 24, borderRadius: 3 }} /> : <View style={{ width: 24, height: 24, borderRadius: 3, backgroundColor: colors.bgElevated }} />}
            <Text style={{ color: colors.text40, fontSize: 7 }}>{formatTimePlayer(item.time!)}</Text>
          </View>
        ))}
      </View>

      {builds?.skill_builds?.[0] && (
        <View style={{ flexDirection: "row", gap: 2, flexWrap: "wrap", marginTop: 4, paddingTop: 4, borderTopWidth: 1, borderTopColor: colors.borderSoft }}>
          {(builds.skill_builds[0].sequence as SkillEntry[]).slice(0, 10).map((sk, j) => (
            <View key={j} style={{ width: 20, height: 20 }}>
              {sk.image ? <Image source={{ uri: sk.image }} style={{ width: 20, height: 20, borderRadius: 2 }} /> : <View style={{ width: 20, height: 20, borderRadius: 2, backgroundColor: colors.bgElevated }} />}
            </View>
          ))}
        </View>
      )}
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
    if (!playerTierMap[tier]) playerTierMap[tier] = { id: pt.id, name: pt.name, image: pt.image };
    else if (tier === 0) playerTierMap[tier] = { id: pt.id, name: pt.name, image: pt.image };
  }

  return (
    <View style={{ backgroundColor: colors.bgRow, padding: 8, borderRadius: 8, borderWidth: 1, borderColor: colors.borderSoft }}>
      {topItem && (
        <View style={{ flexDirection: "row", gap: 8, marginBottom: 8 }}>
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.text60, fontSize: 9, marginBottom: 3, letterSpacing: 0.3 }}>Мета · {topItem.win_rate.toFixed(1)}% WR · {topItem.games} games</Text>
            <View style={{ flexDirection: "row", gap: 2, flexWrap: "wrap" }}>
              {(topItem.sequence as ItemEntry[]).slice(0, 9).map((item, j) => (
                <View key={j} style={{ alignItems: "center", width: 32 }}>
                  {item.image ? <Image source={{ uri: item.image }} style={{ width: 26, height: 26, borderRadius: 3 }} /> : <View style={{ width: 26, height: 26, borderRadius: 3, backgroundColor: colors.bgElevated }} />}
                  {item.time != null && item.time > 0 && <Text style={{ color: colors.orange, fontSize: 7, marginTop: 1 }}>{formatTimePlayer(item.time)}</Text>}
                </View>
              ))}
            </View>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.orange, fontSize: 9, marginBottom: 3, fontWeight: "600" }}>Твой билд</Text>
            <View style={{ flexDirection: "row", gap: 2, flexWrap: "wrap" }}>
              {(playerItems ?? []).map((item, j) => (
                <View key={j} style={{ alignItems: "center", width: 32 }}>
                  {item.image ? <Image source={{ uri: item.image }} style={{ width: 26, height: 26, borderRadius: 3 }} /> : <View style={{ width: 26, height: 26, borderRadius: 3, backgroundColor: colors.bgElevated }} />}
                  {item.time != null && item.time > 0 && <Text style={{ color: colors.orange, fontSize: 7, marginTop: 1 }}>{formatTimePlayer(item.time)}</Text>}
                </View>
              ))}
              {(playerItems ?? []).length === 0 && <Text style={{ color: colors.text40, fontSize: 9 }}>Нет данных</Text>}
            </View>
          </View>
        </View>
      )}
      <View style={{ flexDirection: "row", gap: 8 }}>
        {topSkill && (
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.text60, fontSize: 9, marginBottom: 3, letterSpacing: 0.3 }}>Мета скиллы · {topSkill.win_rate.toFixed(1)}% WR</Text>
            <View style={{ flexDirection: "row", gap: 2, flexWrap: "wrap" }}>
              {(topSkill.sequence as SkillEntry[]).map((skill, j) => (
                <View key={j} style={{ alignItems: "center", width: 24 }}>
                  <View style={{ position: "relative" }}>
                    {skill.image ? <Image source={{ uri: skill.image }} style={{ width: 22, height: 22, borderRadius: 3 }} /> : <View style={{ width: 22, height: 22, borderRadius: 3, backgroundColor: colors.bgElevated }} />}
                    <View style={{ position: "absolute", top: -2, right: -2, backgroundColor: colors.bg, borderRadius: 5, width: 10, height: 10, alignItems: "center", justifyContent: "center" }}>
                      <Text style={{ color: colors.orange, fontSize: 6, fontWeight: "700" }}>{j + 1}</Text>
                    </View>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}
        {(playerAbilities ?? []).length > 0 && (
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.orange, fontSize: 9, marginBottom: 3, fontWeight: "600" }}>Твои скиллы</Text>
            <View style={{ flexDirection: "row", gap: 2, flexWrap: "wrap" }}>
              {(playerAbilities ?? []).slice(0, 15).map((ab, j) => (
                <View key={j} style={{ alignItems: "center", width: 24 }}>
                  {ab.image ? <Image source={{ uri: ab.image }} style={{ width: 22, height: 22, borderRadius: 3 }} /> : <View style={{ width: 22, height: 22, borderRadius: 3, backgroundColor: colors.bgElevated }} />}
                </View>
              ))}
            </View>
          </View>
        )}
      </View>
      <View style={{ flexDirection: "row", gap: 8, marginTop: 6 }}>
        <View style={{ flex: 1 }}>
          <Text style={{ color: colors.text60, fontSize: 9, marginBottom: 3, letterSpacing: 0.3 }}>Мета таланты</Text>
          {[10, 15, 20, 25].map(tier => {
            const pair = talentsByTier[tier];
            if (!pair) return null;
            return (
              <View key={tier} style={{ flexDirection: "row", alignItems: "center", marginBottom: 2 }}>
                <Text style={{ color: colors.text40, fontSize: 7, width: 14 }}>{tier}</Text>
                <View style={{ flex: 1 }}>
                  {pair.left && (
                    <View style={{ flexDirection: "row", alignItems: "center", gap: 2 }}>
                      {pair.left.image ? <Image source={{ uri: pair.left.image }} style={{ width: 14, height: 14, borderRadius: 2 }} /> : <View style={{ width: 14, height: 14, borderRadius: 2, backgroundColor: colors.bgElevated }} />}
                      <Text style={{ color: colors.text80, fontSize: 6 }} numberOfLines={1}>{pair.left.name}</Text>
                      <Text style={{ color: colors.purpleLight, fontSize: 5 }}>{pair.left.pick_rate}% {pair.left.win_rate}%</Text>
                    </View>
                  )}
                  {pair.right && (
                    <View style={{ flexDirection: "row", alignItems: "center", gap: 2 }}>
                      {pair.right.image ? <Image source={{ uri: pair.right.image }} style={{ width: 14, height: 14, borderRadius: 2 }} /> : <View style={{ width: 14, height: 14, borderRadius: 2, backgroundColor: colors.bgElevated }} />}
                      <Text style={{ color: colors.text80, fontSize: 6 }} numberOfLines={1}>{pair.right.name}</Text>
                      <Text style={{ color: colors.purpleLight, fontSize: 5 }}>{pair.right.pick_rate}% {pair.right.win_rate}%</Text>
                    </View>
                  )}
                </View>
              </View>
            );
          })}
        </View>
        <View style={{ flex: 1 }}>
          <Text style={{ color: colors.orange, fontSize: 9, marginBottom: 3, fontWeight: "600" }}>Твои таланты</Text>
          {[10, 15, 20, 25].map(tier => {
            const t = playerTierMap[tier];
            return (
              <View key={tier} style={{ flexDirection: "row", alignItems: "center", marginBottom: 2 }}>
                <Text style={{ color: colors.text40, fontSize: 7, width: 14 }}>{tier}</Text>
                {t ? (
                  <View style={{ flexDirection: "row", alignItems: "center", gap: 2 }}>
                    {t.image ? <Image source={{ uri: t.image }} style={{ width: 14, height: 14, borderRadius: 2 }} /> : <View style={{ width: 14, height: 14, borderRadius: 2, backgroundColor: colors.bgElevated }} />}
                    <Text style={{ color: colors.text80, fontSize: 6 }} numberOfLines={1}>{t.name}</Text>
                  </View>
                ) : (
                  <Text style={{ color: colors.text40, fontSize: 6, fontStyle: "italic", marginLeft: 16 }}>—</Text>
                )}
              </View>
            );
          })}
        </View>
      </View>
    </View>
  );
}
