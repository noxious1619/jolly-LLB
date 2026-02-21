from app.rule_engine import check_eligibility
from app.extractor import UserProfile

profile = UserProfile(
    age=14,
    annual_income=80000
)

result = check_eligibility(profile)

print(result)