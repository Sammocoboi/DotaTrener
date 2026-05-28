import HeroMetaCardList from "@/components/HeroMetaCardList"
import { router } from "expo-router"
import { Button,View,ScrollView } from "react-native"

const HeroMeta =()=>{
    return(
        <ScrollView>

            <Button title="назад" onPress={()=>router.back()}/>
            <HeroMetaCardList />
        </ScrollView>
    )
}

export default HeroMeta;