"""
load_schemes.py — Real scheme loader from HuggingFace Dataset
Dataset: shrijayan/gov_myscheme (723 real Indian government scheme PDFs from myscheme.gov.in)

Strategy:
  1. Use huggingface_hub to list all PDF files in the dataset repo.
  2. Download each PDF (non-copy, primary files only).
  3. Extract text via pypdf.
  4. Parse the extracted text into the JOLLY-LLB SCHEMES schema.
  5. Falls back to dummy_data.py if anything fails.

Note: On first run this downloads ~35 MB of PDFs and caches them locally.
      Subsequent runs are instant (cached in HuggingFace's local cache).
"""

import re
import os


# ─────────────────────────────────────────────────────────────────────────────
# Text Utilities
# ─────────────────────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    """Normalize whitespace in extracted text."""
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _extract_section(text: str, *section_headers: str, max_chars: int = 600) -> str:
    """
    Extract text under a section heading from the raw PDF text.
    Tries each header alias in order, returns the first match.
    """
    for header in section_headers:
        # Case-insensitive match; grab text until next all-caps heading or end
        pattern = rf'(?i){re.escape(header)}\s*[:\-]?\s*\n?(.*?)(?=\n[A-Z][A-Z ]+[:\n]|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            val = _clean(match.group(1))
            if val:
                return val[:max_chars]
    return ""


def _extract_url(text: str) -> str:
    """Find the first https URL in text."""
    match = re.search(r'https?://[^\s\)\"\']+', text)
    return match.group(0).rstrip('.,') if match else "https://www.myscheme.gov.in"


def _extract_scheme_name(text: str, filename_stem: str) -> str:
    """Try to get scheme name from the first non-empty line of the PDF."""
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 8 and not line.startswith('http') and not re.match(r'^[A-Z0-9\-]+$', line):
            return line[:120]
    # Fall back to filename-based name
    return filename_stem.replace('-', ' ').replace('_', ' ').upper()


def _build_tags(name: str, text: str) -> list:
    """Generate search tags from scheme name and content keywords."""
    tags = set()

    keywords = [
        'scholarship', 'student', 'education', 'farmer', 'kisan', 'agriculture',
        'pension', 'widow', 'disabled', 'pwd', 'sc', 'st', 'obc', 'minority',
        'health', 'housing', 'women', 'mahila', 'startup', 'business', 'msme',
        'skill', 'training', 'loan', 'subsidy', 'insurance', 'employment',
        'labour', 'senior citizen', 'girl', 'child', 'rural', 'urban',
        'tribal', 'backward', 'income', 'financial assistance', 'stipend',
    ]
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            tags.add(kw)

    # Add meaningful words from name
    for word in name.lower().split():
        if len(word) > 3 and word not in ('scheme', 'yojana', 'pradhan', 'mantri', 'national'):
            tags.add(word)

    return list(tags)[:12]


# ─────────────────────────────────────────────────────────────────────────────
# PDF → Scheme Mapper
# ─────────────────────────────────────────────────────────────────────────────

def _pdf_bytes_to_scheme(pdf_bytes: bytes, idx: int, filename_stem: str) -> dict | None:
    """Parse raw PDF bytes into a scheme dict. Returns None on failure."""
    try:
        import io
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages_text = []
        for page in reader.pages[:6]:  # Read up to 6 pages (most scheme PDFs are 1-3 pages)
            pages_text.append(page.extract_text() or "")
        text = _clean("\n".join(pages_text))

        if len(text) < 30:
            return None  # PDF has no extractable text

        # ── Extract Fields ──────────────────────────────────────────────────
        name = _extract_section(text, 'Scheme Name', 'Name of Scheme', 'Scheme') or \
               _extract_scheme_name(text, filename_stem)

        description = _extract_section(
            text,
            'Brief Description', 'Description', 'About the Scheme',
            'Objective', 'Overview',
            max_chars=800
        ) or text[:500]

        ministry = _extract_section(text, 'Ministry', 'Department', 'Nodal Ministry', max_chars=150) \
                   or "Government of India"

        category = _extract_section(text, 'Tags', 'Category', 'Sector', 'Benefit Type', max_chars=100) \
                   or "General"

        # Eligibility — combine multiple fields
        eligibility_raw = _extract_section(
            text,
            'Eligibility', 'Eligibility Criteria', 'Who Can Apply',
            'Target Beneficiaries', 'Beneficiary Type',
            max_chars=600
        )
        eligibility = {"criteria": eligibility_raw} if eligibility_raw \
            else {"general": "Check official portal for eligibility details."}

        # Other eligibility sub-fields
        for field, keys in [
            ("age", ["Age", "Age Limit"]),
            ("gender", ["Gender"]),
            ("caste", ["Caste", "Category"]),
            ("income_limit", ["Income", "Annual Income", "Family Income"]),
            ("state", ["State", "Applicability"]),
        ]:
            val = _extract_section(text, *keys, max_chars=100)
            if val:
                eligibility[field] = val

        benefits_raw = _extract_section(
            text,
            'Benefits', 'Scheme Benefit', 'Financial Assistance', 'Incentive',
            'What You Get', 'Amount',
            max_chars=500
        )
        benefits = {"details": benefits_raw} if benefits_raw \
            else {"details": "Refer to official portal for benefit details."}

        process_raw = _extract_section(
            text,
            'Application Process', 'How to Apply', 'Application Procedure',
            'Procedure', 'Steps to Apply',
            max_chars=600
        )
        if process_raw:
            steps = [s.strip() for s in re.split(r'\n|(?<=[.?])\s+(?=\d+[\.\)])', process_raw) if s.strip()]
            next_steps = steps[:6] if steps else [process_raw[:300]]
        else:
            next_steps = ["Visit the official portal to apply."]

        docs_raw = _extract_section(
            text,
            'Documents Required', 'Required Documents', 'Documents Needed',
            'Documents', 'Attachments',
            max_chars=400
        )
        if docs_raw:
            required_documents = [d.strip() for d in re.split(r',|\n|•|-', docs_raw) if d.strip()][:8]
        else:
            required_documents = ["Aadhaar Card", "Relevant supporting documents (check official portal)"]

        portal_url = _extract_url(text)

        deadline = _extract_section(text, 'Deadline', 'Last Date', 'Application Deadline', max_chars=120) \
                   or "Check official portal for current deadlines."

        return {
            "id": f"scheme_{idx:04d}",
            "name": name.strip(),
            "category": category.strip(),
            "ministry": ministry.strip(),
            "description": description.strip(),
            "eligibility": eligibility,
            "benefits": benefits,
            "next_steps": next_steps,
            "required_documents": required_documents,
            "portal_url": portal_url,
            "deadline": deadline.strip(),
            "tags": _build_tags(name, text),
        }

    except Exception as e:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Main Loader
# ─────────────────────────────────────────────────────────────────────────────

def load_real_schemes(max_schemes: int = None) -> list:
    """
    Download and return schemes from the HuggingFace dataset.

    Args:
        max_schemes: Limit the number of schemes loaded (None = load all).
                     Use a smaller number (e.g. 50) for faster loading during testing.

    Returns:
        List of scheme dicts compatible with the JOLLY-LLB SCHEMES schema.
    """
    try:
        from huggingface_hub import hf_hub_download, list_repo_files

        repo_id = "shrijayan/gov_myscheme"
        repo_type = "dataset"

        print(f"📂 Listing files in {repo_id}...")
        all_files = list(list_repo_files(repo_id, repo_type=repo_type))

        # Filter: only primary PDFs (exclude " copy.pdf" duplicates), in text_data/
        pdf_files = [
            f for f in all_files
            if f.startswith("text_data/")
            and f.endswith(".pdf")
            and " copy" not in f
            and "(1)" not in f
            and "(2)" not in f
            and "(3)" not in f
        ]

        if max_schemes:
            pdf_files = pdf_files[:max_schemes]

        total = len(pdf_files)
        print(f"✅ Found {total} unique scheme PDFs. Downloading and parsing...")
        print("   (First run downloads ~30MB and caches locally — subsequent runs are instant)")

        schemes = []
        failed = 0

        for idx, filepath in enumerate(pdf_files, start=1):
            try:
                # Download (cached in ~/.cache/huggingface)
                local_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=filepath,
                    repo_type=repo_type,
                    quiet=True,
                )
                with open(local_path, "rb") as f:
                    pdf_bytes = f.read()

                stem = os.path.splitext(os.path.basename(filepath))[0]
                scheme = _pdf_bytes_to_scheme(pdf_bytes, idx, stem)

                if scheme and scheme.get("name"):
                    schemes.append(scheme)
                    if idx % 50 == 0:
                        print(f"   📄 Parsed {idx}/{total} schemes...")
                else:
                    failed += 1

            except Exception as e:
                failed += 1
                continue

        print(f"\n✅ Successfully parsed {len(schemes)} schemes ({failed} failed/skipped).")
        return schemes if schemes else _fallback()

    except Exception as e:
        print(f"⚠️  Could not load real schemes: {e}")
        return _fallback()


def _fallback() -> list:
    """Return dummy data as a fallback."""
    print("   Falling back to dummy_data.py...")
    try:
        from data.dummy_data import SCHEMES
        return SCHEMES
    except ImportError:
        return []


def get_schemes(max_schemes: int = None) -> list:
    """Convenience alias used by ingest.py."""
    return load_real_schemes(max_schemes=max_schemes)


# ─────────────────────────────────────────────────────────────────────────────
# Quick Test (run this file directly to preview 5 schemes)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Testing real scheme loader (first 5 schemes)...")
    print("=" * 60)
    schemes = load_real_schemes(max_schemes=5)
    print(f"\nLoaded {len(schemes)} scheme(s):\n")
    for s in schemes:
        print(f"  [{s['id']}] {s['name']}")
        print(f"       Category : {s['category']}")
        print(f"       Ministry : {s['ministry']}")
        print(f"       Tags     : {s['tags'][:5]}")
        desc = s['description'][:100].replace('\n', ' ')
        print(f"       Desc     : {desc}...")
        print()
