import jobsData from '../../assets/data/jobs.json';

export function getAllJobs() {
  return jobsData;
}

export function getStats(jobs) {
  const companies = new Set();
  const countries = new Set();
  jobs.forEach((j) => {
    if (j.company) companies.add(j.company);
    if (j.country) countries.add(j.country);
  });
  return {
    totalJobs: jobs.length,
    totalCompanies: companies.size,
    totalCountries: countries.size,
  };
}

export function getFilterOptions(jobs) {
  const companyCount = {};
  const countryCount = {};
  const categoryCount = {};

  jobs.forEach((j) => {
    if (j.company) companyCount[j.company] = (companyCount[j.company] || 0) + 1;
    if (j.country) countryCount[j.country] = (countryCount[j.country] || 0) + 1;
    if (j.category) categoryCount[j.category] = (categoryCount[j.category] || 0) + 1;
  });

  const toOptions = (obj) =>
    Object.keys(obj)
      .sort()
      .map((k) => ({ label: `${k} (${obj[k]})`, value: k }));

  return {
    companies: toOptions(companyCount),
    countries: toOptions(countryCount),
    categories: toOptions(categoryCount),
  };
}

export function filterJobs(jobs, { query, company, country, category }) {
  const q = (query || '').toLowerCase();
  return jobs.filter((j) => {
    if (q) {
      const match =
        j.title.toLowerCase().includes(q) ||
        j.company.toLowerCase().includes(q) ||
        j.location.toLowerCase().includes(q) ||
        j.category.toLowerCase().includes(q);
      if (!match) return false;
    }
    if (company && j.company !== company) return false;
    if (country && j.country !== country) return false;
    if (category && j.category !== category) return false;
    return true;
  });
}

export function paginate(items, page, perPage = 25) {
  const start = (page - 1) * perPage;
  return {
    data: items.slice(start, start + perPage),
    totalPages: Math.ceil(items.length / perPage),
    total: items.length,
    start: start + 1,
    end: Math.min(start + perPage, items.length),
  };
}
