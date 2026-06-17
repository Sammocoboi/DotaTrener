import { Hero } from "@/types/hero";
import { Text, View, StyleSheet } from "react-native";

type Props = {
    hero: Hero;
}

const HeroCard = ({ hero }: Props) => {
    return (
        <View style={styles.card}>
            <Text style={styles.name}>{hero.localized_name}</Text>
            <Text style={styles.attr}>Атрибут: {hero.primary_attr}</Text>
            <Text style={styles.roles}>Роли: {Array.isArray(hero.roles) ? hero.roles.join(', ') : (hero.roles && typeof hero.roles === 'object' ? Object.keys(hero.roles).join(', ') : 'нет')}</Text>
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        padding: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#ccc',
        backgroundColor: '#f9f9f9',
    },
    name: {
        fontWeight: 'bold',
        fontSize: 16,
    },
    attr: {
        fontSize: 14,
        color: '#555',
    },
    roles: {
        fontSize: 12,
        color: '#777',
    },
});

export default HeroCard;