import axios from "axios";
import { HeroMeta } from "@/types/herometa";
import { Text, View, Button} from "react-native";
import { useEffect, useState } from "react";

type Props = {
    herometa: HeroMeta;
}
const API_URLS_INFO = "http://127.0.0.1:8000/api/stratz/hero-meta/"

const HeroCard = ({ herometa }: Props) => {
    const 
    return (
        <View>
            <Text> {herometa.heroname}</Text>
            <Text>Атрибут: {hero.primary_attr}</Text>
            <Text>Роли: {hero.roles?.join(', ') || 'нет'}</Text>
        </View>
    );
};