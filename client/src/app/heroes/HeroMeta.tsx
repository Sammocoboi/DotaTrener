import React, { useState } from "react";
import { 
  View, Text, TextInput, TouchableOpacity, 
  ScrollView, SafeAreaView, StyleSheet, Platform 
} from "react-native";
import { router } from "expo-router";
import HeroMetaCardList from "@/components/HeroMetaCardList";

const HeroMeta = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAttributes, setSelectedAttributes] = useState<string[]>([]);
  const [selectedPositions, setSelectedPositions] = useState<string[]>([]);

  const attributes = [
    { id: "strength", label: "Strength", icon: "💪" },
    { id: "agility", label: "Agility", icon: "⚡" },
    { id: "intelligence", label: "Intelligence", icon: "🔮" },
  ];

  const positions = ["Pos 1", "Pos 2", "Pos 3", "Pos 4", "Pos 5"];

  const toggleFilter = (setter: React.Dispatch<React.SetStateAction<string[]>>, value: string) => {
    setter(prev => prev.includes(value) ? prev.filter(v => v !== value) : [...prev, value]);
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backText}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Heroes</Text>
      </View>

      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            placeholder="Search heroes..."
            placeholderTextColor="#64748B"
            value={searchQuery}
            onChangeText={setSearchQuery}
            style={styles.searchInput}
          />
        </View>

        {/* Attributes Filter */}
        <Text style={styles.sectionLabel}>ATTRIBUTES</Text>
        <View style={styles.filterRow}>
          {attributes.map((attr) => (
            <TouchableOpacity
              key={attr.id}
              onPress={() => toggleFilter(setSelectedAttributes, attr.id)}
              style={[
                styles.chip,
                selectedAttributes.includes(attr.id) && styles.chipActive
              ]}
            >
              <Text style={[styles.chipText, selectedAttributes.includes(attr.id) && styles.chipTextActive]}>
                {attr.icon} {attr.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Positions Filter */}
        <Text style={styles.sectionLabel}>POSITIONS</Text>
        <View style={styles.filterRow}>
          {positions.map((pos) => (
            <TouchableOpacity
              key={pos}
              onPress={() => toggleFilter(setSelectedPositions, pos)}
              style={[
                styles.chip,
                selectedPositions.includes(pos) && styles.chipActive
              ]}
            >
              <Text style={[styles.chipText, selectedPositions.includes(pos) && styles.chipTextActive]}>
                {pos}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Hero List */}
        <HeroMetaCardList 
          searchQuery={searchQuery}
          selectedAttributes={selectedAttributes}
          selectedPositions={selectedPositions}
        />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0B1120" },
  header: { flexDirection: "row", alignItems: "center", padding: 16, paddingTop: Platform.OS === "ios" ? 12 : 16 },
  backBtn: { marginRight: 12, padding: 4 },
  backText: { color: "#60A5FA", fontSize: 20, fontWeight: "600" },
  headerTitle: { color: "#FFFFFF", fontSize: 20, fontWeight: "700" },
  scrollContent: { paddingBottom: 20 },
  searchContainer: {
    flexDirection: "row", alignItems: "center", marginHorizontal: 16, marginBottom: 16,
    backgroundColor: "#131B31", borderRadius: 12, paddingHorizontal: 14, paddingVertical: 12,
    borderWidth: 1, borderColor: "rgba(255,255,255,0.08)"
  },
  searchIcon: { fontSize: 18, marginRight: 10, opacity: 0.6 },
  searchInput: { flex: 1, color: "#FFFFFF", fontSize: 15 },
  sectionLabel: { color: "#64748B", fontSize: 11, fontWeight: "600", letterSpacing: 0.8, marginHorizontal: 16, marginBottom: 8, marginTop: 4 },
  filterRow: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginHorizontal: 16, marginBottom: 16 },
  chip: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 10, backgroundColor: "#131B31", borderWidth: 1, borderColor: "rgba(255,255,255,0.08)" },
  chipActive: { backgroundColor: "rgba(59,130,246,0.15)", borderColor: "#3B82F6" },
  chipText: { color: "#94A3B8", fontSize: 12, fontWeight: "600" },
  chipTextActive: { color: "#60A5FA" },
});

export default HeroMeta;