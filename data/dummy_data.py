
SCHEMES = [
    # ── 1. Scholarship ───────────────────────────────────────────────────────
    {
        "id": "scheme_001",
        "name": "National Scholarship Portal (NSP) — Pre-Matric Scholarship for Minorities",
        "category": "Scholarship / Education",
        "ministry": "Ministry of Minority Affairs, Government of India",
        "description": (
            "The NSP Pre-Matric Scholarship is a Central Government scheme that provides "
            "financial support to students from minority communities (Muslim, Christian, Sikh, "
            "Buddhist, Jain, Zoroastrian) studying in Class 1 to Class 10. The objective is to "
            "reduce the dropout rate among economically weaker sections and encourage children to "
            "continue their education. The scholarship covers tuition fees, a maintenance allowance, "
            "and an annual book grant."
        ),
        "eligibility": {
            "community": ["Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Zoroastrian"],
            "class_range": "Class 1 to Class 10",
            "annual_family_income_max_inr": 100000,
            "minimum_attendance_percent": 75,
            "institution_type": "Government or Government-aided school only",
        },
        "benefits": {
            "day_scholar_monthly": "Rs. 100 – Rs. 500 per month (varies by class)",
            "hosteller_monthly": "Rs. 600 – Rs. 1,200 per month (varies by class)",
            "adhoc_grant": "Rs. 500 per annum for books and stationery",
        },
        "next_steps": [
            "1. Visit scholarships.gov.in and click 'New Registration'.",
            "2. Register using your Aadhaar number and a valid mobile number.",
            "3. Fill in personal, academic, and bank account details completely.",
            "4. Upload required documents: Income Certificate, Minority Certificate, Marksheet, Fee Receipt.",
            "5. Submit and note your Application ID for future tracking.",
            "6. Await verification by your school/institution, then district-level approval.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "Community / Minority Certificate from a competent authority",
            "Family Income Certificate (annual)",
            "Previous Year Marksheet",
            "Bank Passbook (in student's name or joint with parent)",
            "Current Year School Fee Receipt",
        ],
        "portal_url": "https://scholarships.gov.in",
        "deadline": "Typically October 31st each year — check the portal for the current deadline.",
        "tags": ["scholarship", "minority", "student", "education", "class 1 to 10",
                 "income below 1 lakh", "NSP", "girls", "boys"],
    },

    # ── 2. Agriculture ────────────────────────────────────────────────────────
    {
        "id": "scheme_002",
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "category": "Farming / Agriculture",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": (
            "PM-KISAN is a Central Government scheme that provides an annual income support of "
            "Rs. 6,000 to all land-holding farmer families across India. The amount is transferred "
            "in three equal instalments of Rs. 2,000 every four months directly into the farmer's "
            "bank account via Direct Benefit Transfer (DBT). The aim is to help farmers meet "
            "agricultural input costs such as seeds, fertilisers, and equipment."
        ),
        "eligibility": {
            "who_can_apply": "All farmer families with cultivable land as per land records.",
            "land_size": "No upper limit on land size (small, marginal, and large farmers all eligible).",
            "excluded_categories": [
                "Institutional landholders",
                "Former/current Ministers, MPs, MLAs, and Constitutional post holders",
                "Retired government employees (except Class IV / MTS / Group D)",
                "Income tax payers",
                "Professionals: Doctors, Engineers, Lawyers, Chartered Accountants, Architects",
            ],
        },
        "benefits": {
            "annual_support_inr": 6000,
            "instalment_amount_inr": 2000,
            "instalment_schedule": ["April – July", "August – November", "December – March"],
            "payment_mode": "Direct Bank Transfer (DBT)",
        },
        "next_steps": [
            "1. Visit pmkisan.gov.in → 'Farmers Corner' → 'New Farmer Registration'.",
            "2. Select Rural or Urban Farmer and enter your Aadhaar number.",
            "3. Provide land details, bank account information, and personal data.",
            "4. Verify with the OTP sent to your Aadhaar-linked mobile number.",
            "5. Await verification by the local Patwari / Revenue official.",
            "6. Alternatively, register at your nearest Common Service Centre (CSC).",
        ],
        "required_documents": [
            "Aadhaar Card (mandatory)",
            "Land Records — Khasra / Khatauni document",
            "Bank Passbook with IFSC code",
            "Mobile number linked to Aadhaar",
        ],
        "portal_url": "https://pmkisan.gov.in",
        "deadline": "Open registration throughout the year. Instalments are released quarterly.",
        "tags": ["farmer", "kisan", "agriculture", "farming", "land", "6000 rupees",
                 "DBT", "PM Kisan", "annual support", "rural"],
    },

    # ── 3. Startup / Entrepreneurship ──────────────────────────────────────
    {
        "id": "scheme_003",
        "name": "Startup India Seed Fund Scheme (SISFS)",
        "category": "Startup / Entrepreneurship",
        "ministry": "Ministry of Commerce and Industry (DPIIT)",
        "description": (
            "The Startup India Seed Fund Scheme (SISFS) provides early-stage financial assistance "
            "to startups for proof of concept, prototype development, market entry, and "
            "commercialisation. Funds are disbursed through selected incubators, which evaluate "
            "and support eligible startups via grants or investment instruments. The scheme targets "
            "innovative startups that face difficulty accessing institutional funding."
        ),
        "eligibility": {
            "dpiit_recognition": "Must be a DPIIT-recognised startup (register at startupindia.gov.in).",
            "startup_age_max_years": 2,
            "incorporation_types": ["Private Limited Company", "LLP", "Partnership Firm"],
            "prior_government_funding_max_inr": 1000000,
            "requirements": [
                "Must have a viable product/service with clear market fit.",
                "Clear scope of commercialisation required.",
                "Promoters must not be part of another startup receiving SISFS grants.",
            ],
        },
        "benefits": {
            "grant_for_poc_prototype_inr": 2000000,
            "investment_for_commercialisation_inr": 5000000,
            "total_scheme_corpus_inr": "Rs. 945 Crore (2021–2025)",
            "instrument": "Grants + Convertible Debentures / Debt-linked instruments",
        },
        "next_steps": [
            "1. Ensure DPIIT recognition — register at startupindia.gov.in if not done.",
            "2. Visit the Startup India portal and navigate to the SISFS section.",
            "3. Browse the list of empanelled incubators and apply to a suitable one.",
            "4. Submit your application: business plan, pitch deck, and financial projections.",
            "5. The incubator's selection committee will evaluate and conduct due diligence.",
            "6. If selected, funds are released in tranches based on agreed milestones.",
        ],
        "required_documents": [
            "DPIIT Recognition Certificate",
            "Certificate of Incorporation",
            "Pitch Deck / Business Plan",
            "Founders' KYC documents",
            "Startup bank account details",
            "Prototype / PoC details (if available)",
            "Financial Projections for the next 3 years",
        ],
        "portal_url": "https://www.startupindia.gov.in/content/sih/en/funding.html",
        "deadline": "Rolling applications — check with specific empanelled incubators.",
        "tags": ["startup", "entrepreneur", "seed fund", "DPIIT", "incubator",
                 "funding", "prototype", "commercialisation", "SISFS", "business"],
    },

    # ── 4. Health ─────────────────────────────────────────────────────────────
    {
        "id": "scheme_004",
        "name": "Ayushman Bharat PM-JAY (Pradhan Mantri Jan Arogya Yojana)",
        "category": "Health / Medical",
        "ministry": "Ministry of Health and Family Welfare",
        "description": (
            "Ayushman Bharat PM-JAY is one of the world's largest government-funded health "
            "insurance schemes, providing a health cover of Rs. 5 lakh per family per year for "
            "secondary and tertiary care hospitalisation. It covers over 1,500+ medical procedures "
            "including surgeries, medical and day-care treatments. Beneficiaries are identified "
            "based on the Socio-Economic Caste Census (SECC) 2011 database."
        ),
        "eligibility": {
            "target": "Economically deprived rural and urban families listed in SECC 2011.",
            "no_cap_on": "Family size or age of members.",
            "rural_criteria": "Families in at least one of the categories: no roof, manual scavenger, "
                              "SC/ST household, landless labourer, bonded labour, etc.",
            "urban_criteria": "Occupation categories: domestic workers, rag pickers, construction "
                              "workers, street vendors, sanitation workers, etc.",
        },
        "benefits": {
            "cover_per_family_per_year_inr": 500000,
            "cashless_treatment": True,
            "empanelled_hospitals": "25,000+ government and private hospitals across India",
            "pre_existing_diseases": "Covered from day one",
            "no_premium": "No premium to be paid by the beneficiary",
        },
        "next_steps": [
            "1. Check eligibility at pmjay.gov.in or call the helpline: 14555.",
            "2. Visit your nearest empanelled hospital or Ayushman Mitra desk.",
            "3. Present your Aadhaar card or ration card for identity verification.",
            "4. The hospital will verify your details against the SECC database.",
            "5. Receive your Ayushman Card and avail cashless treatment.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "Ration Card (if Aadhaar not available)",
            "Any government-issued photo ID",
        ],
        "portal_url": "https://pmjay.gov.in",
        "deadline": "Ongoing scheme — no application deadline.",
        "tags": ["health", "insurance", "hospital", "cashless", "PM-JAY", "Ayushman Bharat",
                 "poor", "BPL", "medical", "surgery", "5 lakh", "free treatment"],
    },

    # ── 5. Housing ─────────────────────────────────────────────────────────────
    {
        "id": "scheme_005",
        "name": "Pradhan Mantri Awas Yojana — Gramin (PMAY-G)",
        "category": "Housing / Rural Development",
        "ministry": "Ministry of Rural Development",
        "description": (
            "PMAY-G aims to provide a pucca (permanent) house with basic amenities to all "
            "houseless families and those living in kutcha/dilapidated houses in rural India "
            "by 2024. Beneficiaries receive financial assistance directly in their bank "
            "accounts in tranches linked to construction progress. The scheme also supports "
            "convergence with amenities like toilets (SBM-G), LPG connections (PMUY), and "
            "electricity (Saubhagya)."
        ),
        "eligibility": {
            "target": "Houseless families or those in kutcha/dilapidated houses in rural areas.",
            "identification": "Selected from the SECC 2011 data and prioritised by Gram Sabhas.",
            "priority_given_to": [
                "SC/ST households",
                "Freed bonded labourers",
                "Minorities",
                "Persons with disabilities",
                "Widows or next-of-kin of defence/police personnel killed in action",
            ],
        },
        "benefits": {
            "financial_assistance_plain_areas_inr": 120000,
            "financial_assistance_hilly_areas_inr": 130000,
            "mgnregs_convergence_days": 90,
            "toilet_support": "Rs. 12,000 under SBM-G",
        },
        "next_steps": [
            "1. Check if your name appears on the SECC beneficiary list at pmayg.nic.in.",
            "2. Contact your Gram Panchayat or Block Development Officer (BDO) to register.",
            "3. Gram Sabha will verify and prioritise the beneficiary list.",
            "4. Open a bank account linked to Aadhaar for DBT payments.",
            "5. Construction funds are released in 3 tranches based on building progress.",
            "6. Geo-tagged photographs of construction progress must be uploaded via AwaasApp.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "Bank Account details linked to Aadhaar",
            "SECC beneficiary slip (issued by Gram Panchayat)",
            "Caste Certificate (if applicable)",
            "Photograph of existing house/land",
        ],
        "portal_url": "https://pmayg.nic.in",
        "deadline": "Ongoing — beneficiary selection done annually.",
        "tags": ["housing", "house", "rural", "pucca", "PMAY", "construction", "BPL",
                 "SC", "ST", "village", "gramin"],
    },

    # ── 6. Women Empowerment ──────────────────────────────────────────────────
    {
        "id": "scheme_006",
        "name": "Mahila Shakti Kendra (MSK)",
        "category": "Women Empowerment",
        "ministry": "Ministry of Women and Child Development",
        "description": (
            "Mahila Shakti Kendra (MSK) is a scheme that aims to empower rural women through "
            "community participation. One-stop convergent service delivery facilities are set up "
            "at the village, block, and district levels to provide rural women with access to "
            "government programmes, training, skill development, digital literacy, employment, "
            "health, and nutrition services. Student volunteers are engaged to reach the last mile."
        ),
        "eligibility": {
            "target": "Rural women, especially from economically weaker and marginalised sections.",
            "coverage": "All states and UTs — priority to 115 aspirational districts.",
        },
        "benefits": {
            "services": [
                "Skill and vocational training",
                "Digital literacy",
                "Health and nutrition awareness",
                "Legal aid and awareness about rights",
                "Linkage to government welfare schemes",
                "Community mobilisation and empowerment",
            ],
        },
        "next_steps": [
            "1. Visit your nearest Mahila Shakti Kendra at the block or district level.",
            "2. Contact the local Anganwadi worker or ASHA worker for more information.",
            "3. Enroll for free skill training or digital literacy courses offered.",
            "4. Avail linkage to other government schemes through the one-stop centre.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "Proof of residence",
            "Income Certificate (if required for specific sub-schemes)",
        ],
        "portal_url": "https://wcd.nic.in/schemes/mahila-shakti-kendra",
        "deadline": "Ongoing scheme.",
        "tags": ["women", "mahila", "rural", "skill", "digital literacy", "empowerment",
                 "training", "health", "nutrition", "legal aid"],
    },

    # ── 7. Employment / Skill ─────────────────────────────────────────────────
    {
        "id": "scheme_007",
        "name": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY 4.0)",
        "category": "Skill Development / Employment",
        "ministry": "Ministry of Skill Development and Entrepreneurship",
        "description": (
            "PMKVY is India's flagship skill training scheme. It enables Indian youth to take "
            "up industry-relevant skill training that will help them in finding better livelihood "
            "opportunities. Short-term training is provided free of cost at registered training "
            "centres. PMKVY 4.0 focuses on emerging technology domains such as coding, AI/ML, "
            "IoT, drones, and mechatronics in addition to traditional trades."
        ),
        "eligibility": {
            "age": "18 – 45 years",
            "education": "No minimum educational qualification required for most courses.",
            "nationality": "Indian citizen",
            "prior_experience": "Prior Learning is recognised via RPL (Recognition of Prior Learning).",
        },
        "benefits": {
            "training_cost": "Free of cost",
            "stipend": "Provided during the training period (varies by sector)",
            "certification": "NSQF-aligned certificate recognised by industry and government",
            "placement_support": "Training centres provide job placement assistance",
            "reward_amount_inr": "Up to Rs. 8,000 as monetary reward after certification",
        },
        "next_steps": [
            "1. Visit pmkvyofficial.org and search for training centres near you.",
            "2. Choose a course from the list of approved sectors and job roles.",
            "3. Register online or visit the training centre directly.",
            "4. Complete the prescribed training programme (typically 150–300 hours).",
            "5. Appear for the assessment conducted by an authorised Assessing Body.",
            "6. Receive your NSQF-aligned certificate and placement support.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "Aadhaar-linked mobile number",
            "Bank account details (for stipend)",
            "Passport-size photograph",
            "Educational certificates (if applicable)",
        ],
        "portal_url": "https://www.pmkvyofficial.org",
        "deadline": "Rolling admissions throughout the year.",
        "tags": ["skill", "training", "employment", "youth", "PMKVY", "job", "certificate",
                 "free training", "vocational", "AI", "coding", "drone"],
    },

    # ── 8. Pension (Social Security) ──────────────────────────────────────────
    {
        "id": "scheme_008",
        "name": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        "category": "Social Security / Pension",
        "ministry": "Ministry of Rural Development",
        "description": (
            "IGNOAPS provides a monthly pension to senior citizens belonging to BPL households. "
            "The scheme is part of the National Social Assistance Programme (NSAP). Persons "
            "aged 60 to 79 years receive Rs. 200 per month from the Centre, and those aged 80 "
            "and above receive Rs. 500 per month. States contribute additional amounts. The "
            "pension is transferred directly to the beneficiary's bank/post office account."
        ),
        "eligibility": {
            "age": "60 years and above",
            "economic_status": "Must belong to a household listed as BPL (Below Poverty Line)",
            "state_authority": "Final selection is made by State/UT governments based on BPL lists",
        },
        "benefits": {
            "central_contribution_60_79_inr_per_month": 200,
            "central_contribution_80_plus_inr_per_month": 500,
            "state_top_up": "Additional amount contributed by respective state governments",
            "payment_mode": "Direct bank transfer or post office account",
        },
        "next_steps": [
            "1. Obtain and fill the IGNOAPS application form from your local Gram Panchayat or Urban Local Body.",
            "2. Submit the form along with required documents to the Gram Panchayat or Block office.",
            "3. The Block Development Officer verifies eligibility and approves the application.",
            "4. After approval, the pension is credited monthly to your bank/post office account.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "Age Proof (Birth Certificate / School Certificate / Medical Certificate)",
            "BPL Card or SECC inclusion proof",
            "Bank account or Post Office passbook details",
            "Passport-size photograph",
        ],
        "portal_url": "https://nsap.nic.in",
        "deadline": "Ongoing — apply at any time through your Gram Panchayat.",
        "tags": ["pension", "old age", "senior citizen", "BPL", "NSAP", "IGNOAPS",
                 "elderly", "monthly support", "retire", "social security"],
    },

    # ── 9. MSME / Small Business ──────────────────────────────────────────────
    {
        "id": "scheme_009",
        "name": "PM SVANidhi — PM Street Vendor's AtmaNirbhar Nidhi",
        "category": "MSME / Micro Finance",
        "ministry": "Ministry of Housing and Urban Affairs",
        "description": (
            "PM SVANidhi is a micro-credit scheme that provides affordable working capital loans "
            "to street vendors who were adversely affected by COVID-19 lockdowns. The scheme aims "
            "to bring street vendors out of debt traps set by moneylenders and enable them to "
            "sustain and grow their livelihoods. Vendors can also earn a 7% interest subsidy "
            "on timely repayment, and benefit from rewards for digital transactions."
        ),
        "eligibility": {
            "who": "Street vendors who were vending in urban areas on or before 24 March 2020.",
            "proof_required": [
                "Certificate of Vending / Identity Card issued by Urban Local Body (ULB)", 
                "OR Letter of Recommendation (LoR) from ULB / Town Vending Committee",
            ],
        },
        "benefits": {
            "initial_loan_inr": 10000,
            "enhanced_loan_2nd_inr": 20000,
            "enhanced_loan_3rd_inr": 50000,
            "interest_subsidy": "7% per annum credited to bank account quarterly",
            "digital_transaction_reward": "Cashback up to Rs. 1,200 per year",
            "collateral": "No collateral required",
        },
        "next_steps": [
            "1. Apply online at pmsvanidhi.mohua.gov.in or via a lending institution (Bank/MFI/SFB).",
            "2. Obtain a Certificate of Vending or Letter of Recommendation from your ULB.",
            "3. Submit completed application with documents to the lending institution.",
            "4. Loan is processed and disbursed within 30 days of application.",
            "5. Repay on time to become eligible for enhanced credit limits.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "Certificate of Vending / Letter of Recommendation from ULB",
            "Bank account details",
            "Passport-size photograph",
            "Mobile number",
        ],
        "portal_url": "https://pmsvanidhi.mohua.gov.in",
        "deadline": "Extended till December 2024 — check portal for current status.",
        "tags": ["street vendor", "hawker", "loan", "micro credit", "SVANidhi", "urban",
                 "business", "covid", "working capital", "digital payment", "rehri patri"],
    },

    # ── 10. Education (Post-Matric) ──────────────────────────────────────────
    {
        "id": "scheme_010",
        "name": "Post-Matric Scholarship for Scheduled Castes (PMS-SC)",
        "category": "Scholarship / Education",
        "ministry": "Ministry of Social Justice and Empowerment",
        "description": (
            "The Post-Matric Scholarship for Scheduled Castes (PMS-SC) provides financial "
            "assistance to SC students studying at post-matriculation or post-secondary stages. "
            "The scheme covers all students enrolled in recognised institutions — from Class 11 "
            "to PhD level — and provides maintenance allowance, study tour charges, thesis "
            "typing/printing charges, and other allowances based on course level."
        ),
        "eligibility": {
            "community": "Scheduled Caste (SC) students only",
            "study_level": "Class 11 / 12, undergraduate, postgraduate, and research/PhD levels",
            "annual_family_income_max_inr": 250000,
            "enrollment": "Must be enrolled in a recognised government or private institution",
            "attendance": "Minimum 75% attendance required",
        },
        "benefits": {
            "maintenance_allowance_hostel": "Rs. 380 – Rs. 1,200 per month (varies by course level)",
            "maintenance_allowance_day_scholar": "Rs. 230 – Rs. 550 per month",
            "study_tour_charges": "Up to Rs. 1,600 per annum (for select courses)",
            "thesis_charges": "Up to Rs. 3,000 (for research scholars)",
        },
        "next_steps": [
            "1. Register on scholarships.gov.in with your Aadhaar and mobile number.",
            "2. Select 'Post-Matric Scholarship for SC Students' from the scheme list.",
            "3. Complete and submit your application before the deadline.",
            "4. Upload required documents (income certificate, caste certificate, marksheet).",
            "5. Track your application via your registered mobile number or the NSP portal.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "SC Caste Certificate from a competent authority",
            "Family Income Certificate",
            "Previous Year Marksheet / Degree Certificate",
            "Admission Fee Receipt / Bonafide Certificate from institution",
            "Bank Passbook (in student's name)",
        ],
        "portal_url": "https://scholarships.gov.in",
        "deadline": "Typically October 31st — check the portal for the latest deadline.",
        "tags": ["scholarship", "SC", "scheduled caste", "post matric", "college",
                 "university", "PhD", "undergraduate", "education", "stipend"],
    },

    # ── 11. Crop Insurance ────────────────────────────────────────────────────
    {
        "id": "scheme_011",
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "category": "Agriculture / Crop Insurance",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": (
            "PMFBY is a comprehensive crop insurance scheme that provides financial support to "
            "farmers suffering crop loss or damage due to unforeseen events like natural calamities, "
            "pests, and diseases. The scheme standardises the premium across all farmers — "
            "maximum 2% for Kharif crops, 1.5% for Rabi crops, and 5% for commercial/horticultural "
            "crops. The balance premium is shared by Central and State governments."
        ),
        "eligibility": {
            "who_can_apply": "All farmers growing notified crops in notified areas — including tenant and sharecropper farmers.",
            "loanee_farmers": "Mandatory enrollment for farmers who have availed Kisan Credit Card (KCC) loans.",
            "non_loanee_farmers": "Optional enrollment — can apply directly via the portal or CSC.",
        },
        "benefits": {
            "farmer_premium_kharif_percent": "Maximum 2% of sum insured",
            "farmer_premium_rabi_percent": "Maximum 1.5% of sum insured",
            "coverage": [
                "Prevented sowing / planting risk",
                "Standing crop loss (mid-season adversity)",
                "Post-harvest losses (up to 14 days)",
                "Localised calamities (hailstorm, landslide, inundation)",
            ],
        },
        "next_steps": [
            "1. Visit pmfby.gov.in or contact your nearest bank / Common Service Centre (CSC).",
            "2. Enroll before the cut-off date for your Kharif or Rabi season.",
            "3. Fill the application form with crop and bank details.",
            "4. Pay the applicable premium amount.",
            "5. Receive the policy document with your unique application number.",
            "6. In case of crop loss, report within 72 hours via the app or your bank.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "Land Records / Khasra-Khatauni",
            "Bank Passbook with IFSC code",
            "Sowing Certificate (from Patwari or self-declaration)",
        ],
        "portal_url": "https://pmfby.gov.in",
        "deadline": "Enrollment deadlines vary by season — check portal for current dates.",
        "tags": ["crop insurance", "farmer", "agriculture", "Kharif", "Rabi", "PMFBY",
                 "natural disaster", "flood", "drought", "pest", "hailstorm"],
    },

    # ── 12. Solar Energy ──────────────────────────────────────────────────────
    {
        "id": "scheme_012",
        "name": "PM Surya Ghar Muft Bijli Yojana (Rooftop Solar Scheme)",
        "category": "Energy / Environment",
        "ministry": "Ministry of New and Renewable Energy",
        "description": (
            "PM Surya Ghar Muft Bijli Yojana is a flagship scheme launched in February 2024 "
            "to promote rooftop solar adoption in residential households. The government provides "
            "substantial subsidies to install solar panels on rooftops, enabling households to "
            "generate their own electricity and receive up to 300 units of free electricity per "
            "month. The scheme targets 1 crore households across India."
        ),
        "eligibility": {
            "who_can_apply": "Any residential household in India with a valid electricity connection.",
            "property": "Own house with a structurally sound roof suitable for solar panel installation.",
        },
        "benefits": {
            "subsidy_up_to_2kw_inr": "Rs. 30,000 per kW (total up to Rs. 60,000)",
            "subsidy_2_to_3kw_inr": "Rs. 18,000 per kW for the additional 1 kW",
            "free_electricity_units": "Up to 300 units per month (based on system size)",
            "net_metering": "Excess electricity can be sold back to the grid",
            "loan_support": "Collateral-free loans available through nationalised banks",
        },
        "next_steps": [
            "1. Register at pmsuryaghar.gov.in with your electricity consumer number.",
            "2. Select an eligible rooftop solar vendor from the approved list.",
            "3. Submit the installation application through the portal.",
            "4. Get technical feasibility approval from your DISCOM (electricity distribution company).",
            "5. Proceed with installation and get net metering connection applied.",
            "6. Apply for the subsidy online — it will be credited directly to your bank account within 30 days.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "Recent electricity bill (with consumer number)",
            "Proof of house ownership",
            "Bank account details",
            "Passport-size photograph",
        ],
        "portal_url": "https://pmsuryaghar.gov.in",
        "deadline": "Ongoing — target to cover 1 crore households by 2027.",
        "tags": ["solar", "energy", "electricity", "rooftop", "subsidy", "environment",
                 "free bijli", "PM Surya Ghar", "renewable", "green energy", "solar panel"],
    },
]