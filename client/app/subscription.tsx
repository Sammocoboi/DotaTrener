import { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import axios from "axios";
import { getToken } from "@/lib/token-storage";
import { colors } from "@/lib/theme";
import { API_BASE as API } from "@/lib/api";

type SubscriptionData = {
  id: number;
  is_active: boolean;
  plan: string;
  started_at: string;
  expires_at: string;
  is_expired: boolean;
};

export default function SubscriptionScreen() {
  const params = useLocalSearchParams<{ token: string }>();
  const token = params.token || getToken();
  const headers = { Authorization: `Token ${token}` };
  const [sub, setSub] = useState<SubscriptionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [subscribing, setSubscribing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    axios
      .get(`${API}/subscription/`, { headers })
      .then((r) => setSub(r.data.subscription))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  const handleSubscribe = async () => {
    setSubscribing(true);
    setError("");
    try {
      const r = await axios.post(`${API}/subscribe/`, {}, { headers });
      if (r.data.ok) {
        setSub(r.data.subscription);
      }
    } catch (e: any) {
      setError(e?.response?.data?.error || "Ошибка");
    } finally {
      setSubscribing(false);
    }
  };

  const isActive = sub?.is_active && !sub?.is_expired;
  const daysLeft = sub?.expires_at
    ? Math.max(
        0,
        Math.ceil(
          (new Date(sub.expires_at).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
        )
      )
    : 0;

  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: colors.bg }}
      contentContainerStyle={{ padding: 16 }}
    >
      <Pressable onPress={() => router.back()} style={{ marginBottom: 12 }}>
        <Text style={{ color: colors.orange }}>← Назад</Text>
      </Pressable>

      <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginBottom: 16 }}>
        Подписка тренера
      </Text>

      {isActive ? (
        <View
          style={{
            backgroundColor: colors.bgCard,
            borderRadius: 14,
            padding: 20,
            marginBottom: 16,
            borderWidth: 1,
            borderColor: colors.borderSoft,
          }}
        >
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <View style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: colors.green }} />
            <Text style={{ color: colors.green, fontSize: 16, fontWeight: "700" }}>
              Подписка активна
            </Text>
          </View>

          <Text style={{ color: colors.text60, fontSize: 12, marginBottom: 4 }}>
            Тариф: Ежемесячная
          </Text>
          <Text style={{ color: colors.text60, fontSize: 12, marginBottom: 4 }}>
            Осталось дней: {daysLeft}
          </Text>
          {sub?.expires_at && (
            <Text style={{ color: colors.text40, fontSize: 11, marginTop: 4 }}>
              Действует до:{" "}
              {new Date(sub.expires_at).toLocaleDateString("ru-RU", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </Text>
          )}

          <Pressable
            onPress={() => router.push({ pathname: "my-services" as any, params: { token } })}
            style={{
              backgroundColor: colors.orange,
              padding: 12,
              borderRadius: 8,
              marginTop: 16,
              alignItems: "center",
            }}
          >
            <Text style={{ color: "#FFFFFF", fontSize: 14, fontWeight: "600" }}>Мои услуги</Text>
          </Pressable>
        </View>
      ) : (
        <>
          <View
            style={{
              backgroundColor: colors.bgCard,
              borderRadius: 14,
              padding: 20,
              marginBottom: 16,
              borderWidth: 2,
              borderColor: colors.orange,
            }}
          >
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <View
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 20,
                  backgroundColor: colors.orangeSoft,
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Text style={{ fontSize: 20 }}>⭐</Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ color: colors.text, fontSize: 18, fontWeight: "700" }}>
                  Тренер
                </Text>
                <Text style={{ color: colors.orange, fontSize: 14, fontWeight: "600" }}>
                  499 ₽/мес
                </Text>
              </View>
            </View>

            <View style={{ marginTop: 12, gap: 10 }}>
              <Feature text="Публикация услуг с ценами" />
              <Feature text="Загрузка видео-обзоров" />
              <Feature text="Чат с игроками" />
              <Feature text="Отзывы и рейтинг" />
              <Feature text="Социальные сети в профиле" />
            </View>
          </View>

          {error ? (
            <Text style={{ color: colors.red, fontSize: 12, marginBottom: 8 }}>{error}</Text>
          ) : null}

          <Pressable
            onPress={handleSubscribe}
            disabled={subscribing}
            style={{
              backgroundColor: subscribing ? colors.bgElevated : colors.orange,
              padding: 16,
              borderRadius: 12,
              alignItems: "center",
            }}
          >
            <Text
              style={{
                color: subscribing ? colors.text40 : "#FFFFFF",
                fontSize: 16,
                fontWeight: "700",
              }}
            >
              {subscribing ? "Активация..." : "Оформить подписку"}
            </Text>
          </Pressable>

          <Text
            style={{
              color: colors.text40,
              fontSize: 10,
              textAlign: "center",
              marginTop: 12,
              paddingHorizontal: 20,
            }}
          >
            Демо-режим: оплата не списывается. Подписка активируется на 30 дней.
          </Text>
        </>
      )}
    </ScrollView>
  );
}

function Feature({ text }: { text: string }) {
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
      <View
        style={{
          width: 20,
          height: 20,
          borderRadius: 10,
          backgroundColor: colors.green,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Text style={{ color: "#FFFFFF", fontSize: 11, fontWeight: "700" }}>✓</Text>
      </View>
      <Text style={{ color: colors.text80, fontSize: 13 }}>{text}</Text>
    </View>
  );
}
