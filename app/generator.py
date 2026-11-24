#Generate fake student/staff records with some deliberate
#errors giving the validator something to catch.
#run from project folder EX:
#python -m app.generator --feed students --count 20 --seed 42

import argparse
import json
import random
import re
from faker import Faker 

fake = Faker()

SCHOOLS = [
    "Maple Ridge Elementary",
    "Cedar Creek Middle",
    "Riverbend High",
    "Pine Valley Elementary",
    "Summit Academy",
]
GRADES = ["K"] + [str(g) for g in range (1, 13)]
JOB_TITLES = [
    "Teacher",
    "Paraprofessional",
    "Counselor",
    "Librarian",
    "Office Manager",
    "Custodian",
    "Principal",
]
ID_FIELD = {"students": "student_id", "staff": "staff_id"}
DATE_FIELD = {"students": "birth_date", "staff": "hire_date"}
REQUIRED_FIELDS = {"students": [
    "student_id", "first_name", "last_name", "email", "birth_date", "grade", "school"
    ], 
    "staff": ["staff_id", "first_name", "last_name", "email", "hire_date", "job_title", "school"],}
ERROR_TYPES = ["missing_field", "invalid_date", "invalid_email", "duplicate_id"]

def email_name(first, last, n):
#build the email using letters and digits only, so removing any characters like ' from O'Reilly
    clean = lambda s: re.sub(r"[^a-z]", "", s.lower())
    return f"{clean(first)}.{clean(last)}{n}"

def make_student(n):
    first, last = fake.first_name(), fake.last_name()
    return {
        "student_id": f"S{n:06d}",
        "first_name": first,
        "last_name": last,
        "email": f"{email_name(first, last, n)}@students.example.edu",
        "birth_date": fake.date_of_birth(minimum_age = 5, maximum_age = 18).isoformat(),
        "grade": random.choice(GRADES),
        "school": random.choice(SCHOOLS),
    }

def make_staff(n):
    first, last = fake.first_name(), fake.last_name()
    return {
        "staff_id": f"E{n:05d}",
        "first_name": first,
        "last_name" : last,
        "email": f"{email_name(first, last, n)}@example.edu",
        "hire_date": fake.date_between(start_date="-25y",
        end_date="today").isoformat(),
        "job_title": random.choice(JOB_TITLES),
        "school": random.choice(SCHOOLS),
    }

def add_error(record, feed, error_type, earlier_ids):
    #Add an error to a record
    if error_type == "missing_field":
        #blank out any required field except the ID.
        choices = [f for f in REQUIRED_FIELDS[feed] if f != ID_FIELD[feed]]
        record[random.choice(choices)] = ""
    elif error_type == "invalid_date":
        record[DATE_FIELD[feed]] = random.choice(["2026-13-45", "2019-02-30", "31/12/2020", "unknown"])
    elif error_type == "invalid_email":
        record["email"] = record["email"].replace("@", " at ")
    elif error_type == "duplicate_id":
        record[ID_FIELD[feed]] = random.choice(earlier_ids)

def generate_records(feed, count, error_rate=0.1, seed = None):
    #returns a list of 'count' fake records for the given feed.
    #about 'error_rate' of them (0.1 = 10%) have one deliberate problem
    #pass a seed to get same records every time (repeatable tests)
    if feed not in ID_FIELD:
        raise ValueError(f"feed must be one of {list(ID_FIELD)}, not {feed!r}")
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)
    make = make_student if feed == "students" else make_staff
    records, seen_ids = [],[]

    for n in range(1, count + 1):
        record = make(n)
        if random.random() < error_rate:
            #a dup needs an earlier ID to copy, skip for first record
            choices = ERROR_TYPES if seen_ids else ERROR_TYPES[:-1]
            add_error(record, feed, random.choice(choices), seen_ids)
        records.append(record)
        seen_ids.append(record[ID_FIELD[feed]])
    return records

def main():
    parser = argparse.ArgumentParser(description="Generate fake feed records.")
    parser.add_argument("--feed", choices=["students", "staff"], default="students")
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--error-rate", type=float,default=0.1)
    parser.add_argument("--seed", type=int, help="same seed = same records")
    parser.add_argument("--out", help="save to this JSON file instead of printing")
    args = parser.parse_args()
    
    records = generate_records(args.feed, args.count, args.error_rate, args.seed)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(records, f, indent=2)
        print(f"Wrote {len(records)} records to {args.out}")
    else:
        print(json.dumps(records, indent=2))

if __name__ == "__main__":
    main()