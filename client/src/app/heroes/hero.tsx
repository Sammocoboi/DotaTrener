import HeroList from "@/components/HeroCardList"
import { router } from "expo-router"
import { Button,View } from "react-native"

const Hero =()=>{
    return(
        <View>

            <Button title="назад" onPress={()=>router.back()}/>
            <HeroList/>
        </View>
    )
}

export default Hero;