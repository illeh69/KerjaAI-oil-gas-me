import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { JobsProvider } from './src/context/JobsContext';
import HomeScreen from './src/screens/HomeScreen';
import BookmarksScreen from './src/screens/BookmarksScreen';
import AboutScreen from './src/screens/AboutScreen';
import Colors from './src/constants/colors';

const Tab = createBottomTabNavigator();

function TabIcon({ label, focused }) {
  const icons = { Home: '🏠', Bookmarks: '★', About: 'ℹ️' };
  return null; // Icons rendered via tabBarIcon text
}

export default function App() {
  return (
    <JobsProvider>
      <NavigationContainer>
        <StatusBar style="light" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            headerShown: false,
            tabBarActiveTintColor: Colors.accent,
            tabBarInactiveTintColor: Colors.textMuted,
            tabBarStyle: {
              backgroundColor: Colors.white,
              borderTopColor: Colors.border,
              paddingBottom: 4,
              height: 56,
            },
            tabBarIcon: ({ focused, color, size }) => {
              const icons = { Home: '🏠', Bookmarks: '⭐', About: 'ℹ️' };
              return (
                <React.Fragment>
                  {/* Using text emoji as icons for simplicity */}
                </React.Fragment>
              );
            },
            tabBarLabel: route.name,
          })}
        >
          <Tab.Screen
            name="Home"
            component={HomeScreen}
            options={{
              tabBarIcon: ({ color }) => null,
              tabBarLabel: '🏠 Jobs',
            }}
          />
          <Tab.Screen
            name="Bookmarks"
            component={BookmarksScreen}
            options={{
              tabBarIcon: ({ color }) => null,
              tabBarLabel: '⭐ Saved',
            }}
          />
          <Tab.Screen
            name="About"
            component={AboutScreen}
            options={{
              tabBarIcon: ({ color }) => null,
              tabBarLabel: 'ℹ️ About',
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </JobsProvider>
  );
}
