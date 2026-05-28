import axios from "axios";
import { HeroMeta } from "@/types/herometa";
import { Text, View, Button} from "react-native";
import { useEffect, useState } from "react";
import HeroMetaCard from "./HeroMetaCard";
import { FlatList,ScrollView } from "react-native";

const API_URL_HEROES = "http://127.0.0.1:8000/api/stratz/hero-meta/";

const HeroMetaCardList = () =>{
    const [heromet,setheromet] = useState<HeroMeta[]>([]);
    const getHeroes = async ()=>{
        const response = await axios.get(API_URL_HEROES)
        setheromet(response.data.results)
    }
        useEffect(() => {
        getHeroes();
    }, []);
    return(

        <ScrollView>
            
            <FlatList
            data={heromet}
            keyExtractor={(item)=>item.id.toString()}
            renderItem={({item})=><HeroMetaCard herometa={item}/>}
            />
        </ScrollView>
    );
};

export default HeroMetaCardList;