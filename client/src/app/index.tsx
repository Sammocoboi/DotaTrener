import { router } from "expo-router";
import {View,Text,Button}from "react-native";

export default function HomeScreen(){
  return(
    <View style={{flex:1, padding:16, gap:12, justifyContent:"center", backgroundColor:"#0B1120"}}>
      <Text style={{color:"#FFF", fontSize:24, fontWeight:"700", textAlign:"center"}}>Dota Trener</Text>
      <Button title="Герои" onPress={()=>router.push('./heroes/Hero')}/>
      <Button title="Мета Героев" onPress={()=>router.push('./heroes/HeroMeta')}/>
      <Button title="Тренеры" onPress={()=>router.push('coaches' as any)}/>
      <Button title="Привязать Steam" onPress={()=>router.push('steam-link' as any)}/>
      <Button title="Мои матчи" onPress={()=>router.push('matches' as any)}/>
      <Button title="Аккаунт" onPress={()=>router.push('profile' as any)}/>
    </View>
  )
}
