# Evaluation Cases — Automation Support Agent

> Test cases with expected outputs.
> Pass/Fail column filled on Day 17 after agent is complete.

| # | Ticket | Expected Category | Expected Tool | Actual Category | Pass? | Notes |
|---|---|---|---|---|---|---|
| 1 | My Mac says startup disk almost full | DISK | check_disk_space | - | - | |
| 2 | Citrix crashes immediately on launch | APPLICATION | check_running_processes | - | - | |
| 3 | macOS upgrade stuck at 75% | UPGRADE | check_os_version | - | - | |
| 4 | VPN package notarization failed | PACKAGING | check_os_version | - | - | |
| 5 | My laptop is slow | DISK | check_disk_space | - | - | Ambiguous — low confidence expected |
| 6 | Cannot connect to VPN from home | NETWORK | check_running_processes | - | - | |
| 7 | Error code 11001 | UNKNOWN | none — human review | - | - | No context — should return UNKNOWN |
| 8 | Everything is broken | UNKNOWN | none — human review | - | - | Vague — should escalate |
| 9 | My computer is hot | UNKNOWN/APPLICATION | check_running_processes | - | - | Ambiguous — could be DISK or APPLICATION |
| 10 | Zoom crashes only on video calls | APPLICATION | check_running_processes | - | - | |
