import HeroList from "@/components/HeroCardList"
import { router } from "expo-router"
import { Pressable, Text, View } from "react-native"
import { colors } from "@/lib/theme"

const Hero =()=>{
    return(
        <View style={{ flex: 1, backgroundColor: colors.bg }}>
            <Pressable onPress={() => router.push("/")} style={{ padding: 16, paddingBottom: 0 }}>
                <Text style={{ color: colors.orange }}>← Назад</Text>
            </Pressable>
            <HeroList/>
        </View>
    )
}

export default Hero;
