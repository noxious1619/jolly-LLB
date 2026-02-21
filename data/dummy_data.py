

SCHEMES = [
    {
        "id": "scheme_001",
        "name": "National Scholarship Portal (NSP) — Pre-Matric Scholarship",
        "category": "Scholarship",
        "ministry": "Ministry of Education, Government of India",
        "description": (
            "NSP Pre-Matric Scholarship ek Central Government ki scheme hai jo minority "
            "communities ke Class 1 se Class 10 tak padhne wale students ko financial "
            "help deti hai. Iska maqsad economically weaker sections ke bachon ko school "
            "mein rokna aur unhe aage padhne ke liye motivate karna hai. "
            "Scholarship mein tuition fees, maintenance allowance, aur book grant shamil hain."
        ),
        "eligibility": {
            "community": ["Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Zoroastrian"],
            "class_range": "Class 1 to Class 10",
            "annual_family_income_max_inr": 100000,
            "minimum_attendance_percent": 75,
            "institution_type": "Government or Government-aided school",
        },
        "benefits": {
            "day_scholar_monthly": "Rs. 100 – Rs. 500 per month (class-wise)",
            "hosteller_monthly": "Rs. 600 – Rs. 1,200 per month (class-wise)",
            "adhoc_grant": "Rs. 500 per annum for books & stationery",
        },
        "next_steps": [
            "1. Visit scholarships.gov.in and click 'New Registration'.",
            "2. Register with your Aadhaar number and mobile number.",
            "3. Fill in personal, academic, and bank account details.",
            "4. Upload: Income Certificate, Minority Certificate, Marksheet, Fee Receipt.",
            "5. Submit and note your Application ID for tracking.",
            "6. Await school/institution verification, then district-level approval.",
        ],
        "required_documents": [
            "Aadhaar Card",
            "Community / Minority Certificate from competent authority",
            "Family Income Certificate (annual)",
            "Previous Year Marksheet",
            "Bank Passbook (student's name or joint with parent)",
            "Current Year School Fee Receipt",
        ],
        "portal_url": "https://scholarships.gov.in",
        "deadline": "Typically October 31st each year — check portal for current deadline.",
        "tags": ["scholarship", "minority", "student", "education", "class 1 to 10",
                 "income below 1 lakh", "NSP", "girls", "boys"],
    },
    {
        "id": "scheme_002",
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "category": "Farming / Agriculture",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": (
            "PM-KISAN ek Central Government scheme hai jo har land-holding kisan "
            "family ko Rs. 6,000 per year ki income support deti hai. Yeh amount "
            "teen installments mein — Rs. 2,000 har chaar mahine mein — seedha kisan "
            "ke bank account mein Direct Benefit Transfer (DBT) se aata hai. "
            "Scheme ka maqsad kisan ko beej, khaad, aur agricultural inputs kharidne "
            "mein madad karna hai."
        ),
        "eligibility": {
            "who_can_apply": "All farmer families with cultivable land as per land records.",
            "land_size": "No upper limit on land size (small, marginal, and large farmers all eligible).",
            "excluded_categories": [
                "Institutional Landholders",
                "Former/current Ministers, MPs, MLAs, Constitutional post holders",
                "Retired government employees (except Class IV / MTS / Group D)",
                "Income Tax payers",
                "Professionals: Doctors, Engineers, Lawyers, CAs, Architects",
            ],
        },
        "benefits": {
            "annual_support_inr": 6000,
            "installment_amount_inr": 2000,
            "installment_schedule": [
                "April – July",
                "August – November",
                "December – March",
            ],
            "payment_mode": "Direct Bank Transfer (DBT)",
        },
        "next_steps": [
            "1. Visit pmkisan.gov.in → 'Farmers Corner' → 'New Farmer Registration'.",
            "2. Select Rural or Urban Farmer; enter Aadhaar number.",
            "3. Enter land details, bank account details, and personal information.",
            "4. Verify with OTP sent to your Aadhaar-linked mobile number.",
            "5. Await verification by local Patwari / Revenue official.",
            "6. Alternatively, register at your nearest Common Service Centre (CSC).",
        ],
        "required_documents": [
            "Aadhaar Card (mandatory)",
            "Land Records — Khasra / Khatauni document",
            "Bank Passbook with IFSC code",
            "Mobile number linked to Aadhaar",
        ],
        "portal_url": "https://pmkisan.gov.in",
        "deadline": "Open registration throughout the year. Installments released quarterly.",
        "tags": ["farmer", "kisan", "agriculture", "farming", "land", "6000 rupees",
                 "DBT", "PM Kisan", "annual support", "rural"],
    },
    {
        "id": "scheme_003",
        "name": "Startup India Seed Fund Scheme (SISFS)",
        "category": "Startup / Entrepreneurship",
        "ministry": "Ministry of Commerce and Industry (DPIIT)",
        "description": (
            "Startup India Seed Fund Scheme (SISFS) early-stage startups ko financial "
            "assistance deti hai — proof of concept, prototype development, market entry, "
            "aur commercialization ke liye. Funds selected incubators ke zariye diye jaate "
            "hain, jo eligible startups ko grant ya investment ke roop mein support karte "
            "hain. Yeh scheme un innovative startups ki help karti hai jo institutional "
            "funding pane mein mushkil face karte hain."
        ),
        "eligibility": {
            "dpiit_recognition": "Must be a DPIIT-recognized startup (register at startupindia.gov.in).",
            "startup_age_max_years": 2,
            "incorporation_types": ["Private Limited Company", "LLP", "Partnership Firm"],
            "prior_government_funding_max_inr": 1000000,
            "requirements": [
                "Must have a viable product/service with market fit.",
                "Clear scope of commercialization required.",
                "Promoters must not be part of another startup receiving SISFS grants.",
            ],
        },
        "benefits": {
            "grant_for_poc_prototype_inr": 2000000,
            "investment_for_commercialization_inr": 5000000,
            "total_scheme_corpus_inr": "Rs. 945 Crore (2021–2025)",
            "instrument": "Grants + Convertible Debentures / Debt-linked instruments",
        },
        "next_steps": [
            "1. Ensure DPIIT recognition — register at startupindia.gov.in if not done.",
            "2. Visit the Startup India portal and navigate to the SISFS section.",
            "3. Browse the empanelled incubator list and apply to a suitable incubator.",
            "4. Submit application: business plan, pitch deck, and financial projections.",
            "5. Incubator selection committee will evaluate and conduct due diligence.",
            "6. If selected, funds are released in tranches based on agreed milestones.",
        ],
        "required_documents": [
            "DPIIT Recognition Certificate",
            "Certificate of Incorporation",
            "Pitch Deck / Business Plan",
            "Founders' KYC documents",
            "Startup bank account details",
            "Prototype / PoC details (if available)",
            "Financial Projections for next 3 years",
        ],
        "portal_url": "https://www.startupindia.gov.in/content/sih/en/funding.html",
        "deadline": "Rolling applications — check with specific empanelled incubators.",
        "tags": ["startup", "entrepreneur", "seed fund", "DPIIT", "incubator",
                 "funding", "prototype", "commercialization", "SISFS", "business"],
    },
]