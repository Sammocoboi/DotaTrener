export type HeroMeta = {
  id: number;
  hero_id: number;
  hero_name: string;
  hero_image: string;
  hero_attr: string;
  patch_version: string;

  pick_rate: number | null;        
  win_rate: number | null;         
  ban_rate: number | null;        
  games_played: number | null;

  roles: Record<string, number>; 
  positions: number[];

  avg_kills: number | null;
  avg_deaths: number | null;
  avg_assists: number | null;
  avg_gpm: number | null;
  avg_xpm: number | null;
  avg_last_hits: number | null;
  avg_denies: number | null;
  avg_networth: number | null;
  avg_hero_damage: number | null;
  avg_tower_damage: number | null;
  avg_kda: number | null;
  avg_kill_participation: number | null;

  updated_at: string;
}