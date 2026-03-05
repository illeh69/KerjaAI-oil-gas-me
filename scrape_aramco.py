#!/usr/bin/env python3
"""
Saudi Aramco Career Jobs Scraper
=================================
Scrapes all job vacancies from careers.aramco.com and saves to CSV.

METODE SCRAPING (untuk referensi di sesi berikutnya):
=====================================================
1. Buka browser ke https://careers.aramco.com/search/?q=&sortColumn=referencedate&sortDirection=desc
2. Gunakan JavaScript di browser (via Claude-in-Chrome MCP tools) untuk fetch semua halaman:

   JavaScript code untuk dijalankan di browser:
   ```javascript
   (async function() {
       const allJobs = [];
       const baseUrl = 'https://careers.aramco.com/search/?q=&sortColumn=referencedate&sortDirection=desc&startrow=';

       for (let page = 0; page < 20; page++) {  // max 20 pages
           const startRow = page * 25;
           const resp = await fetch(baseUrl + startRow);
           const html = await resp.text();
           const parser = new DOMParser();
           const doc = parser.parseFromString(html, 'text/html');
           const rows = doc.querySelectorAll('tr.data-row');

           if (rows.length === 0) break;

           rows.forEach(row => {
               const link = row.querySelector('a.jobTitle-link');
               if (link) {
                   allJobs.push({
                       title: link.textContent.trim(),
                       url: 'https://careers.aramco.com' + link.getAttribute('href')
                   });
               }
           });
       }
       window._aramcoAll = allJobs;
       return JSON.stringify({total: allJobs.length});
   })()
   ```

3. Ekstrak data dari browser dalam batch kecil (max 15-20 per batch karena
   limitasi output tool):
   - Titles:  window._titles.slice(START, END).join('||')
   - URLs:    window._urls.slice(START, END).map(u => u.replace('https://careers.aramco.com/','')).join('\\n')

4. Masukkan data titles[] dan paths[] ke script ini, lalu jalankan untuk
   generate CSV.

CATATAN PENTING:
- Aramco menggunakan pagination dengan ?startrow=N (kelipatan 25)
- Setiap halaman menampilkan max 25 jobs dalam <tr class="data-row">
- Link job ada di <a class="jobTitle-link"> dengan href relatif
- URL format: /expat_us/job/SLUG/NUMERIC_ID/ atau /expat_uk/job/... atau /saudi/job/...
- Tidak bisa fetch langsung dari Python (blocked), HARUS pakai browser
- Location dan Category tidak tersedia di listing page (semua "SA"),
  jadi category di-assign berdasarkan title keywords

Terakhir dijalankan: 2026-03-05 (220 jobs)
"""

import csv
import os
from datetime import date
from collections import Counter


def categorize(title: str) -> str:
    """Assign job category based on title keywords."""
    t = title.lower()

    if any(w in t for w in ['counsel', 'legal', 'intellectual property', 'litigation', 'compliance counsel']):
        return 'Legal'
    if any(w in t for w in ['graduate', 'experienced it', 'experienced engineer', 'experienced business',
                             'experienced other', 'experienced science']):
        return 'Early Careers'
    if any(w in t for w in ['geolog', 'geophys', 'geosci', 'reservoir', 'seismol', 'geochem', 'geomech',
                             'hydrogeol', 'petrophys', 'ior specialist', 'subsurface', 'oilfield microbiology']):
        return 'Geoscience & Reservoir'
    if any(w in t for w in ['drilling', 'well intervention', 'well operations', 'production engineer']):
        return 'Drilling & Production'
    if any(w in t for w in ['data scien', 'it ', 'digital', 'solution architect', 'network',
                             'platform engineer', 'infrastructure engineer', 'computational', 'automation',
                             'system analyst', 'ai governance', 'data manage', 'information system']):
        return 'Digital & IT'
    if any(w in t for w in ['safety', 'security', 'loss prevention', 'fire protection', 'emergency',
                             'crisis', 'incident', 'human factors']):
        return 'Safety & Security'
    if any(w in t for w in ['finance', 'treasury', 'accounting', 'credit', 'investment', 'debt', 'audit',
                             'fraud', 'insurance', 'deal quality', 'corporate finance', 'banking', 'financial']):
        return 'Finance & Audit'
    if any(w in t for w in ['marketing', 'sales', 'writer', 'communications', 'media relations',
                             'content creator', 'speechwriter']):
        return 'Marketing & Communications'
    if any(w in t for w in ['contract', 'procurement']):
        return 'Contracts & Procurement'
    if any(w in t for w in ['strateg', 'planning', 'planner', 'transformation', 'governance',
                             'enterprise risk', 'continuous improvement', 'operational excellence']):
        return 'Strategy & Planning'
    if any(w in t for w in ['psycholog', 'organizational', 'training', 'industrial relations', 'real estate',
                             'workforce planning', 'assessment', 'career development', 'instructional',
                             'teacher', 'archivist', 'coaching']):
        return 'Human Resources'
    if any(w in t for w in ['environmental', 'sustainability', 'climate', 'gri', 'greenhouse',
                             'decarbonization']):
        return 'Environmental & Sustainability'
    if any(w in t for w in ['engineer', 'specialist', 'architect', 'process', 'electrical', 'mechanical',
                             'instrument', 'corrosion', 'reliability', 'static', 'turnaround', 'quality',
                             'cost engineer', 'estimating', 'facilities', 'lng', 'gas ', 'metering',
                             'switchgear', 'power', 'rotating', 'foreman', 'ospas', 'pilot plant', 'modeli']):
        return 'Engineering'
    if any(w in t for w in ['business', 'affiliate', 'consultant', 'advisor', 'analyst', 'assistant']):
        return 'Business & Operations'
    return 'General'


def build_csv(titles: list, paths: list, output_path: str):
    """
    Build Saudi_Aramco_Jobs.csv from titles and URL paths.

    Args:
        titles: List of job title strings
        paths: List of URL paths (after careers.aramco.com/)
        output_path: Full path to output CSV file
    """
    BASE = "https://careers.aramco.com/"
    today = date.today().isoformat()

    assert len(titles) == len(paths), f"Mismatch: {len(titles)} titles vs {len(paths)} paths"

    rows = []
    for i in range(len(titles)):
        rows.append({
            "Country": "Saudi Arabia",
            "Company": "Saudi Aramco",
            "Title": titles[i],
            "Category": categorize(titles[i]),
            "Location": "Saudi Arabia",
            "Date Posted": today,
            "Link": BASE + paths[i],
        })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Country", "Company", "Title", "Category", "Location", "Date Posted", "Link"])
        w.writeheader()
        w.writerows(rows)

    print(f"Written {len(rows)} Saudi Aramco jobs to {output_path}")

    # Show category breakdown
    cc = Counter(r["Category"] for r in rows)
    for c, n in cc.most_common():
        print(f"  {c}: {n}")

    return rows


# ============================================================================
# DATA - Update bagian ini setiap kali scraping ulang
# Paste titles dan paths dari hasil ekstraksi browser
# ============================================================================

titles = [
    # 0-19
    "Industrial Communications Engineer", "Sr Counsel - Corporate & Project Finance", "Tax Counsel",
    "Infrastructure Facilities Planning Engineer", "Substation Equipment Engineer",
    "Compressors & Steam Turbines Engineer", "Heat Exchanger Engineer",
    "Sr Counsel - Joint Venture Development", "Electrical Planning Engineer",
    "Nonmetallic Engineering Specialist", "Solution Architect", "Sr Counsel - Venture Capital",
    "Estimating Engineer", "Gas Business Modeler", "Senior Writer/Editor",
    "Gas Commercial Specialist", "Lead Gas Master Planning Specialist",
    "Computing and IT Graduates (less than three years of work experience)",
    "Business Graduates (less than three years of work experience)", "Safety Advisor",
    # 20-39
    "Planning & Performance Management Analyst",
    "Engineering Graduates (less than three years of work experience)",
    "Reservoir Simulation Developer", "OSPAS Specialist", "Lead Drilling Engineer",
    "Accounting Analyst", "Senior Mechanical Maintenance Engineer",
    "Lead Process Operations Engineer", "Senior Contract Advisor", "Field Compliance Coordinator",
    "Security Investigator", "Information System Consultant", "Safety Engineer",
    "Fire Protection Engineer", "Process Safety Engineer", "Well Intervention Specialist",
    "Process Engineer", "Building Life Safety Plans Examiner",
    "Safety Engineer (Drilling & Workover Operations)", "Business Writer",
    # 40-59
    "D&IT Affiliates Advisor", "Digital & IT Strategy Consultant", "Business System Analyst",
    "Field Development Geologist", "Data Scientist Specialist",
    "Oil Reservoir Management Engineer",
    "Geomatics/Geographic Information Systems Analyst", "Risk & Resource Geoscientist",
    "Facilities Engineer", "Environmental Coordinator", "LNG Economist",
    "Deal Quality Specialist", "LNG Sales & Marketing Specialist",
    "Subsurface Data Management Specialist", "Industrial Computer Engineer",
    "Senior Diving Inspection Specialist", "Diving Specialist",
    "International Media Relations Specialist", "Program Manager and Development Advisor",
    "Credit Risk Management Analyst",
    # 60-79
    "Lead Financial Analyst", "Assessment & Coaching Subject Matter Expert",
    "Career Development Specialist", "Management and Professional Trainer",
    "Senior Accounting Analyst", "Gas Reservoir Engineer",
    "Linear Programming (LP) Modeling Engineer", "Project Support Engineer",
    "AFFILIATES MANAGEMENT ADVISOR", "Affiliate Financial Advisor",
    "English Content Creator", "Litigation Counsel", "Downstream Transformation Analyst",
    "Digital Marketing Analyst", "Capital Markets Financial Analyst",
    "Strategy & Energy Market Specialist", "Insurance Risk Specialist", "Senior Archivist",
    "Oil Reservoir Management Engineer", "Project Finance Specialist",
    # 80-99
    "Venture Building Expert", "Treasury Analyst", "Affiliate Finance Advisor",
    "Cash Management Treasury Analyst", "Debt Management Specialist",
    "Crisis and Business Continuity Advisor", "Safety Engineer - Marine Operations",
    "Safety Engineer - Aviation Operations", "Petroleum Engineer Systems Analyst",
    "Architect", "Sr Counsel - Manufacturing & Power Practice", "Drilling Engineer",
    "Upstream & LNG Strategist",
    "Process Engineer - Solomon Benchmarking - Refinery Experience Only",
    "Compliance Counsel", "Accounting Analyst", "Elementary-Intermediate Teacher",
    "Lead Field Compliance Coordinator",
    "Business Development Specialist - Transaction & Execution", "AI Governance Officer",
    # 100-119
    "Speechwriter", "Affiliates Management Advisor - Medical Services",
    "Mineral Strategy Analyst", "Onshore Structural Engineer",
    "Business Development Specialist - Transaction Execution", "Lead Accounting Analyst",
    "Process Modeling Specialist", "Gas & NGL Planning Engineer",
    "Process Simulation Twin & Optimization Engineer - Refinery Experience Only",
    "Sr Strategy & Market Consultant", "Operational Excellence Specialist",
    "Instructional Designer",
    "Manufacturing Performance Expert - Refinery Experience Only",
    "Field Compliance Coordinator", "Facilities Planning Engineer", "Production Engineer",
    "Lead Corporate Strategist - Industrial Portfolio", "Sr Legal Counsel - Gas",
    "Sr Power Systems Strategy & Market Consultant", "Business Origination Specialist",
    # 120-139
    "Sr Legal Counsel - Unconventional Gas", "Sr Counsel - Chemicals & Retail",
    "Computational Research Expert (Optimization and Control)",
    "Computational Research Expert (AI Specialist)", "Electrical Power Contracts Engineer",
    "Other Graduates (less than three years of work experience)",
    "Experienced IT (more than three years of work experience)",
    "Counsel - General Corporate and Commercial Contracts",
    "Experienced Engineer (more than three years of work experience)",
    "Experienced Business (more than three years of work experience)",
    "Experienced Other (more than three years of work experience)",
    "Assistant to Director", "Occupational Health Consultant",
    "Senior Corporate Strategy Advisor",
    "Greenhouse Gas Management and Decarbonization Specialist",
    "Pilot Plant Process Engineer", "Data Scientist",
    "Process Engineer - Fluid Catalytic Cracking - Refinery Experience Only",
    "Metering Engineer - Refinery Experience Only", "Oilfield Microbiology Specialist",
    # 140-159
    "Enterprise Risk Management Specialist", "Data Scientist", "Financial Specialist",
    "Process Engineer", "Data Management Analyst", "MV Switchgear Specialist",
    "Communications Specialist",
    "Downstream Corrosion Engineer - Refinery Experience Only",
    "Financial Auditor", "Operational Auditor", "Drilling Foreman", "Drilling Foreman",
    "Process Engineer", "Instrumentation & Control Engineer", "Drilling Foreman",
    "IT Auditor", "Rotating Equipment Engineer", "Protection & Control Engineer",
    "Drilling Foreman", "Rotating Equipment Engineer",
    # 160-179
    "Process Engineer", "Gas Insulated Switchgear Specialist",
    "Overhead Power Line Specialist", "Automation Engineer",
    "Turnaround & Inspection Engineer", "Plant Corrosion Engineer", "Electrical Engineer",
    "Fraud Investigator", "Plant Corrosion Engineer",
    "Reliability & Asset Integrity Engineer", "Reservoir Engineer",
    "Static Mechanical Engineer", "Continuous Improvement Consultant",
    "Power Cable Specialist", "Strategic Workforce Planning Consultant",
    "Executive Assessment Lead", "Sr Counsel I",
    "Computational Research Expert (Material Discovery)",
    "Electrical Project Engineer", "Lead Mechanical Project Engineer",
    # 180-199
    "Mechanical Project Engineer", "Downstream Sustainability Specialist",
    "Planning & Performance Analyst", "Accounting Analyst",
    "Oil & Gas Financial Analyst",
    "Senior Downstream Planning & Performance Management Analyst",
    "Governance, Risk & Compliance Specialist",
    "Lead Financial Reporting & Performance Analyst",
    "Lead Downstream Finance, Planning & Performance Management Analyst",
    "Senior Planning & Performance Management Advisor",
    "Banking Operations Specialist", "Senior Project Engineer",
    "Rotating Equipment Engineer", "Contracts Advisor",
    "Business Development Specialist", "Business Development Specialist",
    "Human Factors Engineer", "Lead Organizational & Management Specialist",
    "Instructional Designer", "Incident Investigator",
    # 200-219
    "Emergency Management Advisor", "Process/Operation Engineer",
    "Program Development & Evaluation Analyst", "Training & Development Advisor",
    "Reliability&Rotating Equipment Engineer", "Intellectual Property Counsel",
    "Corrosion Engineer", "Reservoir Engineer", "Instrumentation Engineer",
    "Sr Counsel", "Exploration Geoscientist", "Contracts Advisor",
    "Delayed Coker Visbreaker Specialist  - Refinery Experience Only",
    "Technology Consultant - Refinery Experience Only",
    "Process Engineer - Utilities & Tank Farm - Refinery Experience Only",
    "Process Engineer - Sulfur Recovery - Refinery Experience Only",
    "Analyzer Engineer - Refinery Experience Only",
    "Instrumentation Engineer - Refinery Experience Only",
    "Maintenance Engineering Specialist - Refinery Experience Only",
    "Lead Turnaround Engineer - Refinery Experience Only",
]

paths = [
    # 0-14
    "expat_us/job/Industrial-Communications-Engineer/857079923/",
    "expat_uk/job/Sr-Counsel-Corporate-&-Project-Finance/857034323/",
    "expat_uk/job/Tax-Counsel/857034223/",
    "expat_us/job/Infrastructure-Facilities-Planning-Engineer/857080223/",
    "expat_us/job/Substation-Equipment-Engineer/857079523/",
    "expat_us/job/Compressors-&-Steam-Turbines-Engineer/857079823/",
    "expat_us/job/Heat-Exchanger-Engineer/857079623/",
    "expat_uk/job/Sr-Counsel-Joint-Venture-Development/857034423/",
    "expat_us/job/Electrical-Planning-Engineer/857080323/",
    "expat_us/job/Nonmetallic-Engineering-Specialist/857079723/",
    "expat_us/job/Solution-Architect/857080123/",
    "expat_uk/job/Sr-Counsel-Venture-Capital/857034523/",
    "expat_us/job/Estimating-Engineer/857080423/",
    "expat_us/job/Gas-Business-Modeler/857079023/",
    "expat_us/job/Senior-WriterEditor/856486923/",
    # 15-29
    "expat_uk/job/Gas-Commercial-Specialist/857079123/",
    "expat_us/job/Lead-Gas-Master-Planning-Specialist/857078923/",
    "saudi/job/Computing-and-IT-Graduates-%28less-than-three-years-of-work-experience%29/766636523/",
    "saudi/job/Business-Graduates-%28less-than-three-years-of-work-experience%29/766636423/",
    "expat_uk/job/Safety-Advisor/857078823/",
    "expat_uk/job/Planning-&-Performance-Management-Analyst/857100723/",
    "saudi/job/Engineering-Graduates-%28less-than-three-years-of-work-experience%29/766636323/",
    "expat_uk/job/Reservoir-Simulation-Developer/857078423/",
    "expat_us/job/OSPAS-Specialist/857099923/",
    "expat_uk/job/Lead-Drilling-Engineer/857100423/",
    "expat_uk/job/Accounting-Analyst/857100023/",
    "expat_uk/job/Senior-Mechanical-Maintenance-Engineer/857128623/",
    "expat_uk/job/Lead-Process-Operations-Engineer/857128423/",
    "expat_uk/job/Senior-Contract-Advisor/857128523/",
    "expat_uk/job/Field-Compliance-Coordinator/857031723/",
    # 30-44
    "expat_uk/job/Security-Investigator/857077823/",
    "expat_uk/job/Information-System-Consultant/857077223/",
    "expat_uk/job/Safety-Engineer/857078223/",
    "expat_uk/job/Fire-Protection-Engineer/857077623/",
    "expat_uk/job/Process-Safety-Engineer/857078123/",
    "expat_us/job/Well-Intervention-Specialist/857031223/",
    "expat_uk/job/Process-Engineer/857077023/",
    "expat_uk/job/Building-Life-Safety-Plans-Examiner/857078023/",
    "expat_uk/job/Safety-Engineer-%28Drilling-&-Workover-Operations%29/857078323/",
    "expat_us/job/Business-Writer/857077323/",
    "expat_uk/job/D&IT-Affiliates-Advisor/857077123/",
    "expat_uk/job/Digital-&-IT-Strategy-Consultant/857076323/",
    "expat_uk/job/Business-System-Analyst/857099523/",
    "expat_uk/job/Field-Development-Geologist/857076523/",
    "expat_uk/job/Data-Scientist-Specialist/857099623/",
    # 45-59
    "expat_uk/job/Oil-Reservoir-Management-Engineer/857030523/",
    "expat_uk/job/GeomaticsGeographic-Information-Systems-Analyst/857076723/",
    "expat_uk/job/Risk-&-Resource-Geoscientist/856937223/",
    "expat_us/job/Facilities-Engineer/857074923/",
    "expat_uk/job/Environmental-Coordinator/857098323/",
    "expat_us/job/LNG-Economist/857075823/",
    "expat_us/job/Deal-Quality-Specialist/857075723/",
    "expat_us/job/LNG-Sales-&-Marketing-Specialist/857075923/",
    "expat_us/job/Subsurface-Data-Management-Specialist/857075623/",
    "expat_uk/job/Industrial-Computer-Engineer/857075023/",
    "expat_uk/job/Senior-Diving-Inspection-Specialist/857075123/",
    "expat_uk/job/Diving-Specialist/857075223/",
    "expat_uk/job/International-Media-Relations-Specialist/857098723/",
    "expat_us/job/Program-Manager-and-Development-Advisor/857074023/",
    "expat_uk/job/Credit-Risk-Management-Analyst/857028523/",
    # 60-74
    "expat_uk/job/Lead-Financial-Analyst/857073823/",
    "expat_us/job/Assessment-&-Coaching-Subject-Matter-Expert/857074123/",
    "expat_us/job/Career-Development-Specialist/857074223/",
    "expat_us/job/Management-and-Professional-Trainer/857074323/",
    "expat_uk/job/Senior-Accounting-Analyst/857097423/",
    "expat_uk/job/Gas-Reservoir-Engineer/857121923/",
    "expat_uk/job/Linear-Programming-%28LP%29-Modeling-Engineer/857096723/",
    "expat_uk/job/Project-Support-Engineer/857121123/",
    "expat_us/job/AFFILIATES-MANAGEMENT-ADVISOR/857095723/",
    "expat_us/job/Affiliate-Financial-Advisor/857095623/",
    "expat_us/job/English-Content-Creator/857096123/",
    "expat_uk/job/Litigation-Counsel/857120423/",
    "expat_uk/job/Downstream-Transformation-Analyst/857120823/",
    "expat_us/job/Digital-Marketing-Analyst/856442623/",
    "expat_uk/job/Capital-Markets-Financial-Analyst/857027123/",
    # 75-89
    "expat_uk/job/Strategy-&-Energy-Market-Specialist/857027423/",
    "expat_uk/job/Insurance-Risk-Specialist/857027323/",
    "expat_us/job/Senior-Archivist/856442923/",
    "expat_uk/job/Oil-Reservoir-Management-Engineer/857023723/",
    "expat_uk/job/Project-Finance-Specialist/857027223/",
    "expat_uk/job/Venture-Building-Expert/857026123/",
    "expat_uk/job/Treasury-Analyst/857023123/",
    "expat_uk/job/Affiliate-Finance-Advisor/857068423/",
    "expat_uk/job/Cash-Management-Treasury-Analyst/857023023/",
    "expat_uk/job/Debt-Management-Specialist/857021523/",
    "expat_uk/job/Crisis-and-Business-Continuity-Advisor/857070923/",
    "expat_uk/job/Safety-Engineer-Marine-Operations/857093823/",
    "expat_uk/job/Safety-Engineer-Aviation-Operations/857093923/",
    "expat_uk/job/Petroleum-Engineer-Systems-Analyst/857094823/",
    "expat_us/job/Architect/856539023/",
    # 90-104
    "expat_uk/job/Sr-Counsel-Manufacturing-&-Power-Practice/856316523/",
    "expat_uk/job/Drilling-Engineer/857092723/",
    "expat_uk/job/Upstream-&-LNG-Strategist/857093323/",
    "expat_us/job/Process-Engineer-Solomon-Benchmarking-Refinery-Experience-Only/855870823/",
    "expat_us/job/Compliance-Counsel/857119823/",
    "expat_uk/job/Accounting-Analyst/857119923/",
    "expat_us/job/Elementary-Intermediate-Teacher/857066723/",
    "expat_uk/job/Lead-Field-Compliance-Coordinator/857067423/",
    "expat_uk/job/Business-Development-Specialist-Transaction-&-Execution/857091523/",
    "expat_uk/job/AI-Governance-Officer/856776223/",
    "expat_us/job/Speechwriter/857091923/",
    "expat_uk/job/Affiliates-Management-Advisor-Medical-Services/857091823/",
    "expat_us/job/Mineral-Strategy-Analyst/857119423/",
    "expat_us/job/Onshore-Structural-Engineer/857089523/",
    "expat_uk/job/Business-Development-Specialist-Transaction-Execution/857064923/",
    # 105-119
    "expat_uk/job/Lead-Accounting-Analyst/856893023/",
    "expat_us/job/Process-Modeling-Specialist/857089423/",
    "expat_us/job/Gas-&-NGL-Planning-Engineer/857089323/",
    "expat_uk/job/Process-Simulation-Twin-&-Optimization-Engineer-Refinery-Experience-Only/857080823/",
    "expat_uk/job/Sr-Strategy-&-Market-Consultant/857119023/",
    "expat_us/job/Operational-Excellence-Specialist/857089023/",
    "expat_uk/job/Instructional-Designer/857088923/",
    "expat_us/job/Manufacturing-Performance-Expert-Refinery-Experience-Only/855896223/",
    "expat_uk/job/Field-Compliance-Coordinator/857117223/",
    "expat_uk/job/Facilities-Planning-Engineer/857118423/",
    "expat_uk/job/Production-Engineer/857117423/",
    "expat_us/job/Lead-Corporate-Strategist-Industrial-Portfolio/857116623/",
    "expat_us/job/Sr-Legal-Counsel-Gas/857013723/",
    "expat_uk/job/Sr-Power-Systems-Strategy-&-Market-Consultant/857062123/",
    "expat_uk/job/Business-Origination-Specialist/857061923/",
    # 120-134
    "expat_uk/job/Sr-Legal-Counsel-Unconventional-Gas/857013823/",
    "expat_uk/job/Sr-Counsel-Chemicals-&-Retail/857013923/",
    "expat_uk/job/Computational-Research-Expert-%28Optimization-and-Control%29/857062823/",
    "expat_uk/job/Computational-Research-Expert-%28AI-Specialist%29/857062223/",
    "expat_uk/job/Electrical-Power-Contracts-Engineer/857062023/",
    "saudi/job/Other-Graduates-%28less-than-three-years-of-work-experience%29/766636923/",
    "saudi/job/Experienced-IT-%28more-than-three-years-of-work-experience%29/856956923/",
    "expat_uk/job/Counsel-General-Corporate-and-Commercial-Contracts/857013023/",
    "saudi/job/Experienced-Engineer-%28more-than-three-years-of-work-experience%29/856956723/",
    "saudi/job/Experienced-Business-%28more-than-three-years-of-work-experience%29/856957123/",
    "saudi/job/Experienced-Other-%28more-than-three-years-of-work-experience%29/856957023/",
    "expat_uk/job/Assistant-to-Director/766671423/",
    "expat_us/job/Occupational-Health-Consultant/857088023/",
    "expat_uk/job/Senior-Corporate-Strategy-Advisor/856748923/",
    "expat_us/job/Greenhouse-Gas-Management-and-Decarbonization-Specialist/857088123/",
    # 135-149
    "expat_uk/job/Pilot-Plant-Process-Engineer/857061123/",
    "expat_uk/job/Data-Scientist/857061023/",
    "expat_us/job/Process-Engineer-Fluid-Catalytic-Cracking-Refinery-Experience-Only/855867223/",
    "expat_uk/job/Metering-Engineer-Refinery-Experience-Only/855916623/",
    "expat_uk/job/Oilfield-Microbiology-Specialist/857060923/",
    "expat_us/job/Enterprise-Risk-Management-Specialist/857044623/",
    "expat_us/job/Data-Scientist/857087823/",
    "expat_uk/job/Financial-Specialist/857040523/",
    "expat_uk/job/Process-Engineer/857087723/",
    "expat_us/job/Data-Management-Analyst/857087423/",
    "expat_uk/job/MV-Switchgear-Specialist/857087323/",
    "expat_uk/job/Communications-Specialist/857087523/",
    "expat_uk/job/Downstream-Corrosion-Engineer-Refinery-Experience-Only/855852423/",
    "expat_uk/job/Financial-Auditor/857038223/",
    "expat_us/job/Operational-Auditor/857038523/",
    # 150-164
    "expat_uk/job/Drilling-Foreman/857038623/",
    "expat_uk/job/Drilling-Foreman/857038823/",
    "expat_uk/job/Process-Engineer/857039823/",
    "expat_uk/job/Instrumentation-&-Control-Engineer/857039023/",
    "expat_uk/job/Drilling-Foreman/857038723/",
    "expat_uk/job/IT-Auditor/857038423/",
    "expat_uk/job/Rotating-Equipment-Engineer/857039523/",
    "expat_us/job/Protection-&-Control-Engineer/857086823/",
    "expat_us/job/Drilling-Foreman/857086623/",
    "expat_uk/job/Rotating-Equipment-Engineer/857039623/",
    "expat_uk/job/Process-Engineer/857039323/",
    "expat_us/job/Gas-Insulated-Switchgear-Specialist/857086923/",
    "expat_us/job/Overhead-Power-Line-Specialist/857086723/",
    "expat_uk/job/Automation-Engineer/857087023/",
    "expat_uk/job/Turnaround-&-Inspection-Engineer/857039723/",
    # 165-179
    "expat_uk/job/Plant-Corrosion-Engineer/857039223/",
    "expat_uk/job/Electrical-Engineer/857038923/",
    "expat_uk/job/Fraud-Investigator/857038323/",
    "expat_uk/job/Plant-Corrosion-Engineer/857039123/",
    "expat_us/job/Reliability-&-Asset-Integrity-Engineer/857086223/",
    "expat_uk/job/Reservoir-Engineer/857039423/",
    "expat_uk/job/Static-Mechanical-Engineer/857039923/",
    "expat_uk/job/Continuous-Improvement-Consultant/857086123/",
    "expat_uk/job/Power-Cable-Specialist/857087123/",
    "expat_uk/job/Strategic-Workforce-Planning-Consultant/857085823/",
    "expat_uk/job/Executive-Assessment-Lead/857085523/",
    "expat_uk/job/Sr-Counsel-I/857085023/",
    "expat_uk/job/Computational-Research-Expert-%28Material-Discovery%29/857085923/",
    "expat_uk/job/Electrical-Project-Engineer/857109923/",
    "expat_uk/job/Lead-Mechanical-Project-Engineer/857110023/",
    # 180-194
    "expat_uk/job/Mechanical-Project-Engineer/857109523/",
    "expat_uk/job/Downstream-Sustainability-Specialist/857110723/",
    "expat_uk/job/Planning-&-Performance-Analyst/857110423/",
    "expat_uk/job/Accounting-Analyst/857110923/",
    "expat_uk/job/Oil-&-Gas-Financial-Analyst/857110623/",
    "expat_uk/job/Senior-Downstream-Planning-&-Performance-Management-Analyst/857109223/",
    "expat_uk/job/Governance%2C-Risk-&-Compliance-Specialist/857108723/",
    "expat_uk/job/Lead-Financial-Reporting-&-Performance-Analyst/857108423/",
    "expat_uk/job/Lead-Downstream-Finance%2C-Planning-&-Performance-Management-Analyst/857108523/",
    "expat_uk/job/Senior-Planning-&-Performance-Management-Advisor/857108323/",
    "job/Banking-Operations-Specialist/857104823/",
    "expat_uk/job/Senior-Project-Engineer/857107623/",
    "expat_uk/job/Rotating-Equipment-Engineer/857105623/",
    "expat_uk/job/Contracts-Advisor/857106023/",
    "expat_uk/job/Business-Development-Specialist/857038023/",
    # 195-219
    "expat_uk/job/Business-Development-Specialist/857037823/",
    "expat_uk/job/Human-Factors-Engineer/857082323/",
    "expat_uk/job/Lead-Organizational-&-Management-Specialist/857083223/",
    "expat_uk/job/Instructional-Designer/857036823/",
    "expat_uk/job/Incident-Investigator/857082423/",
    "expat_uk/job/Emergency-Management-Advisor/857082623/",
    "expat_uk/job/ProcessOperation-Engineer/857082823/",
    "expat_uk/job/Program-Development-&-Evaluation-Analyst/857083023/",
    "expat_uk/job/Training-&-Development-Advisor/857082923/",
    "expat_uk/job/Reliability&Rotating-Equipment-Engineer/857036323/",
    "expat_uk/job/Intellectual-Property-Counsel/857034823/",
    "expat_us/job/Corrosion-Engineer/857036423/",
    "expat_us/job/Reservoir-Engineer/857035223/",
    "expat_us/job/Instrumentation-Engineer/857036523/",
    "expat_uk/job/Sr-Counsel/857034923/",
    "expat_uk/job/Exploration-Geoscientist/857034723/",
    "expat_uk/job/Contracts-Advisor/857081023/",
    "expat_uk/job/Delayed-Coker-Visbreaker-Specialist-Refinery-Experience-Only/857081923/",
    "expat_uk/job/Technology-Consultant-Refinery-Experience-Only/857080623/",
    "expat_uk/job/Process-Engineer-Utilities-&-Tank-Farm-Refinery-Experience-Only/857081423/",
    "expat_uk/job/Process-Engineer-Sulfur-Recovery-Refinery-Experience-Only/857081623/",
    "expat_uk/job/Analyzer-Engineer-Refinery-Experience-Only/857082223/",
    "expat_uk/job/Instrumentation-Engineer-Refinery-Experience-Only/857080723/",
    "expat_uk/job/Maintenance-Engineering-Specialist-Refinery-Experience-Only/857081323/",
    "expat_uk/job/Lead-Turnaround-Engineer-Refinery-Experience-Only/857080923/",
]


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "Saudi_Aramco_Jobs.csv")
    build_csv(titles, paths, output_path)
