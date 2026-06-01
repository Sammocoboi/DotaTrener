export type Match = {
  match_id: string;
  hero: string;
  result: "win" | "loss";
  side: string;
  duration: number;
  kda: string;
  gpm: number;
  xpm: number;
  created: boolean;
};