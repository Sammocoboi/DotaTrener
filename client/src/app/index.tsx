import { router } from "expo-router";
import {View,Text,Button}from "react-native";

export default function HomeScreen(){
  return(
    <View>
      <Text>Главная страница</Text>
      <Button title="герои" onPress={()=>router.push('./heroes/Hero')}/>
      <Button title="Мета Гером" onPress={()=>router.push('./heroes/HeroMeta')}/>
    </View>
  )
    
  
}
