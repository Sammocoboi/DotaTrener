export type HeroMeta = {
  id: number;
  hero_id: number;
  hero_name: string;
  hero_image: string;
  patch_version: string;

  pick_rate: number;        
  win_rate: number;         
  ban_rate: number;        
  games_played: number;

  roles: Record<string, number>; 

  avg_kills: number ;
  avg_deaths: number ;
  avg_assists: number ;
  avg_gpm: number;
  avg_xpm: number ;
  avg_last_hits: number ;
  avg_denies: number ;
  avg_networth: number ;
  avg_hero_damage: number ;
  avg_tower_damage: number ;
  avg_kda: number ;
  avg_kill_participation: number ;

  updated_at: string; 
}