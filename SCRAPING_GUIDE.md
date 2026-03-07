# Oil & Gas Job Board - Scraping Guide

## Company Scraping Methods

### 1. SLB (824 jobs)
- **URL**: https://careers.slb.com/job-listing
- **Platform**: Coveo Atomic Search
- **Method**: REST API POST to `{apiBase}/rest/search/v2?organizationId={orgId}`
- **Config Source**: `document.querySelector('atomic-search-interface').engine.state.configuration`
- **Credentials**: orgId=`schlumbergerproduction0cs2zrh7`, Bearer token from engine state
- **Notes**: Single API call with `numberOfResults: 1000` returns all jobs. Returns structured JSON with `raw.country`, `raw.city`, `raw.category` arrays.

### 2. Baker Hughes (741 jobs)
- **URL**: https://careers.bakerhughes.com/global/en/search-results
- **Platform**: Phenom People
- **Method**: Phenom API endpoint
- **Notes**: Re-scraped worldwide via Phenom platform.

### 3. TotalEnergies (658 jobs)
- **URL**: https://jobs.totalenergies.com/en_US/careers/SearchJobs/?listFilterMode=1&jobRecordsPerPage=20
- **Platform**: Custom careers portal
- **Method**: Server-side pagination via `jobOffset` parameter (20 per page, 34 pages)
- **DOM Selectors**:
  - Job container: `.article--result`
  - Title/link: `a.link`
  - Date: `.list-item-jobCreationDate`
  - Country: `.list-item-jobCountry`
  - Employment type: `.list-item-employmentType`
  - Company: `.list-item-jobEmployerCompany`
- **Notes**: Pages are slow (~5 sec each). Site returns many duplicate jobs across pages — must deduplicate by URL. Pagination: `?listFilterMode=1&jobRecordsPerPage=20&jobOffset={N}`. Sync XHR limited to ~2 pages per browser call.

### 4. ExxonMobil (542 jobs)
- **URL**: https://jobs.exxonmobil.com/search/?createNewAlert=false&q=&locationsearch=
- **Platform**: SuccessFactors (SAP)
- **Method**: Server-side pagination via `startrow` parameter (25 per page)
- **DOM Selectors**:
  - Job rows: `table.searchResults tr.data-row`
  - Title link: `a.jobTitle-link`
  - Columns (td): location, career field, job type, post date
- **Pagination URL**: `/search/?q=&sortColumn=referencedate&sortDirection=desc&startrow={N}`
- **Notes**: Country is a 2-letter code at end of location string (e.g., "Houston, TX, US"). Needs country code mapping. Can fetch pages via `fetch()` and parse with DOMParser.

### 5. Halliburton (523 jobs)
- **URL**: https://careers.halliburton.com/en/search-jobs
- **Platform**: TalentBrew
- **Method**: AJAX API endpoint `/en/search-jobs/results?CurrentPage={N}&RecordsPerPage={N}`
- **Notes**: Set `RecordsPerPage=600` to get all jobs in one call. HTML response has literal `\r\n` — must replace `\\r\\n` with spaces before DOMParser. Job links from `href` attribute on `<a data-job-id>` elements (NOT `?jobId=` which redirects to search page). Title from `<h2>`, location from `span.job-location`, category from `span.jobCategories`.

### 6. BP (416 jobs)
- **URL**: https://careers.bp.com/listing
- **Platform**: Algolia Search
- **Method**: REST API POST to `https://UM59DWRPA1-dsn.algolia.net/1/indexes/production_bp_jobs/query`
- **Credentials**: AppId=`UM59DWRPA1`, API Key=`33719eb8d9f28725f375583b7e78dbab`, Index=`production_bp_jobs`
- **Config Source**: `window.search.client.transporter.queryParameters` (appId, apiKey), `search.mainIndex` (index name)
- **Notes**: Single API call with `hitsPerPage=1000`. Returns title, primary_country[], location[], professional_function[], posting_date[], slug[]. Job links use format: `https://careers.bp.com/job-description/{RQ_ID}` (NOT `/listing/{slug}` which returns 404).

### 7. QatarEnergy (293 jobs)
- **URL**: Middle East only (original scrape)
- **Notes**: ME-only company, unchanged from original scrape.

### 8. Saudi Aramco (220 jobs)
- **URL**: Middle East only (original scrape)
- **Notes**: ME-only company, unchanged from original scrape.

### 9. Shell (181 jobs)
- **URL**: https://shell.wd3.myworkdayjobs.com/ShellCareers
- **Platform**: Workday
- **Method**: JSON API POST to `/wday/cxs/shell/ShellCareers/jobs`
- **Body**: `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`
- **Notes**: Links must include `/ShellCareers/` in path (e.g., `myworkdayjobs.com/ShellCareers/job/...`). Workday was intermittently down for maintenance.

### 10. Chevron (176 jobs)
- **URL**: Worldwide scrape
- **Notes**: Scraped worldwide.

### 11. Petrofac (55 jobs)
- **URL**: https://petrofac.referrals.selectminds.com
- **Platform**: SelectMinds/iCIMS
- **Method**: URL-based pagination `/page/{N}`
- **Notes**: 55 jobs total. Used `fetch()` to load all pages and extract job data from DOM. Clean "and 1 additional location" from country field.

### 12. ConocoPhillips (31 jobs)
- **URL**: Worldwide scrape
- **Notes**: Scraped worldwide.

### 13. Petronas (30 jobs)
- **URL**: Worldwide scrape
- **Notes**: Scraped worldwide.

### 14. Suncor (27 jobs)
- **URL**: https://suncor.wd1.myworkdayjobs.com/Suncor_External
- **Platform**: Workday
- **Method**: Workday JSON API POST to `/wday/cxs/suncor/Suncor_External/jobs`
- **Body**: `{"appliedFacets":{},"limit":50,"offset":0,"searchText":""}`
- **Detail API**: GET `/wday/cxs/suncor/Suncor_External/job/{path}` for country info
- **Notes**: API sometimes returns 400 on repeated calls. DOM scraping works as fallback (page 1: 20 jobs, page 2: 7 jobs). Job links: `https://suncor.wd1.myworkdayjobs.com/Suncor_External/job/{path}`. Country from detail API: `jobPostingInfo.country.descriptor`.

### 15. Mubadala Energy (40 jobs)
- **URL**: https://www.careers-page.com/mubadalaenergy#openings
- **Platform**: careers-page.com (client-rendered SPA)
- **Method**: Live DOM scraping (fetch+DOMParser does NOT work — SPA requires live browser rendering)
- **Pagination**: `?page=N` (20 jobs per page, 2 pages)
- **DOM Selectors**:
  - Job links: `a[href*="/mubadalaenergy/job/"]`
  - Title: link text content
  - Location: `span.is-block` (first span after title)
  - Country: parsed from location string
- **Data Format**: `title~location~country~~~link` (no category or date available)
- **Notes**: Client-rendered SPA — JavaScript state (`window._mubJobs`) is lost on page navigation. Must extract and dump each page independently. "Tax Associate Energy Sector" has no location — defaults to Abu Dhabi, UAE (Mubadala HQ). Link format: `https://www.careers-page.com/mubadalaenergy/job/{CODE}`.

### Middle East Only Companies (unchanged)
- **ADNOC** (57 jobs)
- **QatarEnergy LNG**
- **ENOC**
- **PDO**
- **OQ Group**
- **KPC**
- **KNPC**
- **NIOC**
- **INOC**
- **Bapco**
- **Dragon Oil**
- **North Oil Company**

---

## Common Patterns

### Workday Sites
- API: POST `/wday/cxs/{company}/{site}/jobs` with `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`
- Detail: GET `/wday/cxs/{company}/{site}/job/{path}`
- Link format: `https://{company}.wd{N}.myworkdayjobs.com/{site}/job/{path}`

### Console Data Transfer
- Use `console.log()` to dump data from browser to VM
- For large datasets, dump as single JSON: `console.log('PREFIX' + JSON.stringify(data))`
- Read via `read_console_messages` tool — auto-persists to file if >50K chars
- Use markers (e.g., `EMSTART`/`EMEND`) for multi-line dumps

### CSV Format
All CSVs use: `Country,Company,Title,Category,Location,Date Posted,Link`

### Build Process
1. Run company-specific `build_{company}.py` to generate `{Company}_Jobs.csv`
2. Run `build_job_board.py` to combine all CSVs into `ME_Oil_Gas_Jobs.html`
3. Copy `ME_Oil_Gas_Jobs.html` to `index.html` for GitHub Pages
4. Git commit and push

### Git
- Repo: https://github.com/illeh69/KerjaAI-oil-gas-me
- Push: `git push https://illeh69:{TOKEN}@github.com/illeh69/KerjaAI-oil-gas-me.git main`
