import { useEffect } from "react";
import { Stack } from 'expo-router';
import { colors } from '@/lib/theme';
import { initToken } from '@/lib/token-storage';

export default function Layout() {
  useEffect(() => { initToken(); }, []);
  return <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.bg } }} />;
}
