import InfoPage from "@/components/HeroCardList"
import { router } from "expo-router"
import { Button,View } from "react-native"

const About =()=>{
    return(
        <View>
            <Button title="назад" onPress={()=>router.back()}/>
        </View>
    )
}

export default About;