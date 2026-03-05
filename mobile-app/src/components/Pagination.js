import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import Colors from '../constants/colors';

export default function Pagination({ currentPage, totalPages, onPageChange }) {
  if (totalPages <= 1) return null;

  const pages = [];
  const start = Math.max(1, currentPage - 2);
  const end = Math.min(totalPages, currentPage + 2);

  if (start > 1) pages.push(1);
  if (start > 2) pages.push('...');
  for (let i = start; i <= end; i++) pages.push(i);
  if (end < totalPages - 1) pages.push('...');
  if (end < totalPages) pages.push(totalPages);

  return (
    <View style={styles.container}>
      {currentPage > 1 && (
        <Btn label="← Prev" onPress={() => onPageChange(currentPage - 1)} />
      )}
      {pages.map((p, i) =>
        p === '...' ? (
          <Text key={`d${i}`} style={styles.dots}>...</Text>
        ) : (
          <Btn
            key={p}
            label={String(p)}
            active={p === currentPage}
            onPress={() => onPageChange(p)}
          />
        )
      )}
      {currentPage < totalPages && (
        <Btn label="Next →" onPress={() => onPageChange(currentPage + 1)} />
      )}
    </View>
  );
}

function Btn({ label, active, onPress }) {
  return (
    <TouchableOpacity
      style={[styles.btn, active && styles.btnActive]}
      onPress={onPress}
    >
      <Text style={[styles.btnText, active && styles.btnTextActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'center',
    flexWrap: 'wrap',
    gap: 6,
    paddingVertical: 16,
    paddingHorizontal: 16,
  },
  btn: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: Colors.border,
    backgroundColor: Colors.white,
  },
  btnActive: {
    backgroundColor: Colors.primaryMid,
    borderColor: Colors.primaryMid,
  },
  btnText: { fontSize: 14, color: Colors.text },
  btnTextActive: { color: Colors.white, fontWeight: '600' },
  dots: { fontSize: 14, color: Colors.textMuted, alignSelf: 'center' },
});
