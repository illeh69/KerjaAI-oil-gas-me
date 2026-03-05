import React from 'react';
import { View, FlatList, Text, StyleSheet } from 'react-native';
import { useJobs } from '../context/JobsContext';
import JobCard from '../components/JobCard';
import Colors from '../constants/colors';

export default function BookmarksScreen() {
  const { bookmarkedJobs, bookmarkIds, toggleBookmark } = useJobs();

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Saved Jobs</Text>
        <Text style={styles.count}>{bookmarkedJobs.length} bookmarked</Text>
      </View>
      <FlatList
        data={bookmarkedJobs}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <JobCard
            job={item}
            isBookmarked={bookmarkIds.includes(item.id)}
            onToggleBookmark={() => toggleBookmark(item.id)}
          />
        )}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyIcon}>☆</Text>
            <Text style={styles.emptyTitle}>No saved jobs yet</Text>
            <Text style={styles.emptyText}>
              Tap the star icon on any job to save it here for later.
            </Text>
          </View>
        }
        contentContainerStyle={{ paddingBottom: 30 }}
      />
    </View>
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
  count: { fontSize: 14, color: Colors.textLight, marginTop: 4 },
  emptyContainer: {
    alignItems: 'center',
    padding: 60,
  },
  emptyIcon: { fontSize: 48, color: Colors.textMuted, marginBottom: 16 },
  emptyTitle: { fontSize: 18, fontWeight: '600', color: Colors.text, marginBottom: 8 },
  emptyText: { fontSize: 14, color: Colors.textLight, textAlign: 'center' },
});
