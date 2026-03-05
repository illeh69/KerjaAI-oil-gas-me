import React, { createContext, useState, useEffect, useCallback, useContext } from 'react';
import { getAllJobs, filterJobs, paginate, getStats, getFilterOptions } from '../utils/data';
import { getBookmarks, addBookmark as addBm, removeBookmark as removeBm } from '../utils/storage';

const JobsContext = createContext();

export function JobsProvider({ children }) {
  const allJobs = getAllJobs();
  const [query, setQuery] = useState('');
  const [company, setCompany] = useState('');
  const [country, setCountry] = useState('');
  const [category, setCategory] = useState('');
  const [page, setPage] = useState(1);
  const [bookmarkIds, setBookmarkIds] = useState([]);

  useEffect(() => {
    getBookmarks().then(setBookmarkIds);
  }, []);

  const filtered = filterJobs(allJobs, { query, company, country, category });
  const paged = paginate(filtered, page);
  const stats = getStats(allJobs);
  const filterOptions = getFilterOptions(allJobs);

  const resetFilters = useCallback(() => {
    setQuery('');
    setCompany('');
    setCountry('');
    setCategory('');
    setPage(1);
  }, []);

  const setFilters = useCallback(({ query: q, company: c, country: ct, category: cat }) => {
    if (q !== undefined) setQuery(q);
    if (c !== undefined) setCompany(c);
    if (ct !== undefined) setCountry(ct);
    if (cat !== undefined) setCategory(cat);
    setPage(1);
  }, []);

  const toggleBookmark = useCallback(async (jobId) => {
    if (bookmarkIds.includes(jobId)) {
      const updated = await removeBm(jobId);
      setBookmarkIds(updated);
    } else {
      const updated = await addBm(jobId);
      setBookmarkIds(updated);
    }
  }, [bookmarkIds]);

  const bookmarkedJobs = allJobs.filter((j) => bookmarkIds.includes(j.id));

  return (
    <JobsContext.Provider
      value={{
        allJobs,
        filtered,
        paged,
        stats,
        filterOptions,
        query, company, country, category,
        setFilters,
        resetFilters,
        page,
        setPage,
        bookmarkIds,
        bookmarkedJobs,
        toggleBookmark,
      }}
    >
      {children}
    </JobsContext.Provider>
  );
}

export function useJobs() {
  return useContext(JobsContext);
}
