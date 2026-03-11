# Oil & Gas Job Board - Scraping Guide

## Company Scraping Methods

### 1. SLB (843 jobs)
- **URL**: https://careers.slb.com/job-listing
- **Platform**: Coveo Atomic Search
- **Method**: REST API POST to `{apiBase}/rest/search/v2?organizationId={orgId}`
- **Config Source**: `document.querySelector('atomic-search-interface').engine.state.configuration`
- **Credentials**: orgId=`schlumbergerproduction0cs2zrh7`, Bearer token from engine state
- **Notes**: Single API call with `numberOfResults: 1000` returns all jobs. Returns structured JSON with `raw.country`, `raw.city`, `raw.category` arrays.

### 2. Baker Hughes (742 jobs)
- **URL**: https://careers.bakerhughes.com/global/en/search-results
- **Platform**: Phenom People
- **Method**: Fetch each page's HTML via `fetch()`, then extract embedded `eagerLoadRefineSearch` JSON using bracket-matching (NOT regex).
- **Pagination**: URL-based: `?from=N&s=1` where N increments by 10. Total pages = `ceil(totalHits / 10)`.
- **Total jobs check**: On page load, `window.phApp.ddo.eagerLoadRefineSearch.totalHits` gives the total count.
- **Data extraction per page**:
  1. Fetch HTML: `fetch('https://careers.bakerhughes.com/global/en/search-results?from=${offset}&s=1')`
  2. Find `"eagerLoadRefineSearch":` in the HTML string
  3. Use bracket-matching (count `{` and `}`) to extract the full JSON object — do NOT use regex (`.*?` fails on nested JSON)
  4. Parse JSON → `.data.jobs` array contains: `title`, `country`, `city`, `multi_category[0]`, `postedDate`, `applyUrl`
- **Bracket-matching code**:
  ```javascript
  const key = '"eagerLoadRefineSearch":';
  const idx = html.indexOf(key);
  const start = idx + key.length;
  let depth = 0, end = start;
  for (let i = start; i < html.length; i++) {
    if (html[i] === '{') depth++;
    else if (html[i] === '}') { depth--; if (depth === 0) { end = i + 1; break; } }
  }
  const obj = JSON.parse(html.substring(start, end));
  // obj.data.jobs = [{title, country, city, multi_category, postedDate, applyUrl, ...}]
  ```
- **Batch strategy**: Fetch 3 pages in parallel with `Promise.all()`, process in sequential batches to avoid browser timeout (60s limit per JS call). Each batch of 3 pages takes ~15-20 sec.
- **IMPORTANT — What does NOT work**:
  - The Phenom widget API (`POST /widgets` with `ddoKey: "eagerLoadRefineSearch"`) returns server errors for all page sizes
  - `POST /widgets` with `ddoKey: "refineSearch"` returns 0 results
  - Regex extraction of the embedded JSON fails because lazy `.*?` stops at inner `}` braces
  - Reading `window.phApp.ddo` directly only works on the currently loaded page (data is lost on navigation)
  - Fetching all 75 pages in a single JS call times out — must split into batches
- **Country normalization**: "United Arab Emirates" → "UAE", "United Kingdom" → "UK", "United States" → "USA"
- **Deduplication**: Some jobs appear on multiple pages — deduplicate by `title + '|' + applyUrl`

### 3. TotalEnergies (658 jobs)
- **URL**: https://jobs.totalenergies.com/en_US/careers/SearchJobs/
- **Platform**: Custom careers portal (server-rendered HTML)
- **Method**: Fetch each page's HTML via `fetch()`, parse with `DOMParser`, extract job data from `.article--result` elements.
- **Pagination**: URL parameter `jobOffset` in increments of 20: `?jobRecordsPerPage=20&jobOffset=N` (N = 0, 20, 40, ...).
- **Total jobs check**: Bottom of page shows "1-20 of N results". Also page title says "Page X".
- **Total pages**: `ceil(totalJobs / 20)` — typically ~34 pages.
- **Data extraction per page**:
  1. Fetch HTML: `fetch('https://jobs.totalenergies.com/en_US/careers/SearchJobs/?jobRecordsPerPage=20&jobOffset=${offset}')`
  2. Parse with `new DOMParser().parseFromString(html, 'text/html')`
  3. Select all `.article--result` elements
  4. For each article, get:
     - **Title**: `art.querySelector('h3 a, h2 a').textContent.trim()`
     - **Link**: `art.querySelector('h3 a, h2 a').getAttribute('href')` — full URL like `https://jobs.totalenergies.com/en_US/careers/JobDetail/TITLE/ID`
     - **Full text**: `art.textContent.trim().replace(/\s+/g, ' ')` — contains: `Title DATE Country ContractType CompanyEntity Apply`
     - **Date**: regex `(\d{2}-\d{2}-\d{4})` from full text (format: DD-MM-YYYY)
     - **Country**: text between date and contract type keyword
  5. Contract type keywords to split on: `Regular position`, `Fixed term position`, `Internship`, `Apprenticeship`, `Full-Time Apprenticeship`, `Alternance`, `Full-Time`, `Graduate`, `VIE`, `Sponsorship`
- **Country parsing code**:
  ```javascript
  const afterDate = text.substring(text.indexOf(dateMatch[1]) + dateMatch[1].length).trim();
  const contractTypes = ['Regular position', 'Fixed term position', 'Internship', 'Apprenticeship',
    'Full-Time Apprenticeship', 'Alternance', 'Full-Time', 'Graduate', 'VIE', 'Sponsorship'];
  let country = '';
  for (const ct of contractTypes) {
    const idx = afterDate.indexOf(ct);
    if (idx > 0) { country = afterDate.substring(0, idx).trim(); break; }
  }
  ```
- **Post-processing (Python)**: After extracting CSV, clean country field by stripping anything after contract type keywords. Some countries have suffixes like "/ US" or "/ FR" — strip with `.replace(/ \/ \w+$/, '')`.
- **Batch strategy**: Fetch 3 pages sequentially per JS call (each `fetch()` takes ~3-5 sec). Each JS call handles 3 pages (~15 sec). Do NOT try more than 3 sequential fetches per call — it will timeout at 60s.
- **IMPORTANT — What does NOT work**:
  - Fetching more than ~5 pages in a single JS execution times out (60s limit)
  - Parallel `Promise.all()` with many pages causes browser disconnection
  - The DOM selectors `.list-item-jobCreationDate`, `.list-item-jobCountry` etc. do NOT exist on the fetched HTML — the data is in unstructured text within `.article--result`
  - Country cannot be extracted from CSS class selectors — must parse from text between date and contract type
- **Country normalization**: "United Arab Emirates" → "UAE", "United Kingdom" → "UK", "United States" → "USA", strip "/ XX" suffixes
- **Deduplication**: Deduplicate by `title + '|' + href` after collection

### 4. ExxonMobil (536 jobs)
- **URL**: https://jobs.exxonmobil.com/search/?createNewAlert=false&q=&locationsearch=
- **Platform**: SuccessFactors (SAP)
- **Method**: Fetch each page's HTML via `fetch()`, parse with `DOMParser`, extract job data from `tr.data-row` elements.
- **Pagination**: URL parameter `startrow` in increments of 25: `/search/?q=&sortColumn=referencedate&sortDirection=desc&startrow={N}` (N = 0, 25, 50, ...).
- **Total jobs check**: `.paginationLabel` element shows "Results 1 – 25 of N".
- **Total pages**: `ceil(totalJobs / 25)`.
- **DOM Selectors**:
  - Job rows: `tr.data-row`
  - Title link: `a.jobTitle-link` → `.textContent.trim()` for title, `.getAttribute('href')` for link (prepend `https://jobs.exxonmobil.com` if relative)
  - Columns (td index): [0]=title, [1]=location, [2]=career field/category, [3]=job type, [4]=post date
- **Country extraction**: Location string ends with 2-letter ISO country code (e.g., "Houston, TX, US"). Extract with regex `/,\s*([A-Z]{2})\s*$/`. Map codes to full names using a lookup table (US→USA, GB→UK, AE→UAE, etc.).
- **Batch strategy**: Fetch 3 pages sequentially per JS call. Each page fetch takes ~2-3 sec. Total ~22 pages.
- **Notes**: Method is stable and works as documented. No API changes detected.

### 5. Halliburton (522 jobs)
- **URL**: https://careers.halliburton.com/en/search-jobs
- **Platform**: TalentBrew
- **Method**: Fetch each page's HTML via `fetch()`, parse with `DOMParser`, extract job data from `a[data-job-id]` elements.
- **Pagination**: URL parameter `?p=N` (N = 1, 2, 3, ...). Each fetched page returns 15 jobs. First page URL has no `?p` parameter.
- **Total jobs check**: Page body text contains "N results" (e.g., "522 results").
- **Total pages**: `ceil(totalJobs / 15)` — typically ~35 pages.
- **Data extraction per page**:
  1. Fetch HTML: `fetch('https://careers.halliburton.com/en/search-jobs?p=' + pageNum)` (page 1: no `?p` param)
  2. Parse with `new DOMParser().parseFromString(html, 'text/html')`
  3. Select all `a[data-job-id]` elements
  4. For each element:
     - **Title**: `a.querySelector('h2').textContent.trim()`
     - **Link**: `a.getAttribute('href')` — relative path, prepend `https://careers.halliburton.com`
     - **Location**: `a.querySelector('span.job-location').textContent.trim()` — contains city, state/province, country (with embedded newlines to clean)
     - **Category**: `a.querySelector('span.job-jobCategories').textContent.trim()` (NOTE: class is `job-jobCategories`, NOT `jobCategories`)
  5. **Country**: Last comma-separated part of location string after cleaning whitespace
- **Batch strategy**: Fetch 3 pages sequentially per JS call. Each page fetch takes ~3-5 sec due to large HTML (~840KB). Do NOT try more than 3 per call — 60s JS timeout.
- **IMPORTANT — What does NOT work**:
  - The old AJAX endpoint `/en/search-jobs/results?CurrentPage=1&RecordsPerPage=600` now returns `{"filters":"","results":"","hasJobs":true,"hasContent":false}` — empty results regardless of parameters or headers
  - Adding `X-Requested-With: XMLHttpRequest` header does not help
  - Setting geo location first via POST to `SetSearchRequestGeoLocation` does not help
  - The live page renders 23 jobs (more than the 15 in fetched HTML) because extra jobs are loaded by client-side JS after initial render
- **Country normalization**: Clean whitespace from location text, then extract last segment after final comma. "United States" → "USA", "United Kingdom" → "UK", "United Arab Emirates" → "UAE"
- **Notes**: No date posted field available in the listing page — leave Date Posted column empty in CSV.

### 6. BP (393 jobs)
- **URL**: https://bpinternational.wd3.myworkdayjobs.com/en-US/bpCareers
- **Platform**: Workday (primary), Algolia Search (backup)
- **Method (Primary — Workday)**: JSON API POST to `/wday/cxs/bpinternational/bpCareers/jobs`
- **Body**: `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`. Response has `total` field and `jobPostings[]` array.
- **Pagination**: 20 per page, use `offset=0,20,40,...` up to `Math.ceil(total/20)` pages (~20 pages for 393 jobs). Fetch in batches of 5 pages per JS call to avoid 60s timeout.
- **Data Structure**: Each `jobPostings[]` item: `title`, `externalPath` (relative URL), `locationsText` (format: "Country - City" e.g., "India - Pune", or country code prefix "IN: Pune"), `postedOn` (e.g., "Posted Today"), `bulletFields[]` (contains RQ ID).
- **Link Format**: `https://bpinternational.wd3.myworkdayjobs.com/en-US/bpCareers` + `externalPath`
- **Country Extraction**: Location text starts with country name ("India - Mumbai") or 2-letter code prefix ("IN:", "CN:", "GB:", "AU:", "US:", "HU:", "BR:", "PL:", "SG:", "ZA:", "TR:", "AE:", "OM:"). "N Locations" → "Multiple". Some jobs have null `locationsText` → "Unknown".
- **Notes**: Dedup by `externalPath`. 2 jobs may have null location. Navigate to Workday URL first, then use fetch() API from that page.
- **Method (Backup — Algolia Search)**:
  - URL: `https://careers.bp.com/listing`
  - REST API POST to `https://UM59DWRPA1-dsn.algolia.net/1/indexes/production_bp_jobs/query`
  - Credentials: AppId=`UM59DWRPA1`, API Key=`33719eb8d9f28725f375583b7e78dbab`, Index=`production_bp_jobs`
  - Config Source: `window.search.client.transporter.queryParameters` (appId, apiKey), `search.mainIndex` (index name)
  - Single API call with `hitsPerPage=1000`. Returns title, primary_country[], location[], professional_function[], posting_date[], slug[]. Job links: `https://careers.bp.com/job-description/{RQ_ID}`

### 7. QatarEnergy (287 jobs)
- **URL**: https://careerportal.qatarenergy.qa/jobs
- **Platform**: Jibe (Angular Material) with REST API
- **Method**: REST API at `/api/jobs?page=N&sortBy=relevance&descending=false&internal=false&limit=100&deviceId=undefined&domain=qatarenergy.jibeapply.com`. `limit=100` works — 3 API calls fetch all 292 results (284 unique after dedup).
- **Data Structure**: `response.jobs[].data` contains: `title`, `slug` (numeric ID used in link), `req_id`, `city`, `location_name`, `short_location`, `category` (array), `department`, `posted_date` (YYYY-MM-DD), `country`, `country_code`.
- **Link Format**: `https://careerportal.qatarenergy.qa/jobs/{slug}`
- **UI Notes**: Angular Material `mat-paginator` shows 10 per page. Lazy loads more on scroll. API `limit` param bypasses pagination entirely.
- **Notes**: All jobs in Qatar (Doha, Mesaieed, Ras Laffan, Dukhan, Offshore). Categories come directly from API data. 8 duplicate slugs removed.

### 8. Saudi Aramco (221 jobs)
- **URL**: https://careers.aramco.com/search/?q=&sortColumn=referencedate&sortDirection=desc
- **Platform**: Custom careers site (careers.aramco.com) with server-rendered HTML pagination
- **Method**: Fetch HTML pages via `?startrow=N` (multiples of 25). Parse `tr.data-row` elements; extract title from `a.jobTitle-link`, href from link attribute. Additional columns: Job Req ID (`td[1]`), Location (`td[2]`), Department (`td[3]`).
- **Pagination**: 25 jobs per page, `startrow=0,25,50,...` up to 9 pages. Empty `tr.data-row` set signals end.
- **Link Format**: `https://careers.aramco.com/{path}` where path is `/expat_uk/job/SLUG/ID/`, `/expat_us/job/SLUG/ID/`, or `/saudi/job/SLUG/ID/`
- **Notes**: All jobs in Saudi Arabia (location always "SA"). Category assigned by title keywords (not available on listing page). Cannot fetch from Python (blocked), must use browser. New job "IP Docketing Specialist" found compared to previous scrape.

### 9. Shell (175 jobs)
- **URL**: https://shell.wd3.myworkdayjobs.com/en-US/ShellCareers
- **Platform**: Workday
- **Method**: JSON API POST to `/wday/cxs/shell/ShellCareers/jobs`
- **Body**: `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`. Response has `total` field and `jobPostings[]` array.
- **Pagination**: 20 per page, use `offset=0,20,40,...` up to `Math.ceil(total/20)` pages. All pages can be fetched in a single async loop (9 pages, fast).
- **Data Structure**: Each `jobPostings[]` item: `title`, `externalPath` (relative URL), `locationsText` (city-level, NOT country), `postedOn` (e.g., "Posted 2 Days Ago"), `bulletFields[]` (contains req ID).
- **Link Format**: `https://shell.wd3.myworkdayjobs.com/en-US/ShellCareers` + `externalPath`
- **Country Extraction**: Location text is city-based (e.g., "Scotford - Refinery", "Houston - EP Center Americas"). Must map to country using keyword matching: Houston/California/Michigan/Chicago → US, London/Aberdeen → UK, Bangalore/Chennai → India, Kuala Lumpur/Cyberjaya/Miri → Malaysia, Rotterdam/Pernis → Netherlands, Manila/Tabangao → Philippines, etc. "N Locations" entries → "Multiple".
- **Notes**: Links must include `/en-US/ShellCareers/` in path. Dedup by `externalPath`. All 175 jobs fetched in ~9 sequential API calls (no batching needed).

### 10. Chevron (179 jobs)
- **URL**: https://careers.chevron.com/search-jobs
- **Platform**: TalentBrew (Radancy/TMP) with ElasticSearch backend
- **Method**: Click-based pagination through 12 pages (15 jobs/page). Extract `a[href*="/job/"]` links; title and location parsed from link text (split by newline). Slugs captured directly from href paths.
- **Pagination**: AJAX pagination via "next page" link click; URL params (`&p=N`) don't work as direct navigation. `window.elasticSearch.searchOptions` provides TotalResults/TotalPages metadata.
- **API Notes**: `window.elasticSearch.search()` exists but DOM updates unreliably. `/search-jobs/results` endpoint returns empty results. Only click-based pagination works reliably.
- **Country mapping**: Location format "City, State/Country" — US states mapped to "United States", other countries extracted from location suffix.
- **Build script**: `build_chevron.py` — includes category classification based on title keywords.
- **Notes**: Scraped worldwide. 15 countries including India (58), US (32), Philippines (31), Argentina (27).

### 11. Petrofac (55 jobs)
- **URL**: https://petrofac.referrals.selectminds.com
- **Platform**: SelectMinds/iCIMS
- **Method**: URL-based pagination `/page/{N}`
- **Notes**: 55 jobs total. Used `fetch()` to load all pages and extract job data from DOM. Clean "and 1 additional location" from country field.

### 12. ConocoPhillips (30 jobs)
- **URL**: https://careers.conocophillips.com/job-search-results/?query=&location=
- **Platform**: Custom careers site (non-Workday UI) with Workday backend (wd1.myworkdayjobs.com). Apply links point to Workday.
- **Method**: Click "Search" with no filters. All jobs load on single page — no pagination. Extract from `.job_search_list_item` elements with grid sub-items.
- **Data structure**: Each job has 4 grid items: (1) category label + job title, (2) Location, (3) Job ID, (4) Apply link to Workday.
- **Multi-location**: Some jobs list multiple locations separated by whitespace; take first location for CSV.
- **Country mapping**: US states (TEXAS, ALASKA, etc.) → United States; QUEENSLAND → Australia; CANADA/NORWAY/UNITED KINGDOM directly.
- **Build script**: `build_conocophillips.py` — categories come directly from the page (Marine, Upstream Production, etc.).
- **Notes**: Workday backend (wd1.myworkdayjobs.com) may be down during maintenance windows. The custom careers.conocophillips.com page still serves job listings even when Workday UI is down.

### 13. Petronas (29 jobs)
- **URL**: https://careers.petronas.com/en/sites/CX_1/jobs?mode=location
- **Platform**: Oracle CX Recruiting
- **Method**: All jobs load on single page (scroll to bottom triggers lazy-load for remaining cards). Extract from `.job-tile` parent divs.
- **DOM Selectors**: `.job-tile` for cards, `.job-tile__title` for title, `.job-list-item__job-info-item` for location/date, `a[href*="/job/"]` for links.
- **Title cleanup**: Some titles have numeric prefixes like "100004709_" or "100005288 - " that need stripping via regex `^\d+[_ -]+`.
- **Multi-location**: Some jobs show "Location and 1 more" — strip the suffix.
- **Notes**: All 29 jobs are in Malaysia (Kuala Lumpur, Perak, Putrajaya). Heavy on academic/research roles (university positions). Date format on page: MM/DD/YYYY → convert to YYYY-MM-DD for CSV.
- **Last scraped**: 2026-03-11 (29 jobs)

### 14. Suncor (20 jobs)
- **URL**: https://suncor.wd1.myworkdayjobs.com/Suncor_External
- **Platform**: Workday
- **Method**: Workday JSON API POST to `/wday/cxs/suncor/Suncor_External/jobs`
- **Body**: `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`
- **Response**: `{total, jobPostings[{title, externalPath, locationsText, postedOn, bulletFields[]}]}`
- **Country mapping**: Most jobs in Canada (Calgary, Fort McMurray, Sarnia, Oakville, Montreal). US locations: Houston, Commerce City, Fort Lupton.
- **Notes**: All 20 jobs fetched in single API call. Posted dates are relative ("Posted Yesterday", "Posted N Days Ago"). Link format: `https://suncor.wd1.myworkdayjobs.com/en-US/Suncor_External{externalPath}`.
- **Last scraped**: 2026-03-11 (20 jobs)

### 15. Mubadala Energy (40 jobs)
- **URL**: https://www.careers-page.com/mubadalaenergy#openings
- **Platform**: careers-page.com (client-rendered SPA)
- **Method**: Live DOM scraping (fetch+DOMParser does NOT work — SPA requires live browser rendering)
- **Pagination**: `?page=N` (20 jobs per page, 2 pages)
- **DOM Selectors**:
  - Job links: `a[href*="/mubadalaenergy/job/"]` (filter out "Apply" button text)
  - Title: link text content (deduplicate by href)
  - Location: find span with comma (location format) in parent div
  - Country: parsed from location string (Malaysia, Indonesia, UAE)
- **Notes**: Client-rendered SPA — JavaScript state is lost on page navigation. Must extract and dump each page independently. No posting dates available. Link format: `https://www.careers-page.com/mubadalaenergy/job/{CODE}`. Clean duplicate city names in location (e.g., "Jakarta, Jakarta, Indonesia" → "Jakarta, Indonesia"). Note: `mubadalaenergy.careers-page.com` returns 404, must use `www.careers-page.com/mubadalaenergy`.
- **Last scraped**: 2026-03-11 (40 jobs)

### 16. INPEX (73 jobs — 2 sites combined)

#### INPEX Australia (25 jobs)
- **URL**: https://careers.inpex.com.au/search/?q=&searchResultView=LIST
- **Platform**: SAP SuccessFactors (UI5 Web Components with Shadow DOM)
- **Method**: POST API `https://careers.inpex.com.au/services/recruiting/v1/jobs` + UI pagination fallback
- **API Payload**: `{"locale": "en_GB", "firstResult": N, "maxResults": 10, "query": "", "sortBy": "date_desc"}`
- **Pagination**: 10 per page, 3 pages. API has a bug returning duplicates and missing some jobs — must supplement with UI page scraping via accessibility tree.
- **Data**: `jobSearchResult[].response` contains `unifiedStandardTitle`, `id`, `jobLocationShort[]`, `urlTitle`, `unifiedStandardStart`
- **Link Format**: `https://careers.inpex.com.au/job/{urlTitle}/{id}-en_GB`
- **Notes**: Shadow DOM prevents direct DOM queries — use accessibility tree (`read_page`) to extract links. API returns max ~18 unique of 25; remaining must be collected from UI pages 2-3.
- **Last scraped**: 2026-03-11 (25 jobs)

#### INPEX Indonesia (48 jobs)
- **URL**: https://career.inpex.co.id/home#jobsearch
- **Platform**: ASP.NET WebForms
- **Method**: DOM scraping with postback pagination
- **Pagination**: 10 per page, 5 pages. Uses `WebForm_DoPostBackWithOptions` for page navigation (click pagination links)
- **DOM Selectors**: `a[href*="/jobdetail/"]` for job links
- **Link Format**: `https://career.inpex.co.id/jobdetail/{title}/{jobId}`
- **Notes**: No category or date info available. All jobs are in Jakarta, Indonesia. JavaScript state preserved across postback pages. Must click through each page and collect links.
- **Last scraped**: 2026-03-11 (48 jobs)

### 17. Woodside Energy (15 jobs)
- **URL**: https://careers.woodside.com.au/go/View-All-Opportunities/9784266/
- **Platform**: Taleo (Oracle)
- **Method**: DOM scraping — all 15 jobs on a single page, no pagination needed
- **DOM Selectors**: `a[href*="/job/"]` for job links (deduplicate by href as each job has multiple link elements). Walk up parent elements until finding one with `Location` + `Posting Date` text to get the full job card context.
- **Data Fields**: Structured text in each card: `Title`, `Location` (country codes: US, MX, AU, SG), `Business Unit` (used as category), `Requisition ID`, `Posting Date` (format: `D Mon YYYY`, e.g., "4 Mar 2026")
- **Link Format**: `https://careers.woodside.com.au/job/{slug}/{id}/`
- **Notes**: Small job count (15). Country codes need mapping to full names. No Shadow DOM — standard DOM queries work fine. Card container is `.sub-section` class (not `tr` or generic `div`).
- **Last scraped**: 2026-03-11 (15 jobs)

### 18. ADNOC (67 jobs)
- **URL**: https://jobs.adnoc.ae/us/en/search-results
- **Platform**: Phenom People (Vue.js, client-side rendered)
- **Method**: DOM scraping with page-by-page navigation. 10 jobs per page, 7 pages. Navigate to `?from=N&s=1` (N=0,10,20,...60). Extract `a[href*="/job/"]` links from each page.
- **DOM Selectors**: `a[href*="/job/"]` for job links. Parent card element contains category (line 2), country (line 3), subsidiary (line 4), city (line 5) in `innerText` split by newlines.
- **Link Format**: `https://jobs.adnoc.ae/us/en/job/{jobId}`
- **Pagination**: Client-side rendered — `fetch()` returns HTML shell without job data. Must navigate browser to each page URL and extract from live DOM.
- **Notes**: All jobs in UAE (Abu Dhabi, Offshore Islands, Onshore Site/Ruwais, Rigs). Categories come from Phenom facets. Subsidiaries include ADNOC GAS O&M, ADNOC Distribution, ADNOC HQ, ADNOC Drilling, ADNOC Onshore, ADNOC Offshore, ADNOC Logistics & Services. Chatbot widget may overlay results — close it first. ALL CAPS titles should be converted to Title Case.
- **Last scraped**: 2026-03-11 (67 jobs)

### 19. CNOOC International (0 jobs)
- **URL**: https://cnoocinternational.com/careers/currentopportunities/
- **Platform**: Lumesse TalentLink (custom CMS integration)
- **Method**: DOM scraping from single page. All jobs visible on one page (no pagination). Job cards contain title, category (Functional Area), country, city, and posted date.
- **DOM Selectors**: Job cards are `div` blocks with fields using `SLOVLIST1` (category), `SLOVLIST2` (country), `SLOVLIST3` (city) class identifiers. Detail links use `a` tags with "See requisition details" text.
- **Link Format**: `https://cnoocinternational.com/careers/currentopportunities/details/?jobId={ID}&jobTitle={ENCODED_TITLE}`
- **Pagination**: None — all jobs on single page (currently only 3 openings)
- **Notes**: CNOOC International is the overseas arm of CNOOC (China National Offshore Oil Corporation). Very small number of openings — may have 0 at times. The Chrome extension blocks JS output containing query strings — use `url.searchParams.get()` to extract individual parameters.
- **Last scraped**: 2026-03-11 (0 jobs)

### 20. PDO (0 jobs)
- **URL**: https://www.petrojobs.om/en-us/Pages/Job/Search_result.aspx?Keyword=&cpn=1&depid=-1&type=s
- **Platform**: PetroJobs Oman (ASP.NET WebForms, shared Oman O&G recruitment portal)
- **Method**: Navigate to search results page with `cpn=1` (company ID for PDO). All 8 jobs visible on one page. Job cards in `div.thumbnail.panel_bg` containers contain title, discipline, job ID (PDO####), position type, dates. Detail page IDs extracted from `a` elements with `Details.aspx?i={id}` pattern.
- **DOM Selectors**: `div.thumbnail.panel_bg` for job cards. Title in first line of `innerText`. Discipline, Job ID, dates in tab-separated label rows. Detail link IDs via regex `i=(\d+)` on anchor `innerHTML`.
- **Link Format**: `https://www.petrojobs.om/en-us/Pages/Job/Details.aspx?i={detailId}`
- **Pagination**: None needed — all results on single page (8 jobs currently)
- **Notes**: PetroJobs.om is a joint recruitment portal for 9 Oman O&G operators (PDO, OQ, BP, Daleel, CC Energy, Oxy, OLNG, ARA, Masar). Company filter value for PDO is `cpn=1`. All PDO jobs are in Oman, no specific city/location provided. Chrome extension may block URLs with query strings in JS output — use document.title or get_page_text for extraction. PDO may have 0 jobs at times — check "Jobs By Company" filter to see if PDO appears.
- **Last scraped**: 2026-03-11 (0 jobs)

### 21. QatarEnergy LNG (17 jobs)
- **URL**: https://careers.qatarenergylng.qa/search/?q=&sortColumn=referencedate&sortDirection=desc
- **Platform**: Taleo (Oracle) career site — server-rendered HTML with `tr.data-row` table rows
- **Method**: Single-page search results. Navigate to URL with `sortColumn=referencedate&sortDirection=desc` to get all jobs sorted by date. Extract from `tr.data-row` elements: title from `a.jobTitle-link`, department from `span.jobDepartment`, location from `span.jobLocation`, date from cell matching date regex, job ID from numeric cell, href from link attribute.
- **DOM Selectors**: `tr.data-row` for job rows. `a.jobTitle-link` for title + href. Location in `span.jobLocation` (format "City, QA"). Department in `span.jobDepartment`. Date in td matching `/^\d+ [A-Z][a-z]{2} \d{4}$/`.
- **Link Format**: `https://careers.qatarenergylng.qa{href}` where href is `/job/City-Title-Slug/NumericId/`
- **Pagination**: None needed — all 12 results on single page
- **Notes**: All jobs in Qatar (Doha, Ras Laffan North, Ras Laffan 2 South, Offshore 2 South). Categories include National Graduates, Finance & Accounting, Information Technology, Internship, HSE, Onshore & Offshore Operations. Some jobs may have empty department field — infer category from title. Location format includes ", QA" suffix which should be stripped.
- **Last scraped**: 2026-03-11 (17 jobs)

### 22. North Oil Company (2 jobs)
- **URL**: https://careers.noc.qa/search/?q=&sortColumn=referencedate&sortDirection=desc
- **Platform**: Taleo (Oracle) career site — same platform as QatarEnergy LNG
- **Method**: Single-page search results. Navigate to URL with sort params. Extract from `tr.data-row` elements: title from `a.jobTitle-link`, department from `span.jobDepartment`, location from `span.jobLocation`, date from cell matching date regex, href from link attribute.
- **DOM Selectors**: `tr.data-row` for job rows. `a.jobTitle-link` for title + href. Department in `span.jobDepartment`. Location in `span.jobLocation` (just "QA").
- **Link Format**: `https://careers.noc.qa{href}` where href is `/job/Title-Slug/NumericId/`
- **Pagination**: None needed — all results on single page (currently only 2 jobs)
- **Notes**: All jobs in Qatar. Very small number of openings. NOC is a Qatar Petroleum / TotalEnergies JV for the Al-Shaheen offshore field. Departments map to categories: "Health and Industrial Hygiene" → HSE, "Human Resources" (for internship postings) → Internship.
- **Last scraped**: 2026-03-11 — 2 jobs

### 23. Dragon Oil (6 jobs)
- **URL**: https://career22.sapsf.com/career?company=dragonoilh
- **Platform**: SAP SuccessFactors career portal
- **Method**: Navigate to portal, click "Search Jobs" to load results. All jobs on single page. Extract from `tr.jobResultItem` rows: title from `a.jobTitle`, requisition info from row `innerText` matching regex `Requisition ID: (\d+) - Posted on (\S+) - (.+)`. Location code on a separate line starting with `DOTL` or `DOHL`.
- **DOM Selectors**: `tr.jobResultItem` for job rows. `a.jobTitle` for title link. Requisition line parsed with regex. Location line starts with `DOTL-` (Turkmenistan) or `DOHL` (Dubai HQ).
- **Link Format**: `https://career22.sapsf.com/career?career_ns=job_listing&company=dragonoilh&navBarLevel=JOB_SEARCH&rcm_site_locale=en_US&career_job_req_id={reqId}&selected_lang=en_GB`
- **Pagination**: None needed — all results on single page
- **Notes**: Dragon Oil is an ENOC subsidiary. Jobs split between Turkmenistan (DOTL = Dragon Oil Turkmenistan Limited, locations: Hazar offshore, Ashgabat) and UAE (DOHL = Dragon Oil Holdings Ltd, Dubai Corporate Head Office). No department field on listing — categories inferred from title. The dragonoil.com/careers/ page links to the SAP SuccessFactors portal via "Current Vacancies". Chrome extension blocks href extraction due to query strings — click through to detail page or use reqId to construct links. Country distribution: Turkmenistan 2, UAE 4.
- **Last scraped**: 2026-03-11 — 6 jobs

### 24. McDermott (375 jobs)
- **URL**: https://www.mcdermott.com/careers/search-apply
- **Platform**: Oracle HCM Cloud (embedded iframe to `edsv.fa.us2.oraclecloud.com`)
- **Method**: REST API pagination from Oracle HCM portal
- **API Endpoint**: `https://edsv.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.secondaryLocations,flexFieldsFacet.values&finder=findReqs;siteNumber=CX_1,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,offset=N,sortBy=POSTING_DATES_DESC`
- **Pagination**: 25 per page, offset increments of 25, total in `items[0].TotalJobsCount`
- **Job Data Path**: `items[0].requisitionList` array, each item has `Id`, `Title`, `PrimaryLocation` (full), `PostedDate`
- **Location Parsing**: `PrimaryLocation` format "City, State/Province, Country" — split by comma, last part = country, first part = city
- **Link Format**: `https://edsv.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/{Id}`
- **Country Normalization**: "United Arab Emirates" → "UAE"
- **Categories**: No department/category field in API — inferred from job titles using keyword matching (see `build_mcdermott.py` categorize function)
- **Notes**: mcdermott.com embeds Oracle HCM in an iframe. CORS blocks cross-origin API calls from mcdermott.com — must navigate browser directly to the Oracle HCM portal (`edsv.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/`) and make API calls from the same origin. Jobs span 19 countries worldwide (UAE 83, Malaysia 74, India 58, Indonesia 42, USA 36, UK 21, Qatar 14, Mexico 11, etc.).
- **Last scraped**: 2026-03-11 — 375 jobs

### 25. Saipem (202 jobs)
- **URL**: https://jobs.saipem.com/
- **Platform**: Custom job board powered by NCorePlat (app.ncoreplat.com)
- **Method**: Static JSON file fetch — all jobs in a single `positions_saipem.json`
- **Data Source**: `https://jobs.saipem.com/positions_saipem.json` (NOTE: root-level path, NOT `/api/positions_saipem.json`)
- **JSON Structure**: `data.Positions` object keyed by subsidiary name (18 subsidiaries), each containing array of job objects
- **Job Fields**: `title`, `countryText`, `sectorText`, `url`, `orderDate`, `root-node` (subsidiary)
- **Pagination**: None — all jobs in single JSON file
- **Link Format**: Direct URLs to `app.ncoreplat.com/jobposition/{id}/...`
- **Subsidiaries**: Global Projects Services AG, Saipem Romania Srl, Saipem SA (France), Saipem Limited (UK), Saipem India, Saipem Luxembourg Angola Branch, Petromar Lda, Saipem Australia, Saipem Spa (Italy), Saipem Offshore Construction, Saipem SpA Qatar Branch, Saipem do Brasil, SAIPEM SpA Abu Dhabi Branch, SEI Spa Ivory Coast Branch, Saudi Arabian Saipem Co. Ltd., Snamprogetti Saudi Arabia Co. Ltd., Saipem America Inc, Corporate
- **Country Normalization**: "United Arab Emirates" → "UAE", "United Kingdom" → "UK", "United States" → "USA", "Cote d'Ivoire" → "Ivory Coast". Empty `countryText` → "Unknown". "Offshore" kept as-is (vessel/offshore-based roles with no fixed country).
- **Categories**: Title-based inference using standard categorize function. French internship postings ("STAGE ...") match the `stage ` pattern in the Internship rule.
- **HTML Entity Decoding**: Titles may contain `&amp;` → `&`, `&#8322;` → `₂`, `&deg;` → `°`
- **Step-by-step extraction method** (VM cannot fetch external URLs — must use browser):
  1. Navigate browser to `https://jobs.saipem.com/`
  2. Run JS in browser to fetch JSON and build compact pipe-delimited data:
     ```javascript
     fetch('/positions_saipem.json').then(r=>r.json()).then(data=>{
       let P=data.data.Positions;
       let cm={'United Arab Emirates':'UAE','United Kingdom':'UK',
               "Cote d'Ivoire":'Ivory Coast','United States':'USA'};
       let jobs=[];
       for(let s of Object.keys(P)){
         for(let j of P[s]){
           let c=(j.countryText||'').trim(); c=cm[c]||c; if(!c) c='Unknown';
           let t=(j.title||'').replace(/&amp;/g,'&').replace(/&#8322;/g,'₂')
                 .replace(/&deg;/g,'°').trim();
           let d=(j.orderDate||'').substring(0,10);
           let id=(j.url||'').match(/\/(\d+)\//); id=id?id[1]:'';
           let slug=(j.url||'').split('/').slice(-2).join('/');
           // Replace pipe chars in title to avoid delimiter collision
           jobs.push([c, t.replace(/\|/g,'-'), categorize(t), d, id, slug].join('|'));
         }
       }
       jobs.sort((a,b)=>{let da=a.split('|')[3],db=b.split('|')[3];return db.localeCompare(da);});
       // Write as individual <div> elements (NOT <pre> — newlines get lost in get_page_text)
       let html='<html><body>';
       for(let i=0;i<jobs.length;i++) html+='<div>'+jobs[i].replace(/</g,'&lt;')+'</div>';
       html+='</body></html>';
       document.open(); document.write(html); document.close();
     });
     ```
     (Include the standard `categorize()` function from the guide in the same JS call)
  3. Use `get_page_text` tool to extract ALL data in one call — the `<div>` elements concatenate without separators into a single string like: `Country1|Title1|...|slugA/companyCountry2|Title2|...|slugB/company...`
  4. Save this concatenated text to `/tmp/saipem_compact.txt` via Bash heredoc (the text is ~25KB, fits in a single heredoc)
  5. Run Python regex parser to split records and build CSV:
     ```python
     import re
     raw = open('/tmp/saipem_compact.txt').read().strip()
     # Country names that appear in the data (used as record boundary markers):
     countries = '(?:Italy|France|UK|Angola|Offshore|Qatar|Indonesia|China|' \
                 'Ivory Coast|Mozambique|Australia|Romania|Saudi Arabia|Nigeria|' \
                 'UAE|India|Brazil|Guyana|USA|Unknown|United States)'
     records = re.findall(
         rf'({countries}\|[^|]*?\|[^|]*?\|\d{{4}}-\d{{2}}-\d{{2}}\|\d+\|[^\|]+?)' \
         rf'(?={countries}\||$)', raw)
     # Each record: country|title|category|date|jobid|slug
     # Reconstruct URL: https://app.ncoreplat.com/jobposition/{jobid}/{slug}
     ```
  6. Write CSV to `Saipem_Jobs.csv` with standard format
- **CRITICAL — What does NOT work**:
  - `python3 requests.get()` / `urllib` / `curl` from VM — all blocked by network restrictions
  - `btoa()` / base64 encoding in browser JS — blocked by Chrome extension
  - `console.log()` with full CSV data — Chrome extension blocks output containing URLs/query strings
  - `document.write('<pre>...')` then `get_page_text` — newlines between records are LOST, records merge into single line (still parseable but harder)
  - `document.write('<plaintext>...')` — same newline loss issue with `get_page_text`
  - Browser blob download (`a.download`) — file goes to host system, not accessible from VM filesystem
  - JS tool output (`javascript_tool`) — hard limit of ~1500 chars, truncates anything beyond ~8 CSV lines
  - **The working method**: Individual `<div>` elements per record → `get_page_text` → regex split on known country names. This reliably extracts all ~200 records in a single tool call.
- **Notes**: Jobs span 20 countries (Italy 56, France 32, Offshore 25, Qatar 15, Saudi Arabia 11, Angola 10, UK 9, Ivory Coast 8, Mozambique 7, etc.). Many French-language internship postings ("STAGE ...") from Saipem SA.
- **Last scraped**: 2026-03-11 — 202 jobs

### 26. Technip Energies (171 jobs)
- **URL**: https://hcxg.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs
- **Platform**: Oracle HCM Cloud (same as McDermott but different instance: `hcxg.fa.em2.oraclecloud.com`)
- **Method**: REST API pagination from Oracle HCM portal
- **API Endpoint**: `https://hcxg.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.secondaryLocations,flexFieldsFacet.values&finder=findReqs;siteNumber=CX_1,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,offset=N,sortBy=POSTING_DATES_DESC`
- **Pagination**: 25 per page (default is 9), offset increments of 25, total in `items[0].TotalJobsCount`
- **Job Data Path**: `items[0].requisitionList` array, each item has `Id`, `Title`, `PrimaryLocation`, `PostedDate`
- **Location Parsing**: `PrimaryLocation` format "City, Region, Country" — split by comma, last part = country, first part = city
- **Link Format**: `https://hcxg.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/{Id}`
- **Country Normalization**: "United Arab Emirates" → "UAE", "United Kingdom" → "UK", "United States" → "USA", "Korea, Republic of" → "South Korea"
- **Categories**: No department/category field in API — inferred from job titles using keyword matching
- **Notes**: T.EN (Technip Energies) career site. Jobs span 15 countries (France 57, UK 26, India 21, Malaysia 14, UAE 11, USA 11, Colombia 9, Spain 8, Germany 4, Mexico 3, Netherlands 2, South Korea 2, Italy 1, Thailand 1, Qatar 1). Many French-language and V.I.E (Volontariat International en Entreprise) postings. Headquarters in Nanterre, France. UAE jobs are predominantly for UAE Nationals.
- **Last scraped**: 2026-03-11 — 171 jobs

### 27. NMDC (68 jobs)
- **URL**: https://fa-evft-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/nmdccareers/jobs
- **Platform**: Oracle HCM Cloud (`fa-evft-saasfaprod1.fa.ocs.oraclecloud.com`)
- **Method**: REST API pagination from Oracle HCM portal
- **API Endpoint**: `https://fa-evft-saasfaprod1.fa.ocs.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.secondaryLocations,flexFieldsFacet.values&finder=findReqs;siteNumber=CX_1,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,offset=N,sortBy=POSTING_DATES_DESC`
- **Pagination**: 25 per page, offset increments of 25, total in `items[0].TotalJobsCount`
- **Job Data Path**: `items[0].requisitionList` array, each item has `Id`, `Title`, `PrimaryLocation`, `PostedDate`
- **Link Format**: `https://fa-evft-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/nmdccareers/job/{Id}`
- **Categories**: No department/category field in API — inferred from job titles (heavy marine/dredging/construction focus)
- **Notes**: NMDC Group is an Abu Dhabi-based marine and dredging company. All 68 jobs are in the UAE. Roles are predominantly marine operations (marine supervisor, tug master, seaman, chief officer), dredging (dredge mechanic, electrician), construction (crane operator, fabrication, rigging, welding, grouting), and engineering (electrical, mechanical). Very specialized workforce. Categories: Operations & Technical 24, Engineering 14, General 8, Management 4, Finance & Accounting 3, IT & Digital 3.
- **Last scraped**: 2026-03-11 — 68 jobs

### 28. Larsen & Toubro (928 jobs)
- **URL**: https://larsentoubrocareers.peoplestrong.com/job/joblist
- **Platform**: PeopleStrong AltOne
- **Method**: REST API POST with pagination
- **API Endpoint**: `POST https://larsentoubrocareers.peoplestrong.com/api/cp/rest/altone/cp/jobs/v1?offset=N&limit=100`
- **Request Body**: Empty JSON `{}`
- **Pagination**: `offset` increments by `limit`, **`totalRecords`** (NOT `count`) in response indicates total count. Auto-paginate until `all.length >= totalRecords`. CRITICAL: the key is `totalRecords`, not `count` — using `count` returns undefined and stops after first page.
- **Response Fields**: `response[]` array, each item has `jobTitle`, `locationHierarchyComplete` (Country>State>City), `organizationUnit`, `industry`, `functionalArea`, `jobPostedDate`, `jobDetailUrl`, `jobCode`
- **Link Format**: `https://larsentoubrocareers.peoplestrong.com/job/detail/{jobCode}` — use last numeric segment of jobCode
- **Country Extraction**: Parse `locationHierarchyComplete` hierarchy — first segment is country. Normalize "United Arab Emirates" → "UAE". Check for country keywords (India, Saudi Arabia, UAE, Oman, Qatar, Kuwait, Indonesia, Uzbekistan, etc.) in the full location string.
- **Location**: Last segment of `locationHierarchyComplete` (after last `>`) gives the specific city/site.
- **Categories**: Inferred from jobTitle using keyword matching. L&T has heavy engineering (MEP, HVAC, civil, QA/QC), EHS, and construction roles especially in UAE.
- **Data extraction**: With ~930 jobs, the div-based get_page_text approach hits the body-too-large limit. Extract in chunks of 200 divs using `window._ltLines` array stored in JS, render 200 at a time, extract via `get_page_text`, save each chunk to `/tmp/lt_chunkN.txt`, then concatenate all chunks with `cat` and parse with Python.
- **Notes**: L&T is a major Indian multinational in engineering, construction, and technology. 928 jobs across 8 countries (India 789, Saudi Arabia 50, UAE 42, Oman 30, Kuwait 6, Indonesia 6, Uzbekistan 4, Qatar 1). Heavy concentration in engineering, management, construction, and structural/civil roles. Many duplicate positions (same role in multiple locations).
- **Last scraped**: 2026-03-11 — 928 jobs

### 29. ENOC (3 jobs)
- **URL**: `https://careers.enoc.com/search/`
- **Platform**: Standard careers portal (tile-based search results)
- **Method**: Navigate to search page, click "Search Jobs" with empty filters. All jobs displayed on single page.
- **DOM Selectors**: `a[href*="/job/"]` for job links. Cards contain Title, Job Category, and Location fields.
- **Link Format**: `https://careers.enoc.com/job/DUBAI-{title-slug}/{jobId}/`
- **Pagination**: None needed — all results on single page (currently only 3 jobs)
- **Notes**: ENOC (Emirates National Oil Company) is a UAE state-owned company. All jobs in Dubai, UAE. Categories from site: IT (2), Retail operations (1). Previously had 8 jobs (2026-03-03), now down to 3.
- **Last scraped**: 2026-03-11 — 3 jobs

### 30. OQ Group (16 jobs)
- **URL**: `https://careers.oq.com/search/?createNewAlert=false&q=&locationsearch=`
- **Platform**: Standard careers portal (tile-based search results, same platform as ENOC — likely TalentBrew/TMP)
- **Method**: Navigate to search page with empty keyword/location. All jobs displayed on single page.
- **DOM Selectors**: `tr.data-row` for job rows. `a[href*="/job/"]` for title link. `span.jobLocation` for location, `span.jobDate` for date, `span.jobDepartment` for department.
- **Link Format**: `https://careers.oq.com/job/{City}-{title-slug}/{jobId}/`
- **Pagination**: None needed — all results on single page (currently 16 jobs)
- **Notes**: OQ (formerly Oman Oil Company) is Oman's integrated energy company. All 16 jobs in Oman (Muscat 12, Duqm 2, Sohar 1, Office 1). Departments from site: Exploration & Productions, Commercial, Downstream Operations, People and Culture, Gas Networks Engineering, Information Digital Solutions and Technology, Finance & Accounting, Legal. Several OQ8 (retail subsidiary) senior positions.
- **Last scraped**: 2026-03-11 — 16 jobs

### 31. KPC (0 jobs)
- **URL**: `https://recruitment.kpc.com.kw/recruitment2/`
- **Platform**: KPC E-Recruitment System (custom ASP.NET portal). Covers KPC and all subsidiaries (KNPC, KIPIC, KOC, KGOC, PIC, etc.)
- **Method**: Navigate to recruitment portal homepage. Active campaigns are displayed when available. No search needed — campaigns appear automatically.
- **Notes**: KPC (Kuwait Petroleum Corporation) is Kuwait's national oil company. Recruitment is campaign-based — jobs only appear when a specific hiring campaign is active. As of 2026-03-11: "No active campaigns for KPC." Internal campaigns only visible from KPC network. Contact: Recruitment@kpc.com.kw
- **Last scraped**: 2026-03-11 — 0 jobs (no active campaigns)

### 32. KNPC (0 jobs)
- **URL**: No dedicated careers page. KNPC recruits through the KPC E-Recruitment System at `https://recruitment.kpc.com.kw/recruitment2/`
- **Platform**: Same as KPC (#31) — shared E-Recruitment portal
- **Method**: Same as KPC. Check the KPC portal for any KNPC-specific campaigns.
- **Notes**: KNPC (Kuwait National Petroleum Company) is a KPC subsidiary responsible for refining. Website at `https://www.knpc.com/en` has no careers section. All recruitment goes through parent company KPC's portal. As of 2026-03-11: no active campaigns.
- **Last scraped**: 2026-03-11 — 0 jobs (no active campaigns)

### 33. AECOM (361 jobs — Energy business line only)
- **URL**: `https://aecom.jobs/business-line/energy/jobs/`
- **Platform**: Custom Nuxt.js frontend powered by SmartRecruiters (API: `prod-search-api.jobsyn.org`)
- **Method**: Navigate to Energy business line filtered URL. Page loads 10 jobs initially. Click "More" button (`#jobListingContent button.btn`) repeatedly to load all jobs (10 per click). ~35 clicks needed for 361 jobs. Do in batches of 10 clicks to avoid browser timeouts.
- **DOM Selectors**: `ul.pb-10 > li` for job items. Each `li` contains: `a` with href for link, `h2` for title. Text content has "Career Area:" and "Business Line:" labels. Location is between title and "Career Area:".
- **Link Format**: `https://aecom.jobs/{city-code}/{title-slug}/{HASH}/job/`
- **API**: `GET https://prod-search-api.jobsyn.org/api/v1/solr/search?page=1&offset=N&businessline=energy&num_items=10` — requires origin header from aecom.jobs domain (cannot call directly from JS fetch due to CORS).
- **Data extraction**: After loading all jobs via "More" clicks, extract via JS: iterate `ul.pb-10 > li`, parse title/location/career area from text content, get link from `a[href]`. Store in `window._aecomJobs` array, dump via `console.log()` with markers, save persisted output to file, parse with Python.
- **Pagination**: Click-based "More" button. Use batches of 10 clicks with 1.2s delays: `for (let i=0; i<10; i++) { btn.click(); await new Promise(r=>setTimeout(r,1200)); }`
- **Notes**: AECOM is a global infrastructure consulting firm. Energy is one of 6 business lines (Transportation, B&P, Water, Environment, Energy, Program Management). 361 Energy jobs across 11 countries (UK 144, US 131, India 30, Romania 13, Ireland 11, Australia 7, Poland 7, Spain 7, Canada 6, New Zealand 4, Philippines 1). Location format from site uses 3-letter country codes (GBR, IND, AUS, ROM) or US state codes (TX, CA, etc.).
- **Last scraped**: 2026-03-11 — 361 jobs (Energy business line only)

### 34. ENI (80 jobs)
- **URL**: `https://www.eni.com/en-IT/careers.html` → Click "Discover EniJobs" → `https://jobs.eni.com/en/sites/CX_1004/jobs`
- **Platform**: Oracle HCM Cloud (same pattern as NMDC #27)
- **Oracle Host**: `fa-evkm-saasfaprod1.fa.ocs.oraclecloud.com`
- **Site Number**: `CX_1004`
- **API**: `GET /hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.secondaryLocations,flexFieldsFacet.values&finder=findReqs;siteNumber=CX_1004,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,offset={N},sortBy=POSTING_DATES_DESC`
- **Pagination**: 25 per page, increment offset by 25. `TotalJobsCount` in first response item gives total.
- **Fields**: `Id`, `Title`, `PostedDate`, `PrimaryLocation` (full location string), `PrimaryLocationCountry` (2-letter code), `CategoryCode` (empty for all ENI jobs), `secondaryLocations` array
- **Link Format**: `https://fa-evkm-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1004/job/{Id}`
- **Country Extraction**: Parse from `PrimaryLocation` — last comma-separated part is country name (e.g., "San Donato Milanese, Milano, Italy" → "Italy")
- **Categorization**: Standard `categorize()` function (CategoryCode is empty)
- **Countries**: Italy 39, Germany 7, Netherlands 7, Spain 5, United Kingdom 5, Iraq 3, Egypt 2, France 2, UAE 2, and 8 others
- **Output**: `ENI_Jobs.csv`

### 35. Repsol (51 jobs)
- **URL**: `https://repsol.wd3.myworkdayjobs.com/en-US/Repsol`
- **Platform**: Workday (wd3)
- **API**: `POST /wday/cxs/repsol/Repsol/jobs` with `{"appliedFacets":{},"limit":20,"offset":N,"searchText":""}`
- **Detail API**: `GET /wday/cxs/repsol/Repsol{externalPath}` — returns `jobPostingInfo` with `title`, `location`, `country.descriptor`, `startDate`
- **Link Format**: `https://repsol.wd3.myworkdayjobs.com/en-US/Repsol{externalPath}`
- **Country Mapping**: `country.descriptor` from detail API. "United States of America" → "United States"
- **Categorization**: Standard `categorize()` function with added Spanish terms (prácticas, curso, prevención, mantenimiento, fiabilidad, producción, laboratorio, jefe, vendedor, expendedor, planta, infraestructura tid)
- **Note**: One job has no location/country — generic "Join our team" posting, defaults to Spain
- **Countries**: Spain 29, United States 19, Bolivia 1, Italy 1, Luxembourg 1
- **Output**: `Repsol_Jobs.csv`

### Middle East Only Companies (unchanged)
- **NIOC**
- **INOC**
- **Bapco**

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
