import React from 'react';
import { View, TextInput, StyleSheet } from 'react-native';
import Colors from '../constants/colors';

export default function SearchBar({ value, onChangeText }) {
  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Search jobs by title, company, or location..."
        placeholderTextColor={Colors.textMuted}
        value={value}
        onChangeText={onChangeText}
        autoCorrect={false}
        clearButtonMode="while-editing"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 4,
  },
  input: {
    backgroundColor: Colors.white,
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 15,
    color: Colors.text,
    borderWidth: 1,
    borderColor: Colors.border,
  },
});
