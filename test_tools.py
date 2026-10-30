from tools import check_fee_status, check_scholarship_status

print("Fee status:")
print(check_fee_status("STU001"))

print("\nScholarship status:")
print(check_scholarship_status("STU002"))

print("\nTesting missing student:")
print(check_fee_status("STU999"))