import { Platform } from "react-native";

const DEV_HOST = "26.49.182.238";

const HOST = DEV_HOST;

export const API_BASE = `http://${HOST}:8000/api/coaching`;
export const API_ROOT = `http://${HOST}:8000`;
export const API_HEROES = `${API_BASE}/heroes/`;
export const API_STRATZ_META = `http://${HOST}:8000/api/stratz/hero-meta/`;
