import React, { useState } from "react";
import { 
  View, Text, TextInput, TouchableOpacity, 
  ScrollView, SafeAreaView, Platform 
} from "react-native";
import { router } from "expo-router";
import HeroMetaCardList from "@/components/HeroMetaCardList";
import { colors } from "@/lib/theme";

const HeroMeta = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAttributes, setSelectedAttributes] = useState<string[]>([]);
  const [selectedPositions, setSelectedPositions] = useState<number[]>([]);

  const attributes = [
    { id: "str", label: "Strength", icon: "💪" },
    { id: "agi", label: "Agility", icon: "⚡" },
    { id: "int", label: "Intelligence", icon: "🔮" },
  ];

  const positions = [1, 2, 3, 4, 5];

  const toggleFilter = (setter: React.Dispatch<React.SetStateAction<any[]>>, value: any) => {
    setter(prev => prev.includes(value) ? prev.filter(v => v !== value) : [...prev, value]);
  };

  const chipBase = { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 10, backgroundColor: colors.bgCard, borderWidth: 1, borderColor: colors.border };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <View style={{ flexDirection: "row", alignItems: "center", padding: 16, paddingTop: Platform.OS === "ios" ? 12 : 16 }}>
        <TouchableOpacity onPress={() => router.push("/")} style={{ marginRight: 12, padding: 4 }}>
          <Text style={{ color: colors.orange, fontSize: 20, fontWeight: "600" }}>←</Text>
        </TouchableOpacity>
        <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700" }}>Heroes</Text>
      </View>

      <ScrollView 
        contentContainerStyle={{ paddingBottom: 20 }}
        showsVerticalScrollIndicator={false}
      >
        <View style={{ flexDirection: "row", alignItems: "center", marginHorizontal: 16, marginBottom: 16, backgroundColor: colors.bgCard, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 12, borderWidth: 1, borderColor: colors.border }}>
          <Text style={{ fontSize: 18, marginRight: 10, opacity: 0.6 }}>🔍</Text>
          <TextInput
            placeholder="Search heroes..."
            placeholderTextColor={colors.text40}
            value={searchQuery}
            onChangeText={setSearchQuery}
            style={{ flex: 1, color: colors.text, fontSize: 15 }}
          />
        </View>

        <Text style={{ color: colors.text40, fontSize: 11, fontWeight: "600", letterSpacing: 0.8, marginHorizontal: 16, marginBottom: 8, marginTop: 4 }}>ATTRIBUTES</Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginHorizontal: 16, marginBottom: 16 }}>
          {attributes.map((attr) => {
            const attrColor = attr.id === "str" ? colors.red : attr.id === "agi" ? colors.orange : colors.blue;
            return (
            <TouchableOpacity
              key={attr.id}
              onPress={() => toggleFilter(setSelectedAttributes, attr.id)}
              style={[chipBase, selectedAttributes.includes(attr.id) && { backgroundColor: attr.id === "str" ? "rgba(239,68,68,0.12)" : attr.id === "agi" ? "rgba(249,115,22,0.12)" : "rgba(59,130,246,0.15)", borderColor: attrColor }]}
            >
              <Text style={[{ color: colors.text60, fontSize: 12, fontWeight: "600" }, selectedAttributes.includes(attr.id) && { color: attrColor }]}>
                {attr.icon} {attr.label}
              </Text>
            </TouchableOpacity>
            );
          })}
        </View>

        <Text style={{ color: colors.text40, fontSize: 11, fontWeight: "600", letterSpacing: 0.8, marginHorizontal: 16, marginBottom: 8, marginTop: 4 }}>POSITIONS</Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginHorizontal: 16, marginBottom: 16 }}>
          {positions.map((pos) => (
            <TouchableOpacity
              key={pos}
              onPress={() => toggleFilter(setSelectedPositions, pos)}
              style={[chipBase, selectedPositions.includes(pos) && { backgroundColor: "rgba(139,92,246,0.12)", borderColor: colors.purple }]}
            >
              <Text style={[{ color: colors.text60, fontSize: 12, fontWeight: "600" }, selectedPositions.includes(pos) && { color: colors.purple }]}>
                Pos {pos}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <HeroMetaCardList 
          searchQuery={searchQuery}
          selectedAttributes={selectedAttributes}
          selectedPositions={selectedPositions}
        />
      </ScrollView>
    </SafeAreaView>
  );
};

export default HeroMeta;
