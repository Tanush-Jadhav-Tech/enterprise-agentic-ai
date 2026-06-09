## Prompt Engineering 

- Prompt engineering is the process of writing effective instructions for a model, such that it consistently generates content that meets your requirements.

- Prompt engineering for IT support

Learn to write prompts that are precise, safe, and production-ready using your real IT support scenarios. By end of day you will have 10 prompt pairs and a reusable enterprise prompt template.

## notes/day03-prompts.md

## Core concepts
5 things to understand today

- Weak prompt

Too much freedom → hallucinations and off-topic answers

- Strong prompt

Role + context + task + constraints + output format

- Enterprise-safe prompt

Explicitly tells the model what it CANNOT do

- Few-shot prompting

2–3 examples inside the prompt to guide format

Prompt anatomy — 5 elements
Role, Context,Task, Constraints, Output format

## Enterprise prompt template
Your reusable template — use this across all projects

    You are an Oracle Enterprise Engineering IT Support Agent with deep expertise in macOS, networking, and enterprise software.

    CONTEXT:
    {ticket_description}

    TASK:
    Analyse the issue and provide a structured diagnosis.

    CONSTRAINTS:
    - Use ONLY the information provided. Do not guess.
    - Never suggest deleting system files without explicit approval.
    - If you cannot determine the issue with confidence, say "Needs human review".
    - Do not run any commands that modify system state.
    - Response must be under 200 words.

    OUTPUT FORMAT (JSON):
    {
    "category": "DISK|UPGRADE|PACKAGING|APPLICATION|NETWORK|UNKNOWN",
    "confidence": 0.0–1.0,
    "findings": "2 sentences max",
    "recommendation": "specific next step",
    "approval_required": true|false
    }
    Role setContext injectedConstraints clearNo guessingJSON output



## 10 prompt pairs — your IT scenarios
Weak vs strong — using your real Oracle EE support cases

1. Low disk space — macOS endpoint
Weak:
Fix the disk space issue on my Mac.

Strong:
You are an Oracle EE macOS support agent. A user reports low disk space on a MacBook Pro M1 (macOS 14.2.1). Check Caches, Trash, and ~/Downloads sizes. List the top 3 folders consuming space. Do NOT delete anything. Respond in JSON: {category, findings, top_folders, recommendation, approval_required}.
RoleContextConstraintOutput format

2. macOS upgrade stuck at 75%
Weak
Help with Mac upgrade failure.

Strong
You are an enterprise macOS support engineer. A macOS 14.4 upgrade has stalled at 75% for 45 minutes on a MacBook Pro (M1 Max, 512GB). Diagnose the most likely causes based on this stage. Do not recommend force-restart without approval. Provide: probable_cause, safe_first_step, approval_required.
ContextConstraintFormat

3. Citrix workspace not launching
Weak
Citrix is broken, fix it.

Strong
You are an enterprise application support agent. Citrix Workspace 23.9 crashes immediately on launch on macOS 14.2. No error dialog shown. Last working: 2 days ago. No recent OS update. Diagnose: list 3 probable causes in order of likelihood. For each: describe the verification step and required approval level (user/IT/none).
ContextFew-shot structureRanked output

4. Package install failure — notarization error
Weak
Package install is failing.

Strong
You are an Oracle EE packaging support agent. A .pkg install fails with ERR_NOTARIZATION_FAILED on macOS 14.2. The package is an internal Oracle tool signed with an enterprise cert. Internet access is available. Diagnose whether this is a Gatekeeper issue, cert expiry, or network block. Reply with: root_cause_hypothesis, verification_command (read-only only), escalation_path.
Read-only constraintContextFormat

5. Application crash on launch
Weak
App is crashing, what do I do?

Strong
You are a macOS application support agent. Zoom 5.17 crashes on launch on macOS 14.1 (Intel). Crash log shows: EXC_BAD_ACCESS KERN_INVALID_ADDRESS. Last successful launch was yesterday. No recent Zoom update. Based ONLY on this crash type: list probable causes and the safest non-destructive diagnostic step for each.
Evidence-onlyNon-destructive constraint

6. Network connectivity — intermittent
Weak
Network keeps dropping.

Strong
You are an enterprise network support agent. A MacBook Pro drops WiFi every 20–30 minutes on a corporate WPA2 network. Other devices on the same network are stable. Issue began after macOS 14.3 update. Propose 3 diagnostic steps in order — read-only, no configuration changes. For each: what to run and what result confirms or rules out that cause.
No config changesOrdered steps

7. User locked out of SSO
Weak
User can't login.

Strong
You are an enterprise identity support agent. A user cannot authenticate via Okta SSO. Error: "Your session has expired." Browser cache has been cleared. Issue is only on Chrome, not Safari. No recent password change. Diagnose: is this a browser issue, Okta policy issue, or cert issue? Provide next step for each hypothesis. Do not suggest resetting credentials without manager approval.
Approval constraintMulti-hypothesis

8. High CPU — unknown process
Weak
CPU is high, which process?

Strong
You are a macOS performance support agent. Activity Monitor shows mds_stores consuming 85% CPU on a MacBook Pro M2. This started after a macOS Spotlight re-index was triggered. Duration: 3 hours. Disk is 90% full. Based ONLY on this data: explain the likely cause, state whether this requires intervention, and if yes — the safest approved action. Do not recommend force-kill without confirmation.
Evidence-onlySafe action constraint

9. Printer not found after macOS update
Weak
Printer disappeared after update.

Strong
You are an enterprise print support agent. An HP LaserJet Pro M404dn disappeared from System Preferences after macOS 14.3 update. The printer is network-connected and visible to other users. Driver version was HP 5.1. List: most likely cause of this disappearance post-update, verification step (read-only), and whether re-adding the printer requires IT involvement.
ContextRoleFormat

10. VPN not connecting from specific location
Weak
VPN not working.

Strong
You are an enterprise VPN support agent. Cisco AnyConnect 4.10 fails to connect from a home network but works from office and other locations. Error: "Connection attempt has timed out." VPN works on the same machine using a mobile hotspot. Diagnose: is this a home router/ISP block, split-tunnel policy issue, or MTU problem? For each: one read-only verification step. Reply in JSON: {hypotheses: [{cause, verification, probability}]}.
Few-shot JSONRead-onlyProbability scoring


## Interview questions to prepare
3 questions from your roadmap — with answers

Q1 — What makes a prompt production-safe vs demo-only?
A demo prompt gets a good-looking answer on a clean input. A production-safe prompt handles bad inputs gracefully — it has explicit constraints (no guessing, no destructive actions without approval), a defined fallback for low-confidence cases, and a fixed output schema that downstream systems can parse. In my Oracle EE support tool, every prompt includes "if you cannot determine with confidence, return needs_human_review" — that is the production safety net.

Q2 — Show me a weak prompt and explain how you improved it
Weak: "Fix the disk space issue on my Mac." — No role, no context, no output format, no constraints.

Strong: "You are an Oracle EE macOS support agent. A user reports low disk space on MacBook Pro M1 (macOS 14.2.1). List top 3 folders consuming space. Do NOT delete anything. Respond in JSON: {category, findings, top_folders, recommendation, approval_required}."

What improved it: Role (who the agent is), Context (what machine and OS), Constraint (no deletion), Output format (JSON schema). Each addition removes one degree of freedom from the model's response.

Q3 — What is few-shot prompting and when would you use it?
Few-shot prompting means giving the model 2–3 worked examples inside the prompt so it learns the exact pattern you want — not from training, but from the examples in front of it. I use it when the output format is complex or unusual, for example when classifying a ticket AND returning a confidence score AND a one-line reason all in one JSON object. One example in the prompt shows the model exactly what that JSON should look like, and it follows the pattern reliably without needing fine-tuning.