"""
Management command to populate release notes with curated version history.

Usage:
    python manage.py populate_release_notes              # Dry-run (print only)
    python manage.py populate_release_notes --apply      # Actually create records
    python manage.py populate_release_notes --clear      # Delete all then re-populate
"""

from datetime import date

from django.core.management.base import BaseCommand

from api.models import ReleaseNote

# Curated release notes written for end-users.
# Focused on what changed from the user's perspective, not technical internals.
RELEASE_NOTES = [
    {
        "version": "1.0.0",
        "release_date": date(2025, 1, 24),
        "status": "stable",
        "summary": "First release of the Overtime Management Portal with core request and approval features.",
        "new_features": [
            "Submit, edit, and track overtime requests with a step-by-step form",
            "Manager approval workflow — requests move through review stages automatically",
            "Employee directory with department and role information",
            "Project list with overtime hour tracking per project",
            "Dashboard overview showing your recent requests and team statistics",
            "Sign in with your company credentials — no separate account needed",
        ],
        "improvements": [],
        "bug_fixes": [],
        "breaking_changes": [],
        "security": [
            "All sessions are secured and expire after 24 hours of inactivity",
        ],
    },
    {
        "version": "1.1.0",
        "release_date": date(2025, 7, 20),
        "status": "stable",
        "summary": "Added a shared calendar, regulation documents, and live notifications.",
        "new_features": [
            "Shared calendar for team events, meetings, and important dates",
            "View and download company overtime regulations directly in the portal",
            "Holiday calendar showing public holidays and team leave schedules",
            "Live notifications — get notified instantly when a request is approved or updated",
        ],
        "improvements": [
            "Easier to find employees with improved search and department filters",
            "Calendar events now display with color labels and priority indicators",
            "Cleaner project detail pages with better data organization",
        ],
        "bug_fixes": [
            "Dates now display correctly regardless of your timezone",
            "Department hierarchy shows properly in the organization view",
        ],
    },
    {
        "version": "1.2.0",
        "release_date": date(2025, 9, 1),
        "status": "stable",
        "summary": "Introduced the Task Board for team collaboration and personal notes.",
        "new_features": [
            "Kanban-style Task Board — organize work by dragging tasks between columns",
            "Add comments on tasks to discuss progress with your team",
            "Break tasks into subtasks and track time spent on each",
            "Personal Notes section for your own reminders and quick notes",
            "Attach files and documents to tasks for easy reference",
            "Set reminders on tasks so you never miss a deadline",
        ],
        "improvements": [
            "Notifications now show read/unread status so you can catch up quickly",
            "More reliable live updates when multiple people work on the same board",
        ],
        "bug_fixes": [
            "Calendar events with repeat schedules now save correctly",
            "Notifications arrive in the right order",
        ],
    },
    {
        "version": "2.0.0",
        "release_date": date(2025, 11, 15),
        "status": "stable",
        "summary": "Complete redesign with a modern interface, plus new Purchasing and Asset Management modules.",
        "new_features": [
            "Brand new modern interface — cleaner, faster, and easier to navigate",
            "Purchase Request module — submit and track procurement requests",
            "Asset Management — view and track company equipment and resources",
            "Dark mode — switch to a dark theme for comfortable viewing",
            "Mobile-friendly — access the portal from your phone or tablet",
            "Admin Dashboard for super admins to manage system settings",
        ],
        "improvements": [
            "Pages load significantly faster across the entire application",
            "New collapsible sidebar for more screen space when you need it",
            "Better tables with sorting, filtering, and quick search",
            "Calendar now offers Year, Month, and Week views",
        ],
        "breaking_changes": [
            "Interface has been completely redesigned — pages may look different from before",
        ],
        "security": [
            "Improved session security and connection handling",
        ],
    },
    {
        "version": "2.1.0",
        "release_date": date(2025, 12, 20),
        "status": "stable",
        "summary": "Faster overtime lists, better exports, and calendar improvements.",
        "new_features": [
            "Enhanced Excel export with color-coded statuses and formatted cells",
            "Calendar Year view with hover previews on each date",
            "Calendar Week view now uses the full screen width",
            "Event reminders — get reminded about upcoming calendar events",
        ],
        "improvements": [
            "Overtime list loads much faster, especially with large datasets",
            "Numbers (hours, costs) now display with proper formatting for easier reading",
            "Tables scroll smoothly on mobile devices",
            "Leave entries on the calendar show clearer date ranges",
            "Improved breadcrumb navigation throughout the portal",
        ],
        "bug_fixes": [
            "Fixed an issue where some pages would redirect incorrectly after login",
            "Fixed occasional page loading errors on slow connections",
            "Fixed employee leave display not showing some team members",
        ],
    },
    {
        "version": "2.2.0",
        "release_date": date(2026, 1, 15),
        "status": "stable",
        "summary": "Network file sharing, version history page, and a way to report issues directly from the portal.",
        "new_features": [
            "Exported Excel files can now be saved directly to a shared network folder",
            "Multiple network share configurations — easily switch between different servers",
            "This Release Notes page — see what's new in every version at a glance",
            "Report an Issue — submit bug reports or feature requests right from the sidebar",
            "Super Admins can manage network share settings from the dashboard",
            "Super Admins can review and respond to user-submitted reports",
            "Version number in the footer links to this page for quick access",
        ],
        "improvements": [
            "Network configuration is loaded more efficiently to avoid slowing down exports",
            "System settings load only once per session instead of on every page",
            "Export feature gracefully falls back to default settings if network config is unavailable",
        ],
        "bug_fixes": [
            "Fixed missing database tables that caused errors on first deployment",
            "Network share settings now support multiple configurations instead of just one",
        ],
        "security": [
            "Network share passwords are encrypted before being stored",
            "Only super admins can access network configuration and report management",
        ],
    },
    {
        "version": "2.3.0",
        "release_date": date(2026, 2, 18),
        "status": "stable",
        "summary": "Performance improvements, real-time report notifications, calendar refinements, and UI polish.",
        "new_features": [
            "Real-time notifications — super admins are notified instantly when a user submits a bug report or feature request",
            "Report status updates — users receive a notification when an admin updates their submitted report",
            "Users can now edit or delete their own open reports before they are reviewed",
            "Admin can view reporter details (name, worker ID, email) on submitted reports",
        ],
        "improvements": [
            "Significantly faster page transitions — eliminated animation lag across the entire application",
            "Sidebar hover interactions are now smooth and responsive with debounced transitions",
            "Larger table areas on Request History, Purchase Requests, and Assets pages for better data visibility",
            "About page now always displays the latest version and build date",
            "PTB Calendar Year view month tabs now have a fixed height with visible scrolling",
            "WebSocket connection handling is more resilient with exponential backoff and reduced retry spam",
        ],
        "bug_fixes": [
            "Fixed WebSocket connection errors caused by cross-origin restrictions between frontend and backend",
            "Fixed user display names for external users — now correctly uses username instead of empty name fields",
            "Fixed PTB Calendar allowing non-admin users to edit holidays — now properly restricted to PTB admins only",
            "Removed redundant Preview section from PTB Calendar leave form modal",
            "Fixed nginx missing WebSocket proxy configuration for real-time features",
        ],
        "security": [
            "WebSocket connections are now validated by token authentication instead of origin-based checks",
        ],
    },
    {
        "version": "2.4.0",
        "release_date": date(2026, 2, 19),
        "status": "stable",
        "summary": "Language support across the entire portal, Developer role distinction, Kanban Board performance overhaul, and comprehensive documentation.",
        "new_features": [
            "Full multi-language support — the entire portal is now available in English, Chinese, and Bahasa Indonesia",
            "Language preference selector in your profile — your choice is remembered across sessions",
            "Developer role is now displayed separately from Super Admin throughout the portal",
            "Comprehensive project documentation with quick-start guides for new developers",
        ],
        "improvements": [
            "Kanban Board loads and responds much faster — the internal code was reorganized into smaller, focused modules",
            "Overtime Summary statistics now load significantly faster with server-side caching",
            "Overtime History no longer fetches data twice when you reset filters — noticeably snappier",
            "Dragging tasks to reorder them on the Kanban Board is much faster, especially with many tasks",
            "All text labels, buttons, and messages across every page now respect your chosen language",
            "User Profile page fully translated with role labels, permission descriptions, and form fields",
            "Overtime Form, Calendar, and detail pages all support language switching",
        ],
        "bug_fixes": [
            "Fixed Developer role users incorrectly showing as 'Super Admin' on their profile page",
            "Fixed event reminders incorrectly treating Developer role as Super Admin",
            "Fixed an unused code warning in the navigation system that appeared during builds",
        ],
    },
]


class Command(BaseCommand):
    help = "Populate release_notes table with version history from git/changelog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually create the records (default is dry-run).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing release notes before populating.",
        )

    def handle(self, *args, **options):
        apply = options["apply"]
        clear = options["clear"]

        if clear and apply:
            deleted, _ = ReleaseNote.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing release notes."))

        created_count = 0
        skipped_count = 0

        for entry in RELEASE_NOTES:
            version = entry["version"]
            exists = ReleaseNote.objects.filter(version=version).exists()

            if exists:
                skipped_count += 1
                self.stdout.write(f"  SKIP v{version} (already exists)")
                continue

            if apply:
                ReleaseNote.objects.create(
                    version=version,
                    release_date=entry["release_date"],
                    status=entry.get("status", "stable"),
                    summary=entry.get("summary", ""),
                    new_features=entry.get("new_features", []),
                    improvements=entry.get("improvements", []),
                    bug_fixes=entry.get("bug_fixes", []),
                    breaking_changes=entry.get("breaking_changes", []),
                    security=entry.get("security", []),
                    known_issues=entry.get("known_issues", []),
                    deprecations=entry.get("deprecations", []),
                    contributors=entry.get("contributors", []),
                    published=True,
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  CREATE v{version}"))
            else:
                created_count += 1
                self.stdout.write(f"  WOULD CREATE v{version}: {entry['summary'][:60]}...")

        if apply:
            self.stdout.write(self.style.SUCCESS(f"\nDone: {created_count} created, {skipped_count} skipped."))
        else:
            self.stdout.write(self.style.WARNING(f"\nDRY RUN: {created_count} would be created, {skipped_count} would be skipped.\nRun with --apply to create records."))
