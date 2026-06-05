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
  selectedPositions: string[];
};

const HeroMetaCardList = ({ searchQuery, selectedAttributes, selectedPositions }: Props) => {
  const [heroes, setHeroes] = useState<HeroMeta[]>([]);
  const [filtered, setFiltered] = useState<HeroMeta[]>([]);

  useEffect(() => {
    const fetchHeroes = async () => {
      try {
        const res = await axios.get(API_URL);
        setHeroes(res.data.results || []);
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
      result = result.filter(h => {
        const roles = Object.keys(h.roles);
        return roles.some(r => selectedAttributes.some(a => r.toLowerCase().includes(a)));
      });
    }

    if (selectedPositions.length > 0) {
      result = result.filter(h => {
        const roles = Object.keys(h.roles);
        return roles.some(r => selectedPositions.some(p => r.toLowerCase().includes(p.replace("Pos ", ""))));
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