import { useEffect, useState } from "react";
import { View, Text, FlatList, Button } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { Match } from "@/types/match";
import axios from "axios";