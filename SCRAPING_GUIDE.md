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

### 7. QatarEnergy (284 jobs)
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

### 9. Shell (181 jobs)
- **URL**: https://shell.wd3.myworkdayjobs.com/ShellCareers
- **Platform**: Workday
- **Method**: JSON API POST to `/wday/cxs/shell/ShellCareers/jobs`
- **Body**: `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`
- **Notes**: Links must include `/ShellCareers/` in path (e.g., `myworkdayjobs.com/ShellCareers/job/...`). Workday was intermittently down for maintenance.

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

### 13. Petronas (30 jobs)
- **URL**: https://careers.petronas.com/en/sites/CX_1/jobs?mode=location
- **Platform**: Oracle CX Recruiting
- **Method**: All jobs load on single page (scroll to bottom triggers lazy-load for remaining cards). Extract from `.job-tile` parent divs; the `a[href*="/job/"]` links inside are empty — data is in the parent div's `innerText`.
- **Data structure**: Each tile shows title (first line), location + posting date (second line, format "Location Posting DateMM/DD/YYYY"), and optional TRENDING badge.
- **Title cleanup**: Some titles have numeric prefixes like "100004709_" or "100005288 - " that need stripping via regex `^\d+[_ -]+`.
- **Multi-location**: Some jobs show "Location and 1 more" — strip the suffix.
- **Build script**: `build_petronas.py` — categories classified by title keywords. All jobs currently in Malaysia.
- **Notes**: All 30 jobs are in Malaysia (Kuala Lumpur, Perak, Putrajaya). Heavy on academic/research roles (university positions).

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

### 16. INPEX (72 jobs — 2 sites combined)

#### INPEX Australia (24 jobs)
- **URL**: https://careers.inpex.com.au/search/?q=&searchResultView=LIST
- **Platform**: SAP SuccessFactors (UI5 Web Components with Shadow DOM)
- **Method**: POST API `https://careers.inpex.com.au/services/recruiting/v1/jobs` + UI pagination fallback
- **API Payload**: `{"locale": "en_GB", "firstResult": N, "maxResults": 10, "query": "", "sortBy": "date_desc"}`
- **Pagination**: 10 per page, 3 pages. API has a bug returning duplicates and missing some jobs — must supplement with UI page scraping via accessibility tree.
- **Data**: `jobSearchResult[].response` contains `unifiedStandardTitle`, `id`, `jobLocationShort[]`, `urlTitle`, `unifiedStandardStart`
- **Link Format**: `https://careers.inpex.com.au/job/{urlTitle}/{id}-en_GB`
- **Notes**: Shadow DOM prevents direct DOM queries — use accessibility tree (`read_page`) to extract links. API returns max ~17 unique of 24; remaining must be collected from UI pages 2-3.

#### INPEX Indonesia (48 jobs)
- **URL**: https://career.inpex.co.id/home#jobsearch
- **Platform**: ASP.NET WebForms
- **Method**: DOM scraping with postback pagination
- **Pagination**: 10 per page, 5 pages. Uses `WebForm_DoPostBackWithOptions` for page navigation (click pagination links)
- **DOM Selectors**: `a[href*="/jobdetail/"]` for job links
- **Link Format**: `https://career.inpex.co.id/jobdetail/{title}/{jobId}`
- **Notes**: No category or date info available. All jobs are in Jakarta, Indonesia. JavaScript state preserved across postback pages. Must click through each page and collect links.

### 17. Woodside Energy (14 jobs)
- **URL**: https://careers.woodside.com.au/go/View-All-Opportunities/9784266/
- **Platform**: Taleo (Oracle)
- **Method**: DOM scraping — all 14 jobs on a single page, no pagination needed
- **DOM Selectors**: `a[href*="/job/"]` for job links (deduplicate by href as each job has multiple link elements). Walk up parent elements until finding one with `Location` + `Posting Date` text to get the full job card context.
- **Data Fields**: Structured text in each card: `Title`, `Location` (country codes: US, MX, AU, SG), `Business Unit` (used as category), `Requisition ID`, `Posting Date` (format: `D Mon YYYY`, e.g., "4 Mar 2026")
- **Link Format**: `https://careers.woodside.com.au/job/{slug}/{id}/`
- **Notes**: Small job count (14). Country codes need mapping to full names. No Shadow DOM — standard DOM queries work fine.

### 18. ADNOC (63 jobs)
- **URL**: https://jobs.adnoc.ae/us/en/search-results
- **Platform**: Phenom People (Vue.js, client-side rendered)
- **Method**: DOM scraping with page-by-page navigation. 10 jobs per page, 7 pages. Navigate to `?from=N&s=1` (N=0,10,20,...60). Extract `a[href*="/job/"]` links from each page.
- **DOM Selectors**: `a[href*="/job/"]` for job links. Parent card element contains category (line 2), country (line 3), subsidiary (line 4), city (line 5) in `innerText` split by newlines.
- **Link Format**: `https://jobs.adnoc.ae/us/en/job/{jobId}`
- **Pagination**: Client-side rendered — `fetch()` returns HTML shell without job data. Must navigate browser to each page URL and extract from live DOM.
- **Notes**: All jobs in UAE (Abu Dhabi, Offshore Islands, Onshore Site/Ruwais, Rigs). Categories come from Phenom facets. Subsidiaries include ADNOC GAS O&M, ADNOC Distribution, ADNOC HQ, ADNOC Drilling, ADNOC Onshore, ADNOC Offshore, ADNOC Logistics & Services. Chatbot widget may overlay results — close it first.

### 19. CNOOC International (3 jobs)
- **URL**: https://cnoocinternational.com/careers/currentopportunities/
- **Platform**: Lumesse TalentLink (custom CMS integration)
- **Method**: DOM scraping from single page. All jobs visible on one page (no pagination). Job cards contain title, category (Functional Area), country, city, and posted date.
- **DOM Selectors**: Job cards are `div` blocks with fields using `SLOVLIST1` (category), `SLOVLIST2` (country), `SLOVLIST3` (city) class identifiers. Detail links use `a` tags with "See requisition details" text.
- **Link Format**: `https://cnoocinternational.com/careers/currentopportunities/details/?jobId={ID}&jobTitle={ENCODED_TITLE}`
- **Pagination**: None — all jobs on single page (currently only 3 openings)
- **Notes**: CNOOC International is the overseas arm of CNOOC (China National Offshore Oil Corporation). Currently all jobs are in Calgary, Canada. Very small number of openings. The Chrome extension blocks JS output containing query strings — use `url.searchParams.get()` to extract individual parameters.

### 20. PDO (8 jobs)
- **URL**: https://www.petrojobs.om/en-us/Pages/Job/Search_result.aspx?Keyword=&cpn=1&depid=-1&type=s
- **Platform**: PetroJobs Oman (ASP.NET WebForms, shared Oman O&G recruitment portal)
- **Method**: Navigate to search results page with `cpn=1` (company ID for PDO). All 8 jobs visible on one page. Job cards in `div.thumbnail.panel_bg` containers contain title, discipline, job ID (PDO####), position type, dates. Detail page IDs extracted from `a` elements with `Details.aspx?i={id}` pattern.
- **DOM Selectors**: `div.thumbnail.panel_bg` for job cards. Title in first line of `innerText`. Discipline, Job ID, dates in tab-separated label rows. Detail link IDs via regex `i=(\d+)` on anchor `innerHTML`.
- **Link Format**: `https://www.petrojobs.om/en-us/Pages/Job/Details.aspx?i={detailId}`
- **Pagination**: None needed — all results on single page (8 jobs currently)
- **Notes**: PetroJobs.om is a joint recruitment portal for 9 Oman O&G operators (PDO, OQ, BP, Daleel, CC Energy, Oxy, OLNG, ARA, Masar). Company filter value for PDO is `cpn=1`. All PDO jobs are in Oman, no specific city/location provided. Chrome extension may block URLs with query strings in JS output — use document.title or get_page_text for extraction.

### 21. QatarEnergy LNG (12 jobs)
- **URL**: https://careers.qatarenergylng.qa/search/?q=&sortColumn=referencedate&sortDirection=desc
- **Platform**: Taleo (Oracle) career site — server-rendered HTML with `tr.data-row` table rows
- **Method**: Single-page search results. Navigate to URL with `sortColumn=referencedate&sortDirection=desc` to get all jobs sorted by date. Extract from `tr.data-row` elements: title from `a.jobTitle-link`, department from `span.jobDepartment`, location from `span.jobLocation`, date from cell matching date regex, job ID from numeric cell, href from link attribute.
- **DOM Selectors**: `tr.data-row` for job rows. `a.jobTitle-link` for title + href. Location in `span.jobLocation` (format "City, QA"). Department in `span.jobDepartment`. Date in td matching `/^\d+ [A-Z][a-z]{2} \d{4}$/`.
- **Link Format**: `https://careers.qatarenergylng.qa{href}` where href is `/job/City-Title-Slug/NumericId/`
- **Pagination**: None needed — all 12 results on single page
- **Notes**: All jobs in Qatar (Doha or Ras Laffan 2 South). Categories include National Graduates, Finance & Accounting, Information Technology, Internship, HSE. Some jobs may have empty department field — infer category from title. Location format includes ", QA" suffix which should be stripped.

### 22. North Oil Company (2 jobs)
- **URL**: https://careers.noc.qa/search/?q=&sortColumn=referencedate&sortDirection=desc
- **Platform**: Taleo (Oracle) career site — same platform as QatarEnergy LNG
- **Method**: Single-page search results. Navigate to URL with sort params. Extract from `tr.data-row` elements: title from `a.jobTitle-link`, department from `span.jobDepartment`, location from `span.jobLocation`, date from cell matching date regex, href from link attribute.
- **DOM Selectors**: `tr.data-row` for job rows. `a.jobTitle-link` for title + href. Department in `span.jobDepartment`. Location in `span.jobLocation` (just "QA").
- **Link Format**: `https://careers.noc.qa{href}` where href is `/job/Title-Slug/NumericId/`
- **Pagination**: None needed — all results on single page (currently only 2 jobs)
- **Notes**: All jobs in Qatar. Very small number of openings. NOC is a Qatar Petroleum / TotalEnergies JV for the Al-Shaheen offshore field. Departments map to categories: "Health and Industrial Hygiene" → HSE, "Human Resources" (for internship postings) → Internship.

### 23. Dragon Oil (8 jobs)
- **URL**: https://career22.sapsf.com/career?company=dragonoilh
- **Platform**: SAP SuccessFactors career portal
- **Method**: Navigate to portal, click "Search Jobs" to load results. All 8 jobs on single page. Extract from `tr.jobResultItem` rows: title from `a.jobTitle`, requisition info from row `innerText` matching regex `Requisition ID: (\d+) - Posted on (\S+) - (.+)`. Location code on a separate line starting with `DOTL` or `DOHL`.
- **DOM Selectors**: `tr.jobResultItem` for job rows. `a.jobTitle` for title link. Requisition line parsed with regex. Location line starts with `DOTL-` (Turkmenistan) or `DOHL` (Dubai HQ).
- **Link Format**: `https://career22.sapsf.com/career?career_ns=job_listing&company=dragonoilh&navBarLevel=JOB_SEARCH&rcm_site_locale=en_US&career_job_req_id={reqId}&selected_lang=en_GB`
- **Pagination**: None needed — all results on single page
- **Notes**: Dragon Oil is an ENOC subsidiary. Jobs split between Turkmenistan (DOTL = Dragon Oil Turkmenistan Limited, locations: Hazar offshore, Ashgabat) and UAE (DOHL = Dragon Oil Holdings Ltd, Dubai Corporate Head Office). No department field on listing — categories inferred from title. The dragonoil.com/careers/ page links to the SAP SuccessFactors portal via "Current Vacancies". Chrome extension blocks href extraction due to query strings — click through to detail page or use reqId to construct links.

### 24. McDermott (357 jobs)
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
- **Notes**: mcdermott.com embeds Oracle HCM in an iframe. CORS blocks cross-origin API calls from mcdermott.com — must navigate browser directly to the Oracle HCM portal (`edsv.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/`) and make API calls from the same origin. Jobs span 18+ countries worldwide (UAE 78, Malaysia 65, India 55, Indonesia 41, US 36, UK 19, etc.).

### 25. Saipem (195 jobs)
- **URL**: https://jobs.saipem.com/
- **Platform**: Custom job board powered by NCorePlat (app.ncoreplat.com)
- **Method**: Static JSON file fetch — all jobs in a single `positions_saipem.json`
- **Data Source**: `https://jobs.saipem.com/positions_saipem.json`
- **JSON Structure**: `data.Positions` object keyed by subsidiary name (17 subsidiaries), each containing array of job objects
- **Job Fields**: `title`, `countryText`, `sectorText`, `url`, `orderDate`, `root-node` (subsidiary)
- **Pagination**: None — all jobs in single JSON file
- **Link Format**: Direct URLs to `app.ncoreplat.com/jobposition/{id}/...`
- **Subsidiaries**: Global Projects Services AG, Saipem Romania Srl, Saipem SA (France), Saipem Limited (UK), Saipem India, Saipem Luxembourg Angola Branch, Petromar Lda, Saipem Australia, Saipem Spa (Italy), Saipem Offshore Construction, Saipem SpA Qatar Branch, Saipem do Brasil, SAIPEM SpA Abu Dhabi Branch, SEI Spa Ivory Coast Branch, Saudi Arabian Saipem Co. Ltd., Snamprogetti Saudi Arabia Co. Ltd., Saipem America Inc
- **Country Normalization**: "United Arab Emirates" → "UAE", "United Kingdom" → "UK", "United States" → "USA", "Cote d'Ivoire" → "Ivory Coast"
- **Categories**: Sector field available (`sectorText`) plus title-based inference for granular categories
- **Notes**: Very straightforward scraping — static JSON with all data. Jobs span 15+ countries (Italy 50, France 32, Offshore 25, Qatar 13, Angola 11, Saudi Arabia 11, etc.). Many French-language internship postings ("STAGE ...") from Saipem SA. The "Offshore" country designation means vessel/offshore-based roles with no fixed country.

### 26. Technip Energies (172 jobs)
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
- **Notes**: T.EN (Technip Energies) career site. Jobs span 15 countries (France 58, UK 27, India 20, Malaysia 15, UAE 11, USA 10, Colombia 9, Spain 8, etc.). Many French-language and V.I.E (Volontariat International en Entreprise) postings. Headquarters in Nanterre, France. UAE jobs are predominantly for UAE Nationals.

### Middle East Only Companies (unchanged)
- **ENOC**
- **OQ Group**
- **KPC**
- **KNPC**
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
