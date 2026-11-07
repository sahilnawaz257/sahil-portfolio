"""
Sahil Nawaz Portfolio — Booking Management CLI Tool
Used by the portfolio owner to manage meeting booking requests securely from the terminal.
Zero Admin Dashboard / Zero Admin Login on the public web.

Usage:
  python backend/manage_bookings.py list
  python backend/manage_bookings.py approve <booking_id> [--link <google_meet_link>]
  python backend/manage_bookings.py reject <booking_id>
"""

import sys
import os
import argparse

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models import MeetingBooking
import email_service
import google_calendar

def list_pending():
    """List all pending meeting requests."""
    bookings = MeetingBooking.get_all_pending()
    print("=" * 80)
    print("SAHIL NAWAZ PORTFOLIO — PENDING MEETING REQUESTS")
    print("=" * 80)
    if not bookings:
        print("No pending meeting requests found.")
        return

    for b in bookings:
        print(f"ID:           {b['id']}")
        print(f"Visitor:      {b['full_name']} <{b['email']}>")
        print(f"Topic:        {b['purpose']}")
        print(f"Date & Time:  {b['meeting_date']} @ {b['meeting_time']}")
        print(f"Notes:        {b.get('notes') or 'None'}")
        print(f"Status:       {b['status']}")
        print("-" * 80)

def approve_booking(booking_id, custom_link=None):
    """Approve a booking, generate/attach Google Meet link, and notify visitor."""
    booking = MeetingBooking.get_by_id(booking_id)
    if not booking:
        print(f"[ERROR] Booking ID '{booking_id}' not found.")
        return

    meet_link = (custom_link or "").strip()
    if not meet_link and google_calendar.is_google_calendar_configured():
        print("Attempting to generate Google Meet link via official Google Calendar API...")
        cal_res = google_calendar.create_google_meet_event(
            summary=f"Google Meet: {booking['full_name']} — {booking['purpose']}",
            description=f"Consultation scheduled with Sahil Nawaz.\nNotes: {booking.get('notes', '')}",
            attendee_email=booking["email"],
            date_str=booking["meeting_date"],
            time_slot_str=booking["meeting_time"]
        )
        if cal_res.get("success"):
            meet_link = cal_res.get("meeting_link")
            print(f"Generated Google Meet Link: {meet_link}")
        else:
            print(f"Google Calendar note: {cal_res.get('message')}")

    updated = MeetingBooking.update_status(booking_id, "Approved", meeting_link=meet_link)
    print(f"Successfully Approved Booking #{booking_id}!")
    if updated.get("google_meet_link") or updated.get("meeting_link"):
        print(f"Google Meet Link: {updated.get('google_meet_link') or updated.get('meeting_link')}")

    # Dispatch confirmation to visitor
    res = email_service.send_booking_confirmation_to_visitor(updated)
    print(f"Visitor Notification: {res.get('message')}")

def reject_booking(booking_id):
    """Reject a booking and notify visitor."""
    booking = MeetingBooking.get_by_id(booking_id)
    if not booking:
        print(f"[ERROR] Booking ID '{booking_id}' not found.")
        return

    updated = MeetingBooking.update_status(booking_id, "Rejected")
    print(f"Successfully Declined Booking #{booking_id}.")
    res = email_service.send_booking_confirmation_to_visitor(updated)
    print(f"Visitor Notification: {res.get('message')}")

def main():
    parser = argparse.ArgumentParser(description="Sahil Nawaz Portfolio — Meeting Booking Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list
    subparsers.add_parser("list", help="List all pending meeting requests")

    # approve
    approve_parser = subparsers.add_parser("approve", help="Approve a booking and dispatch confirmation")
    approve_parser.add_argument("id", help="Booking Reference ID")
    approve_parser.add_argument("--link", help="Optional Google Meet link (e.g. https://meet.google.com/xxx-yyyy-zzz)", default="")

    # reject
    reject_parser = subparsers.add_parser("reject", help="Decline a booking and dispatch update")
    reject_parser.add_argument("id", help="Booking Reference ID")

    args = parser.parse_args()

    if args.command == "list":
        list_pending()
    elif args.command == "approve":
        approve_booking(args.id, custom_link=args.link)
    elif args.command == "reject":
        reject_booking(args.id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
