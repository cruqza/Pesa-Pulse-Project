"""
Day 1 - API Data Analysis Using Python Structures
Squad Python Specialization - Data Science, AI & Analytics
"""

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"


def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print(f"Error fetching customers: {error}")
        return []

# d = get_customers(API_URL)
# print(d)


def explore(record: dict | list, indent: int = 0) -> None:
    """Print every key in a (possibly nested) record with its type, indented by depth."""
    if isinstance(record, dict):
        for key, value in record.items():
            print(" " * indent + f"{key}: {type(value).__name__}")
            if isinstance(value, (dict, list)):
                explore(value, indent + 3)
    elif isinstance(record, list):
        for index, item in enumerate(record):
            print(" " * indent + f"[{index}]: {type(item).__name__}")
            if isinstance(item, (dict, list)):
                explore(item, indent + 3)

# explore(d)

def extract_attributes(customers: list[dict]) -> list[dict]:
    """Return one flat dict per customer with the attributes listed in the task."""
    rows = []
    for c in customers:
        try:
            rows.append({
                "id": c["id"],
                "name": c["name"],
                "username": c["username"],
                "email": c["email"],
                "email_domain": c["email"].split("@")[-1].split(".")[-1].lower(),
                "phone": c["phone"],
                "city": c["address"]["city"],
                "zipcode": c["address"]["zipcode"],
                "latitude": float(c["address"]["geo"]["lat"]),
                "longitude": float(c["address"]["geo"]["lng"]),
                "company": c["company"]["name"],
                "website": c["website"],
            })
        except (KeyError, TypeError, ValueError) as error:
            print(f"Skipping customer {c.get('id')}: {type(error).__name__}: {error}")
    return rows

# x = extract_attributes(d)
# print(x)

def unique_cities(customers: list[dict]) -> set[str]:
    """Return the set of distinct cities."""
    return {c["address"]["city"] for c in customers}

# cities = unique_cities(d)
# print(cities)

def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city using a loop and/or a dict comprehension (no Counter, no pandas)."""
    counts = {}
    for c in customers:
        city = c["address"]["city"]
        counts[city] = counts.get(city, 0) + 1
    return counts

# custcity = city_counts(d)
# print(custcity)


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Return {email top-level domain (e.g. 'biz', 'tv'): number of customers} using a dict comprehension."""
    domains = [c["email"].split("@")[-1].split(".")[-1].lower() for c in customers]
    return {d: domains.count(d) for d in set(domains)}

# emails = email_domain_counts(d)
# print(emails)

def print_sorted(counts: dict[str, int], title: str) -> None:
    """Print counts from most to least common, ties listed alphabetically."""
    print(title)
    for name, n in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {name}: {n}")


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    """Convert the flat records into a pandas DataFrame."""
    return pd.DataFrame(rows)


def plot_distribution(counts: dict[str, int], path: Path) -> None:
    """Save a labelled horizontal bar chart of the distribution to path."""
    path = Path(path)
    os.makedirs(path.parent, exist_ok=True)

    items = sorted(counts.items(), key=lambda item: (item[1], item[0]))
    labels = [name for name, _ in items]
    values = [n for _, n in items]

    fig, ax = plt.subplots(figsize=(8, max(3, 0.4 * len(labels))))
    ax.barh(labels, values)
    ax.set_title("Customer distribution")
    ax.set_xlabel("Number of customers")
    ax.set_xticks(range(0, max(values) + 1))
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    # 1. Fetch
    customers = get_customers()
    print(f"Customers retrieved: {len(customers)}")

    # 2. Explore nested structure
    explore(customers)

    # 3. Flatten each record
    records = extract_attributes(customers)
    print(f"Flat records: {len(records)}")

    # 4. Unique cities (set)
    cities = unique_cities(customers)
    print(f"Unique cities: {len(cities)}  (out of {len(customers)} customers)")

    # 5. Counts by city and by email top-level domain
    city_counts_dict = city_counts(customers)
    print_sorted(city_counts_dict, "Customers by city")
    print_sorted(email_domain_counts(customers), "Customers by email domain")

    # 6. DataFrame + shape / dtypes + pandas cross-check
    df = to_dataframe(records)
    print(f"\nDataFrame shape: {df.shape}")
    print("DataFrame dtypes:")
    print(df.dtypes)

    print("\nCross-check (hand-written vs pandas groupby):")
    print(f"  cities  : {city_counts_dict}  vs  {df['city'].value_counts().to_dict()}")
    print(f"  domains : {email_domain_counts(customers)}  vs  {df['email_domain'].value_counts().to_dict()}")

    # Findings summary
    most_common_city = max(city_counts_dict, key=lambda k: city_counts_dict[k])
    print("\nFindings summary:")
    print(f"  Customers retrieved : {len(customers)}")
    print(f"  Unique cities       : {len(cities)}")
    print(f"  Most common city    : {most_common_city} ({city_counts_dict.get(most_common_city)})")
    print(f"  Email domains       : {email_domain_counts(customers)}")
    print(f"  Chart saved to      : output/customer_distribution.png")

    # 7. Export CSVs (no index)
    os.makedirs("output", exist_ok=True)
    df.to_csv("output/customers.csv", index=False)

    city_df = (
        df.groupby("city")
          .size()
          .to_frame("customer_count")
          .reset_index()
          .sort_values(["customer_count", "city"], ascending=[False, True])
    )
    city_df.to_csv("output/city_counts.csv", index=False)

    # 8. Charts
    plot_distribution(city_counts_dict, Path("output/customer_distribution.png"))
    plot_distribution(email_domain_counts(customers), Path("output/email_tld_distribution.png"))
