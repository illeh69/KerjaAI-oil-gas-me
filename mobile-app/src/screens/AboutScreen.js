import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import { useJobs } from '../context/JobsContext';
import Colors from '../constants/colors';

export default function AboutScreen() {
  const { stats } = useJobs();

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>About</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.appName}>ME Oil & Gas Jobs</Text>
        <Text style={styles.version}>Version 1.0.0</Text>
        <Text style={styles.desc}>
          A comprehensive job board featuring the latest vacancies from top oil and gas companies
          across the Middle East. Browse {stats.totalJobs} jobs from {stats.totalCompanies} companies
          in {stats.totalCountries} countries.
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Data Sources</Text>
        <Text style={styles.bodyText}>
          Job listings are collected from official company career portals including Saudi Aramco,
          QatarEnergy, ADNOC, SLB, Baker Hughes, Halliburton, Shell, TotalEnergies, BP, and more.
        </Text>
        <Text style={[styles.bodyText, { marginTop: 8 }]}>
          Jobs may have been updated since last collection. Always verify details on the company's
          official career page.
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Features</Text>
        <Text style={styles.bodyText}>• Search across all job titles, companies, and locations</Text>
        <Text style={styles.bodyText}>• Filter by company, country, or category</Text>
        <Text style={styles.bodyText}>• Save jobs to your bookmarks for later</Text>
        <Text style={styles.bodyText}>• Apply directly through company career portals</Text>
        <Text style={styles.bodyText}>• Works offline — all data bundled in-app</Text>
      </View>

      <TouchableOpacity
        style={styles.linkBtn}
        onPress={() => WebBrowser.openBrowserAsync('https://illeh69.github.io/KerjaAI-oil-gas-me/')}
      >
        <Text style={styles.linkText}>Visit Web Version →</Text>
      </TouchableOpacity>

      <Text style={styles.footer}>Built with KerjaAI</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: {
    backgroundColor: Colors.white,
    padding: 20,
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  title: { fontSize: 24, fontWeight: '700', color: Colors.text },
  card: {
    backgroundColor: Colors.white,
    margin: 16,
    marginBottom: 0,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  appName: { fontSize: 20, fontWeight: '700', color: Colors.text },
  version: { fontSize: 13, color: Colors.textLight, marginTop: 4, marginBottom: 12 },
  desc: { fontSize: 15, color: Colors.text, lineHeight: 22 },
  sectionTitle: { fontSize: 17, fontWeight: '600', color: Colors.text, marginBottom: 10 },
  bodyText: { fontSize: 14, color: Colors.textLight, lineHeight: 21 },
  linkBtn: {
    margin: 16,
    padding: 16,
    backgroundColor: Colors.accent,
    borderRadius: 10,
    alignItems: 'center',
  },
  linkText: { color: Colors.white, fontSize: 16, fontWeight: '600' },
  footer: {
    textAlign: 'center',
    padding: 20,
    paddingBottom: 40,
    color: Colors.textMuted,
    fontSize: 13,
  },
});
