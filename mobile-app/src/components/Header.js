import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Colors from '../constants/colors';
import StatsBar from './StatsBar';

export default function Header({ stats }) {
  return (
    <LinearGradient
      colors={[Colors.primary, Colors.primaryDark, Colors.primaryMid]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}
    >
      <Text style={styles.title}>
        Middle East{' '}
        <Text style={styles.titleAccent}>Oil & Gas</Text>
        {'\n'}Job Board
      </Text>
      <Text style={styles.subtitle}>
        Latest job vacancies from top oil & gas companies in the Middle East
      </Text>
      <StatsBar stats={stats} />
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingTop: 60,
    paddingBottom: 24,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 26,
    fontWeight: '700',
    color: Colors.white,
    textAlign: 'center',
    marginBottom: 8,
  },
  titleAccent: {
    color: Colors.accent,
  },
  subtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.7)',
    textAlign: 'center',
    marginBottom: 16,
  },
});
