import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import Colors from '../constants/colors';

export default function JobCard({ job, isBookmarked, onToggleBookmark }) {
  const openLink = async () => {
    if (job.link) {
      await WebBrowser.openBrowserAsync(job.link);
    }
  };

  return (
    <View style={styles.card}>
      <View style={styles.topRow}>
        <Text style={styles.title} numberOfLines={2}>{job.title}</Text>
        <View style={styles.actions}>
          <TouchableOpacity onPress={onToggleBookmark} style={styles.bookmarkBtn}>
            <Text style={styles.bookmarkIcon}>{isBookmarked ? '★' : '☆'}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.applyBtn} onPress={openLink}>
            <Text style={styles.applyText}>Apply →</Text>
          </TouchableOpacity>
        </View>
      </View>
      <View style={styles.meta}>
        <Badge text={job.company} bg={Colors.badgeCompanyBg} color={Colors.badgeCompanyText} />
        <Badge text={job.country} bg={Colors.badgeCountryBg} color={Colors.badgeCountryText} />
        {job.category ? (
          <Badge text={job.category} bg={Colors.badgeCategoryBg} color={Colors.badgeCategoryText} />
        ) : null}
      </View>
      <View style={styles.details}>
        <Text style={styles.detailText}>📍 {job.location}</Text>
        <Text style={styles.detailText}>📅 {job.date}</Text>
      </View>
    </View>
  );
}

function Badge({ text, bg, color }) {
  return (
    <View style={[styles.badge, { backgroundColor: bg }]}>
      <Text style={[styles.badgeText, { color }]}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.white,
    borderRadius: 10,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: Colors.cardBorder,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 8,
    marginBottom: 8,
  },
  title: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: Colors.text,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  bookmarkBtn: { padding: 4 },
  bookmarkIcon: { fontSize: 22, color: Colors.accent },
  applyBtn: {
    backgroundColor: Colors.accent,
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 6,
  },
  applyText: {
    color: Colors.white,
    fontSize: 13,
    fontWeight: '600',
  },
  meta: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 20,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  details: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  detailText: {
    fontSize: 13,
    color: Colors.textLight,
  },
});
