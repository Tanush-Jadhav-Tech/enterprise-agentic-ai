"""
Automation Support Agent — Diagnostic Tools Layer
Safe read-only tools for IT diagnostics.
Risky tools require approval gate before execution.
All tools return structured dicts for agent reasoning.
Oracle Enterprise Engineering — Agentic AI Portfolio Project
"""

import datetime
import random


# ── SAFE TOOLS (auto-run — no approval needed) ────────────────────────────────

def check_disk_space() -> dict:
    """
    Check available disk space on the primary volume.
    Safe, read-only. Returns structured disk usage data.

    Used for: DISK category tickets
    Risk level: SAFE — no system changes
    """
    return {
        "volume":       "Macintosh HD",
        "total_gb":     512,
        "used_gb":      487,
        "free_gb":      25,
        "percent_used": 95.1,
        "critical":     True,
        "top_consumers": [
            {"path": "~/Library/Caches",   "size_gb": 18.2},
            {"path": "~/Downloads",         "size_gb": 22.4},
            {"path": "~/Library/Developer", "size_gb": 14.6},
        ],
        "checked_at": datetime.datetime.now().isoformat(),
    }


def check_os_version() -> dict:
    """
    Return the current macOS version and pending updates.
    Safe, read-only. Returns OS details and upgrade status.

    Used for: UPGRADE and PACKAGING category tickets
    Risk level: SAFE — no system changes
    """
    return {
        "os_name":        "macOS",
        "version":        "14.2.1",
        "build":          "23C71",
        "architecture":   "arm64 (Apple Silicon)",
        "pending_update": "14.4",
        "update_size_gb": 3.8,
        "update_required": True,
        "last_checked":   datetime.datetime.now().isoformat(),
    }


def check_running_processes() -> dict:
    """
    List top CPU-consuming processes on the system.
    Safe, read-only. Returns process list with CPU percentages.

    Used for: APPLICATION and NETWORK category tickets
    Risk level: SAFE — no system changes
    """
    return {
        "top_processes": [
            {"pid": 1234, "name": "kernel_task",      "cpu_pct": 45.2, "mem_mb": 512},
            {"pid": 5678, "name": "Citrix Workspace", "cpu_pct": 38.1, "mem_mb": 1024},
            {"pid": 9012, "name": "mds_stores",       "cpu_pct": 12.4, "mem_mb": 256},
            {"pid": 3456, "name": "Zoom",             "cpu_pct":  4.2, "mem_mb": 384},
        ],
        "total_cpu_usage_pct": 99.9,
        "total_ram_gb":        16,
        "used_ram_gb":         14.2,
        "sampled_at":          datetime.datetime.now().isoformat(),
    }


def read_sample_log(path: str = "sample.log") -> dict:
    """
    Read a log file and return last 20 lines with error summary.
    Safe, read-only. Returns structured log analysis data.

    Used for: all categories — log evidence gathering
    Risk level: SAFE — no system changes
    """
    sample_lines = [
        "2024-01-15 09:22:00 INFO  Starting upgrade process...",
        "2024-01-15 09:22:05 INFO  Downloading macOS 14.4 (3.8 GB)...",
        "2024-01-15 09:35:22 ERROR Download failed: disk full",
        "2024-01-15 09:35:23 ERROR Upgrade aborted: insufficient space (need 35GB, have 22GB)",
        "2024-01-15 09:35:24 WARN  Rolling back to previous state",
        "2024-01-15 09:36:01 INFO  Rollback complete",
        "2024-01-15 09:36:02 INFO  System restored to macOS 14.2.1",
    ]
    errors   = [l for l in sample_lines if "ERROR" in l]
    warnings = [l for l in sample_lines if "WARN"  in l]

    return {
        "path":         path,
        "total_lines":  len(sample_lines),
        "error_count":  len(errors),
        "warn_count":   len(warnings),
        "errors":       errors,
        "warnings":     warnings,
        "last_lines":   sample_lines[-5:],
        "read_at":      datetime.datetime.now().isoformat(),
    }


def check_package_status(package_name: str = "CompanyVPN") -> dict:
    """
    Check installation status of a named package.
    Safe, read-only. Returns package details and last error.

    Used for: PACKAGING category tickets
    Risk level: SAFE — no system changes
    """
    return {
        "package":          package_name,
        "installed":        False,
        "version":          None,
        "last_attempt":     "2024-01-15T09:23:11",
        "error_code":       "ERR_NOTARIZATION_FAILED",
        "error_detail":     "Package not notarized by Apple. "
                            "Contact IT admin to re-sign the package.",
        "requires_approval": True,
        "checked_at":       datetime.datetime.now().isoformat(),
    }


# ── RISKY TOOLS (approval required — always) ──────────────────────────────────

def clear_cache() -> dict:
    """
    Clear ~/Library/Caches to free disk space.
    RISKY — permanently deletes files. Requires approval gate.

    Used for: DISK category — remediation action
    Risk level: RISKY — permanent deletion, cannot be undone
    """
    # Mock implementation — real version calls clear_cache_mac.sh
    return {
        "status":        "success",
        "tool":          "clear_cache_mac.sh",
        "target":        "~/Library/Caches",
        "freed_gb":      18.2,
        "files_deleted": 4821,
        "executed_at":   datetime.datetime.now().isoformat(),
        "note":          "Mock result — real tool calls clear_cache_mac.sh --auto"
    }


def reinstall_package(package_name: str = "CompanyVPN") -> dict:
    """
    Reinstall a named package from the enterprise software catalogue.
    RISKY — modifies system state. Requires approval gate.

    Used for: PACKAGING category — remediation action
    Risk level: RISKY — modifies installed software
    """
    return {
        "status":        "success",
        "package":       package_name,
        "version":       "2.1.0",
        "installed_at":  datetime.datetime.now().isoformat(),
        "note":          "Mock result — real tool calls enterprise pkg installer"
    }


# ── TOOL REGISTRY ─────────────────────────────────────────────────────────────

# Maps issue category to the correct diagnostic tool function
TOOL_REGISTRY = {
    "DISK":        check_disk_space,
    "UPGRADE":     check_os_version,
    "PACKAGING":   check_package_status,
    "APPLICATION": check_running_processes,
    "NETWORK":     check_running_processes,
    # UNKNOWN → None — no tool, route to human review
}

# Safe tools — auto-run without approval
SAFE_TOOLS = [
    "check_disk_space",
    "check_os_version",
    "check_running_processes",
    "read_sample_log",
    "check_package_status",
]

# Risky tools — always require approval gate before execution
RISKY_TOOLS = [
    "clear_cache",
    "reinstall_package",
    "force_reboot",
    "run_cleanup_script",
]