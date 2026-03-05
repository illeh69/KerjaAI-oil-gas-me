import React, { useState } from 'react';
import {
  View, Text, Modal, TouchableOpacity, FlatList, StyleSheet, TextInput, SafeAreaView,
} from 'react-native';
import Colors from '../constants/colors';

export default function FilterModal({ visible, title, options, selected, onSelect, onClose }) {
  const [search, setSearch] = useState('');

  const filtered = search
    ? options.filter((o) => o.label.toLowerCase().includes(search.toLowerCase()))
    : options;

  const handleSelect = (val) => {
    onSelect(val === selected ? '' : val);
    onClose();
    setSearch('');
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>{title}</Text>
          <TouchableOpacity onPress={() => { onClose(); setSearch(''); }}>
            <Text style={styles.close}>Close</Text>
          </TouchableOpacity>
        </View>

        <TextInput
          style={styles.search}
          placeholder={`Search ${title.toLowerCase()}...`}
          placeholderTextColor={Colors.textMuted}
          value={search}
          onChangeText={setSearch}
          clearButtonMode="while-editing"
        />

        {selected ? (
          <TouchableOpacity style={styles.clearBtn} onPress={() => handleSelect('')}>
            <Text style={styles.clearText}>Clear filter</Text>
          </TouchableOpacity>
        ) : null}

        <FlatList
          data={filtered}
          keyExtractor={(item) => item.value}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[styles.option, item.value === selected && styles.optionActive]}
              onPress={() => handleSelect(item.value)}
            >
              <Text style={[styles.optionText, item.value === selected && styles.optionTextActive]}>
                {item.label}
              </Text>
              {item.value === selected && <Text style={styles.check}>✓</Text>}
            </TouchableOpacity>
          )}
        />
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    backgroundColor: Colors.white,
  },
  title: { fontSize: 18, fontWeight: '600', color: Colors.text },
  close: { fontSize: 16, color: Colors.accent, fontWeight: '600' },
  search: {
    margin: 12,
    backgroundColor: Colors.white,
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 15,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  clearBtn: {
    marginHorizontal: 12,
    marginBottom: 8,
    padding: 10,
    backgroundColor: '#fce8e6',
    borderRadius: 8,
    alignItems: 'center',
  },
  clearText: { color: '#d93025', fontWeight: '600', fontSize: 14 },
  option: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 14,
    marginHorizontal: 12,
    marginBottom: 4,
    backgroundColor: Colors.white,
    borderRadius: 8,
  },
  optionActive: { backgroundColor: Colors.primaryMid },
  optionText: { fontSize: 15, color: Colors.text },
  optionTextActive: { color: Colors.white, fontWeight: '600' },
  check: { color: Colors.white, fontSize: 18, fontWeight: '700' },
});
