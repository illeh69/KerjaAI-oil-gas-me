import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Colors from '../constants/colors';

export default function StatsBar({ stats }) {
  return (
    <View style={styles.row}>
      <Stat num={stats.totalJobs} label="Total Jobs" />
      <Stat num={stats.totalCompanies} label="Companies" />
      <Stat num={stats.totalCountries} label="Countries" />
    </View>
  );
}

function Stat({ num, label }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.num}>{num}</Text>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 30,
  },
  stat: { alignItems: 'center' },
  num: {
    fontSize: 28,
    fontWeight: '700',
    color: Colors.accent,
  },
  label: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.6)',
  },
});
