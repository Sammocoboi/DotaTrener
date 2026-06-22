const MEDALS: [number, string][] = [
  [1, "Herald"], [2, "Guardian"], [3, "Crusader"],
  [4, "Archon"], [5, "Legend"], [6, "Ancient"], [7, "Divine"],
];

export function rankLabel(seasonRank: number): string {
  if (!seasonRank || seasonRank <= 0) return "Uncalibrated";
  if (seasonRank >= 80) return "Immortal";
  const medalId = Math.floor(seasonRank / 10);
  const star = seasonRank % 10;
  const name = MEDALS.find(([id]) => id === medalId)?.[1];
  if (!name) return "Unknown";
  return star >= 1 && star <= 5 ? `${name} ${star}` : name;
}

export function rankIconUrl(seasonRank: number): string {
  if (!seasonRank || seasonRank <= 0) return "";
  const medalId = Math.floor(seasonRank / 10);
  const star = seasonRank % 10;
  return `http://83.222.16.188/api/coaching/rank-icon/${medalId}/${star}/`;
}
