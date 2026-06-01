import React from "react";
import { View, Text, Image, StyleSheet, Pressable } from "react-native";
import { HeroMeta } from "@/types/herometa";

type Props = {
  herometa: HeroMeta;
  onPress?: () => void;
};

const HeroMetaCard = ({ herometa, onPress }: Props) => {
  const winPercent = herometa.win_rate.toFixed(1);
  const pickPercent = herometa.pick_rate.toFixed(1);
  const banPercent = herometa.ban_rate.toFixed(1);

  return (
    <Pressable onPress={onPress} style={styles.card}>
      <View style={styles.header}>
        {herometa.hero_image ? (
          <Image source={{ uri: herometa.hero_image }} style={styles.heroImage} />
        ) : null}
        <View style={styles.headerText}>
          <Text style={styles.name}>{herometa.hero_name}</Text>
          <Text style={styles.patch}>Patch {herometa.patch_version}</Text>
        </View>
      </View>

      <View style={styles.statsRow}>
        <StatBadge label="Win" value={`${winPercent}%`} color="#22C55E" />
        <StatBadge label="Pick" value={`${pickPercent}%`} color="#3B82F6" />
        <StatBadge label="Ban" value={`${banPercent}%`} color="#EF4444" />
        <StatBadge label="Games" value={`${herometa.games_played}`} color="#A78BFA" />
      </View>

      <View style={styles.avgRow}>
        <Text style={styles.avgLabel}>K/D/A</Text>
        <Text style={styles.avgValue}>
          {herometa.avg_kills.toFixed(1)} / {herometa.avg_deaths.toFixed(1)} / {herometa.avg_assists.toFixed(1)}
        </Text>
      </View>

      <View style={styles.avgRow}>
        <Text style={styles.avgLabel}>GPM / XPM</Text>
        <Text style={styles.avgValue}>
          {Math.round(herometa.avg_gpm)} / {Math.round(herometa.avg_xpm)}
        </Text>
      </View>

      <View style={styles.avgRow}>
        <Text style={styles.avgLabel}>KDA</Text>
        <Text style={styles.avgValue}>{herometa.avg_kda.toFixed(2)}</Text>
      </View>

      {herometa.roles && Object.keys(herometa.roles).length > 0 && (
        <View style={styles.rolesRow}>
          {Object.entries(herometa.roles).map(([role, value]) => (
            <View key={role} style={styles.roleBadge}>
              <Text style={styles.roleText}>{role}</Text>
              <Text style={styles.roleValue}>{value.toFixed(1)}%</Text>
            </View>
          ))}
        </View>
      )}
    </Pressable>
  );
};

const StatBadge = ({ label, value, color }: { label: string; value: string; color: string }) => (
  <View style={styles.statBadge}>
    <Text style={[styles.statValue, { color }]}>{value}</Text>
    <Text style={styles.statLabel}>{label}</Text>
  </View>
);

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#131B31",
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.06)",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
    gap: 12,
  },
  heroImage: {
    width: 48,
    height: 48,
    borderRadius: 8,
  },
  headerText: {
    flex: 1,
  },
  name: {
    color: "#FFFFFF",
    fontSize: 17,
    fontWeight: "700",
  },
  patch: {
    color: "#64748B",
    fontSize: 12,
  },
  statsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 12,
  },
  statBadge: {
    alignItems: "center",
    flex: 1,
  },
  statValue: {
    fontSize: 15,
    fontWeight: "700",
  },
  statLabel: {
    color: "#64748B",
    fontSize: 11,
    marginTop: 2,
  },
  avgRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 4,
    borderTopWidth: 1,
    borderTopColor: "rgba(255,255,255,0.04)",
  },
  avgLabel: {
    color: "#94A3B8",
    fontSize: 13,
  },
  avgValue: {
    color: "#CBD5E1",
    fontSize: 13,
    fontWeight: "600",
  },
  rolesRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginTop: 10,
  },
  roleBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(59,130,246,0.1)",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  roleText: {
    color: "#94A3B8",
    fontSize: 11,
    marginRight: 4,
  },
  roleValue: {
    color: "#60A5FA",
    fontSize: 11,
    fontWeight: "600",
  },
});

export default HeroMetaCard;
