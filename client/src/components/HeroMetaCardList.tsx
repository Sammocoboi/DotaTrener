import React, { useEffect, useState } from "react";
import { View, Text, FlatList, StyleSheet } from "react-native";
import { router } from "expo-router";
import axios from "axios";
import { HeroMeta } from "@/types/herometa";
import { API_STRATZ_META as API_URL } from "@/lib/api";
import HeroMetaCard from "./HeroMetaCard";

type Props = {
  searchQuery: string;
  selectedAttributes: string[];
  selectedPositions: number[];
};

const HeroMetaCardList = ({ searchQuery, selectedAttributes, selectedPositions }: Props) => {
  const [heroes, setHeroes] = useState<HeroMeta[]>([]);
  const [filtered, setFiltered] = useState<HeroMeta[]>([]);

  useEffect(() => {
    const fetchHeroes = async () => {
      try {
        const res = await axios.get(API_URL);
        const raw: HeroMeta[] = res.data.results || [];
        const sanitized = raw.map(h => ({
          ...h,
          roles: h.roles ?? {},
          pick_rate: Number(h.pick_rate) || 0,
          win_rate: Number(h.win_rate) || 0,
          ban_rate: Number(h.ban_rate) || 0,
          games_played: Number(h.games_played) || 0,
          avg_kills: Number(h.avg_kills) || 0,
          avg_deaths: Number(h.avg_deaths) || 0,
          avg_assists: Number(h.avg_assists) || 0,
          avg_gpm: Number(h.avg_gpm) || 0,
          avg_xpm: Number(h.avg_xpm) || 0,
          avg_last_hits: Number(h.avg_last_hits) || 0,
          avg_denies: Number(h.avg_denies) || 0,
          avg_networth: Number(h.avg_networth) || 0,
          avg_hero_damage: Number(h.avg_hero_damage) || 0,
          avg_tower_damage: Number(h.avg_tower_damage) || 0,
          avg_kda: Number(h.avg_kda) || 0,
          avg_kill_participation: Number(h.avg_kill_participation) || 0,
        }));
        setHeroes(sanitized);
      } catch (err) {
        console.error("Failed to fetch heroes:", err);
      }
    };
    fetchHeroes();
  }, []);

  useEffect(() => {
    let result = heroes;

    if (searchQuery) {
      result = result.filter(h => h.hero_name.toLowerCase().includes(searchQuery.toLowerCase()));
    }

    if (selectedAttributes.length > 0) {
      result = result.filter(h => selectedAttributes.includes(h.hero_attr));
    }

    if (selectedPositions.length > 0) {
      result = result.filter(h => {
        const heroPositions = h.positions || [];
        return selectedPositions.some(p => heroPositions.includes(p));
      });
    }

    setFiltered(result);
  }, [searchQuery, selectedAttributes, selectedPositions, heroes]);

  if (filtered.length === 0) {
    return (
      <View style={styles.emptyState}>
        <Text style={styles.emptyIcon}>🔍</Text>
        <Text style={styles.emptyText}>No heroes found</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={filtered}
      keyExtractor={(item) => item.id.toString()}
      renderItem={({ item }) => (
        <HeroMetaCard
          herometa={item}
          onPress={() => router.push({ pathname: "heroes/HeroDetail" as any, params: { hero_id: item.hero } })}
        />
      )}
      contentContainerStyle={styles.listPadding}
      scrollEnabled={false}
    />
  );
};

const styles = StyleSheet.create({
  listPadding: { paddingHorizontal: 16, paddingBottom: 20 },
  emptyState: { alignItems: "center", justifyContent: "center", paddingVertical: 40 },
  emptyIcon: { fontSize: 36, opacity: 0.3, marginBottom: 8 },
  emptyText: { color: "#64748B", fontSize: 14 },
});

export default HeroMetaCardList;