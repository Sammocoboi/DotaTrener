
import { HeroMeta } from "@/types/herometa";
import { Text, View} from "react-native";


type Props = {
    herometa: HeroMeta;
}


const HeroMetaCard = ({ herometa }: Props) => {
    return (
        <View>
            <Text> {herometa.hero_name}</Text>
            <Text>киллов в срднем: { herometa.avg_kills}</Text>
            <Text>смертей в среднем: { herometa.avg_deaths}</Text>
            <Text>средний гпм: {herometa.avg_gpm}</Text>
            <Text>средний xpm {herometa.avg_xpm}</Text>
            <Text>средний нетворс {herometa.avg_networth}</Text>
            <Text>винрейт: {herometa.win_rate}</Text>
        </View>
    );
};

export default HeroMetaCard;