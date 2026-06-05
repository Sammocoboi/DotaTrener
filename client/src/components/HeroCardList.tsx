import axios from "axios";
import { Hero } from "@/types/hero";
import { useEffect, useState } from "react";
import { FlatList, Text, View, ActivityIndicator, StyleSheet } from "react-native";
import HeroCard from "./HeroCard";
import { API_HEROES as API_URL_HEROES } from "@/lib/api";

const HeroList = () => {
    const [heroes, setHeroes] = useState<Hero[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const getHeroes = async () => {
        try {
            const response = await axios.get(API_URL_HEROES);
      
            setHeroes(response.data.results);   
            setError(null);
        } catch (err) {
            console.error("Ошибка загрузки героев:", err);
            setError("Не удалось загрузить героев. Проверьте соединение с сервером.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        getHeroes();
    }, []);

    if (loading) {
        return (
            <View style={styles.center}>
                <ActivityIndicator size="large" />
                <Text>Загрузка героев...</Text>
            </View>
        );
    }

    if (error) {
        return (
            <View style={styles.center}>
                <Text style={styles.error}>{error}</Text>
            </View>
        );
    }

    if (heroes.length === 0) {
        return (
            <View style={styles.center}>
                <Text>Нет героев в базе данных.</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Герои Dota 2</Text>
            <FlatList
                data={heroes}
                keyExtractor={(item) => item.id.toString()}
                renderItem={({ item }) => <HeroCard hero={item} />}
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
    },
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        textAlign: 'center',
        marginVertical: 12,
    },
    center: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    error: {
        color: 'red',
        textAlign: 'center',
        margin: 20,
    },
});

export default HeroList;