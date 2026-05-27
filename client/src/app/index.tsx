import { router } from "expo-router";
import {View,Text,Button}from "react-native";

export default function HomeScreen(){
  return(
    <View>
      <Text>Главная страница</Text>
      <Button title="герои" onPress={()=>router.push('/heroes/hero')}/>
      <Button title=""  onPress={()=>router.push('/info/contacts')}/>
    </View>
  )
    
  
}
