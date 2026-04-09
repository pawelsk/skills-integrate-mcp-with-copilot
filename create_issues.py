#!/usr/bin/env python3
"""
Script to create GitHub issues for new features
Usage: python3 create_issues.py <github_token>
"""

import requests
import sys
import json

def create_issue(token, owner, repo, title, body, labels=None):
    """Create a GitHub issue using the GitHub API"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": title,
        "body": body,
    }
    
    if labels:
        data["labels"] = labels
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        issue = response.json()
        print(f"✓ Created issue #{issue['number']}: {title}")
        return issue
    else:
        print(f"✗ Failed to create issue '{title}'")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def main():
    # Check for token argument
    if len(sys.argv) < 2:
        print("Usage: python3 create_issues.py <github_token>")
        print("\nYou can get a GitHub token from: https://github.com/settings/tokens")
        print("Required scopes: repo (full control of private repositories)")
        sys.exit(1)
    
    token = sys.argv[1]
    owner = "pawelsk"
    repo = "skills-integrate-mcp-with-copilot"
    
    # List of issues to create
    issues = [
        {
            "title": "Feature: User Authentication & Role-Based Access",
            "body": """Add comprehensive user authentication system with multiple roles (admin, super-admin, member).

**Requirements:**
- User login and registration system
- Role-based access control (RBAC)
- Session management
- Different permission levels for different user types
- Secure password handling

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Allow Organizers to Create and Manage Activities",
            "body": """Currently activities are pre-defined. Add functionality for organizers/admins to create, edit, and delete activities.

**Requirements:**
- Create new activity endpoint
- Edit activity details
- Delete activities
- Search and filter by activity creator
- Activity status management

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Admin Dashboard for Activity Management",
            "body": """Build a comprehensive admin dashboard for super-admins and organizers.

**Requirements:**
- View all activities and clubs
- Manage participants
- View analytics
- System-wide controls
- Support for multiple admin levels

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Attendance Tracking for Events",
            "body": """Add ability to track who attended events (beyond just sign-ups).

**Requirements:**
- Mark attendance during/after events
- Attendance reports
- Attendance statistics
- Check-in functionality

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Event Ticketing System",
            "body": """Implement ticketing functionality for events with ticket management capabilities.

**Requirements:**
- Create event tickets
- Track ticket sales/distribution
- Ticket validation
- Capacity management

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Task Management for Event Planning",
            "body": """Add task management system to assign and track event planning tasks.

**Requirements:**
- Create tasks for events
- Assign tasks to team members
- Track task completion status
- Task deadlines

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Club Budget Management System",
            "body": """Implement budget tracking and management for clubs.

**Requirements:**
- Set club budgets
- Track spending against budget
- Budget reports
- Budget alerts when limits approached
- Multi-currency support

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Financial Transaction Management",
            "body": """Track all financial transactions (income, expenses) for clubs.

**Requirements:**
- Record transactions
- Transaction categories
- Transaction history/reports
- Reconciliation features
- Export transaction data

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Event Photo Gallery",
            "body": """Allow uploading and managing photos from events.

**Requirements:**
- Upload event photos
- Gallery view with thumbnails
- Full-size image viewing
- Album organization
- Photo deletion capability

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: CSV Export Functionality",
            "body": """Add ability to export data (participants, transactions, etc.) to CSV format.

**Requirements:**
- Export participant lists
- Export transaction reports
- Export attendance records
- Export activity data
- Schedule automated exports

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Push Notifications for Events",
            "body": """Implement real-time notifications using Firebase or similar service.

**Requirements:**
- Send notifications for new events
- Notification preferences
- In-app notification center
- Email notification fallback
- Notification scheduling

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Automated Event Reminders",
            "body": """Send automated reminders before events.

**Requirements:**
- Configurable reminder times (e.g., 24h, 1h before)
- Email reminders
- Push notification reminders
- Reminder frequency settings
- Opt-in/opt-out preferences

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Event Feedback and Sentiment Analysis",
            "body": """Collect participant feedback on events and analyze sentiment.

**Requirements:**
- Feedback form after events
- Rating system (1-5 stars)
- Comment collection
- Sentiment analysis of comments
- Feedback reports/trends

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Activity Feed with Real-Time Updates",
            "body": """Implement RSS/activity feed showing recent activities and updates.

**Requirements:**
- Real-time feed updates
- Event announcements
- Participant updates
- RSS feed generation
- Activity notifications

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Persistent Database Layer",
            "body": """Upgrade from in-memory storage to a proper database with Firebase integration.

**Requirements:**
- SQLite or PostgreSQL for data storage
- Firebase integration for real-time features
- Data migration utilities
- Backup functionality
- Connection pooling

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        },
        {
            "title": "Feature: Analytics and Reporting Dashboard",
            "body": """Add comprehensive analytics for activity participation, engagement, and trends.

**Requirements:**
- Participation statistics
- Attendance trends
- Popular activities
- Member engagement metrics
- Custom report generation

**Related to:** ClubPortalEvent feature analysis""",
            "labels": ["feature"]
        }
    ]
    
    print(f"\n📝 Creating {len(issues)} GitHub issues for {owner}/{repo}...\n")
    
    created_count = 0
    failed_count = 0
    
    for issue in issues:
        result = create_issue(token, owner, repo, issue["title"], issue["body"], issue.get("labels"))
        if result:
            created_count += 1
        else:
            failed_count += 1
    
    print(f"\n{'='*60}")
    print(f"✓ Created: {created_count} issues")
    if failed_count > 0:
        print(f"✗ Failed: {failed_count} issues")
    print(f"{'='*60}\n")
    
    if created_count == len(issues):
        print("🎉 All issues created successfully!")
        return 0
    else:
        print("⚠️  Some issues failed to create. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
