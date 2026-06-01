import { router } from "expo-router";
import {View,Text,Button}from "react-native";

export default function HomeScreen(){
  return(
    <View style={{flex:1, padding:16, gap:12, justifyContent:"center"}}>
      <Text>Главная страница</Text>
      <Button title="Герои" onPress={()=>router.push('./heroes/Hero')}/>
      <Button title="Мета Героев" onPress={()=>router.push('./heroes/HeroMeta')}/>
      <Button title="Привязать Steam" onPress={()=>router.push('steam-link' as any)}/>
      <Button title="Мои матчи" onPress={()=>router.push('matches' as any)}/>
    </View>
  )
    
  
}
