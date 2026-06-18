"""
Day 15 — Test the approval gate.
Tests both SAFE (auto-run) and RISKY (approval required) paths.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import approval_gate, is_risky, SAFE_ACTIONS, RISKY_ACTIONS

print("\n" + "="*60)
print("APPROVAL GATE — TEST RUN")
print("="*60)

# Test 1 — is_risky() function
print("\n[TEST 1] is_risky() checks")
for tool in SAFE_ACTIONS:
    result = is_risky(tool)
    status = "❌ WRONG" if result else "✅ SAFE"
    print(f"  {status}: is_risky('{tool}') = {result}")

for tool in RISKY_ACTIONS:
    result = is_risky(tool)
    status = "✅ RISKY" if result else "❌ WRONG"
    print(f"  {status}: is_risky('{tool}') = {result}")

# Test 2 — approval_gate() function
print("\n[TEST 2] Live approval gate test")
print("You will be asked to approve or decline a test action.")
print("Type 'yes' to approve or 'no' to decline.\n")

approved = approval_gate(
    action_name="clear_cache",
    details=(
        "About to delete ~/Library/Caches to free 18.2 GB.\n"
        "Ticket: My MacBook disk is 95% full.\n"
        "Category: DISK (confidence: 0.99)"
    )
)

if approved:
    print("\n✅ Test result: Action APPROVED")
    print("   In production: clear_cache_mac.sh would run now")
else:
    print("\n✅ Test result: Action DECLINED")
    print("   In production: no files would be deleted")

print("\n[TEST 3] Full process_ticket() with approval gate")
print("Running a DISK ticket — check_disk_space() is SAFE")
print("It should run automatically without asking for approval.\n")

from app import process_ticket
result = process_ticket("My MacBook Pro says the startup disk is almost full")
print(f"\nFinal status: {result['tool_result'].get('status', 'completed')}")