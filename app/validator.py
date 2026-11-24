"""Check a batch of feed records and report every problem found.
Each problem becomes one error dict, shaped to match the feed_errors table.
A record can have more than one problem, so it can produce more than one error.

Try it from the project Folder:
    python -m app.validator --feed staff --count 20 --error-rate 0.3 --seed 7
"""

import argparse
import re
from datetime import date, datetime

from app.generator import DATE_FIELD, ID_FIELD, REQUIRED_FIELDS, generate_records

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$") #YYYY-MM-DD
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$") #something@something.something

def make_error(number, record, feed, field, error_type, message):
    return{
        "record_number": number,
        "record_id": record.get(ID_FIELD[feed]) or None,
        "field_name": field,
        "error_type": error_type,
        "message": message,
        "raw_record": record,
    }

def check_date(value):
    """Return a problem description, or None if the date is fine."""
    if not DATE_PATTERN.match(value):
        return f"'{value}' is not in YYYY-MM-DD format"
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return f"'{value}' is not a real calendar date"
    if parsed > date.today():
        return f"'{value}' is in the future"
    return None

def validate_records(feed, records):
    """Check every record. Returns (number of valid records, list of errors)."""
    if feed not in ID_FIELD:
        raise ValueError(f"feed must be one of {list(ID_FIELD)}, not {feed!r}")

    errors = []
    seen_ids = set()
    valid_count = 0

    for number, record in enumerate(records, start=1):
        record_errors = []
        #1. Every required field must be present and not blank
        for field in REQUIRED_FIELDS[feed]:
            if not str(record.get(field) or "").strip(): 
                record_errors.append(make_error(number, record, feed, field, "missing_field", f"Required field '{field}' is missing or blank"))
        
        #2.The date must be a real date in the right format. Skipped when blank because #1 already reported it.
        date_field = DATE_FIELD[feed]
        date_value = str(record.get(date_field) or "").strip()
        if date_value:
            problem = check_date(date_value)
            if problem:
                record_errors.append(make_error(number, record, feed, date_field, "invalid_date", problem))
        
        #3. The eamil must look like an email address
        email = str(record.get("email") or "").strip()
        if email and not EMAIL_PATTERN.match(email):
            record_errors.append(make_error(number, record, feed, "email", "invalid_email", f"'{email}' is not a valid email address"))
        
        #4. The ID must not repeat an ID from earlier in the same batch.
        record_id = str(record.get(ID_FIELD[feed]) or "").strip()
        if record_id:
            if record_id in seen_ids:
                record_errors.append(make_error(number, record, feed, ID_FIELD[feed],"duplicate_id", f"ID '{record_id}' already appeared earlier in this batch"))
            seen_ids.add(record_id)
        
        if record_errors: 
            errors.extend(record_errors)
        else:
            valid_count += 1
    return valid_count, errors

def main():
    parser = argparse.ArgumentParser(description="Generate fake records and validate them.")
    parser.add_argument("--feed", choices=["students", "staff"], default="students")
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--error-rate", type=float, default=0.1)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    records = generate_records(args.feed, args.count, args.error_rate, args.seed)
    valid_count, errors = validate_records(args.feed, records)

    print(f"{len(records)} records checked: {valid_count} valid, " f"{len(records)-valid_count} with problems, {len(errors)} errors total\n")

    for e in errors:
        print(f" Record {e['record_number']} ({e['record_id']}): " f"[{e['error_type']}] {e['message']}")
    
if __name__ == "__main__":
    main()
            
