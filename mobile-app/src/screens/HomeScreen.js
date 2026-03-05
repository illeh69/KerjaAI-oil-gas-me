import React, { useState, useCallback } from 'react';
import { View, FlatList, TouchableOpacity, Text, StyleSheet, RefreshControl } from 'react-native';
import { useJobs } from '../context/JobsContext';
import Header from '../components/Header';
import SearchBar from '../components/SearchBar';
import FilterModal from '../components/FilterModal';
import JobCard from '../components/JobCard';
import Pagination from '../components/Pagination';
import Colors from '../constants/colors';

export default function HomeScreen() {
  const {
    stats, filterOptions, paged, filtered, page, setPage,
    query, company, country, category, setFilters,
    bookmarkIds, toggleBookmark,
  } = useJobs();

  const [modalType, setModalType] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 300);
  }, []);

  const filterButtons = [
    { key: 'company', label: company || 'Company', active: !!company },
    { key: 'country', label: country || 'Country', active: !!country },
    { key: 'category', label: category || 'Category', active: !!category },
  ];

  const modalConfig = {
    company: { title: 'Select Company', options: filterOptions.companies, selected: company, onSelect: (v) => setFilters({ company: v }) },
    country: { title: 'Select Country', options: filterOptions.countries, selected: country, onSelect: (v) => setFilters({ country: v }) },
    category: { title: 'Select Category', options: filterOptions.categories, selected: category, onSelect: (v) => setFilters({ category: v }) },
  };

  const ListHeader = () => (
    <>
      <Header stats={stats} />
      <SearchBar value={query} onChangeText={(q) => setFilters({ query: q })} />
      <View style={styles.filterRow}>
        {filterButtons.map((fb) => (
          <TouchableOpacity
            key={fb.key}
            style={[styles.filterBtn, fb.active && styles.filterBtnActive]}
            onPress={() => setModalType(fb.key)}
          >
            <Text style={[styles.filterBtnText, fb.active && styles.filterBtnTextActive]} numberOfLines={1}>
              {fb.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      <Text style={styles.resultsText}>
        Showing {paged.start}-{paged.end} of {paged.total} jobs
      </Text>
    </>
  );

  const ListFooter = () => (
    <View style={{ paddingBottom: 30 }}>
      <Pagination currentPage={page} totalPages={paged.totalPages} onPageChange={setPage} />
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={paged.data}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <JobCard
            job={item}
            isBookmarked={bookmarkIds.includes(item.id)}
            onToggleBookmark={() => toggleBookmark(item.id)}
          />
        )}
        ListHeaderComponent={ListHeader}
        ListFooterComponent={ListFooter}
        ListEmptyComponent={
          <Text style={styles.empty}>No jobs match your search criteria.</Text>
        }
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.accent} />
        }
      />

      {modalType && (
        <FilterModal
          visible={!!modalType}
          {...modalConfig[modalType]}
          onClose={() => setModalType(null)}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  filterRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 8,
  },
  filterBtn: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: Colors.white,
    borderWidth: 1,
    borderColor: Colors.border,
    alignItems: 'center',
  },
  filterBtnActive: {
    backgroundColor: Colors.primaryMid,
    borderColor: Colors.primaryMid,
  },
  filterBtnText: { fontSize: 13, color: Colors.textLight },
  filterBtnTextActive: { color: Colors.white, fontWeight: '600' },
  resultsText: {
    paddingHorizontal: 16,
    paddingBottom: 8,
    fontSize: 13,
    color: Colors.textLight,
  },
  empty: {
    textAlign: 'center',
    padding: 40,
    fontSize: 15,
    color: Colors.textMuted,
  },
});
