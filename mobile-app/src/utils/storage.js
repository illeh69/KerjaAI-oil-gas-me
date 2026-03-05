import AsyncStorage from '@react-native-async-storage/async-storage';

const BOOKMARKS_KEY = '@me_oil_gas_bookmarks';

export async function getBookmarks() {
  try {
    const raw = await AsyncStorage.getItem(BOOKMARKS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export async function addBookmark(jobId) {
  const bookmarks = await getBookmarks();
  if (!bookmarks.includes(jobId)) {
    bookmarks.push(jobId);
    await AsyncStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
  }
  return bookmarks;
}

export async function removeBookmark(jobId) {
  let bookmarks = await getBookmarks();
  bookmarks = bookmarks.filter((id) => id !== jobId);
  await AsyncStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
  return bookmarks;
}

export async function isBookmarked(jobId) {
  const bookmarks = await getBookmarks();
  return bookmarks.includes(jobId);
}
