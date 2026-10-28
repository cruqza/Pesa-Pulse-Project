
import os
import matplotlib 
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"


def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing."""
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print(f"Error fetching customers: {error}")
        return {error}

customers = get_customers()
print(customers)


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

explore(customers)


def extract_attributes(customers: list[dict]) -> list[dict]:
    """Return one flat dict per customer with the attributes listed in the task."""
    rows = []
        # creating an empty list , inisde it will have many dictionaries, each dictinary has individual attributes from the jason file(a nested dictinary)
    
    # customers is the whole jason file with (eg 500 customers), c stands for one out of the 500 customers.
    for c in customers:
        try:
            rows.append({
                "id": c["id"],
                "name": c["name"],
                "username": c["username"],
                "email": c["email"],
                "email_domain": c["email"].split("@")[-1].lower(),
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


result = extract_attributes(customers)
print(result)


def unique_cities(customers: list[dict]) -> set[str]:
    """Return the set of distinct cities."""
    return {c["address"]["city"] for c in customers}

cities = unique_cities(customers)
print(cities)


def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city using a loop and/or a dict comprehension (no Counter, no pandas)."""
    counts = {}

    for c in customers:
        city = c["address"]["city"]
        counts[city] = counts.get(city, 0) + 1

    return counts


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Return {email domain: number of customers} using a dict comprehension."""
    domains = [c["email"].split("@")[-1].lower() for c in customers]
    return {d: domains.count(d) for d in set(domains)}


def print_sorted(counts: dict[str, int], title: str) -> None:
    """Print counts from most to least common, ties listed alphabetically."""
    print(title)
    for name, n in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {name}: {n}")


distinct_email = email_domain_counts(customers)
print(distinct_email)
      
distict_count_cities = city_counts(customers)
print(distict_count_cities)
print_sorted(city_counts(customers), "Customers by city")
print_sorted(email_domain_counts(customers), "Customers by email domain")



def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    return df

df = to_dataframe(result)
pd.set_option("display.max_columns", None)
print(df.shape)
print(df.dtypes)
# df.columns
print(df)


os.makedirs("output", exist_ok=True)     

# 1. customers.csv: the full flat table
df.to_csv("output/customers.csv", index=False)

# 2. city_counts.csv: one row per city 
city_df = (
    df.groupby("city")
      .size()
      .reset_index(name="count")
      .sort_values(["count", "city"], ascending=[False, True])
)
city_df.to_csv("output/city_counts.csv", index=False)



def plot_distribution(counts: dict[str, int], path: str, title: str = "Customer distribution") -> None:
    """Save a horizontal bar chart of counts, most common at the top."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    items = sorted(counts.items(), key=lambda item: (item[1], item[0]))  
    labels = [name for name, _ in items]
    values = [n for _, n in items]

    fig, ax = plt.subplots(figsize=(8, max(3, 0.4 * len(labels))))
    ax.barh(labels, values)
    ax.set_title(title)
    ax.set_xlabel("Number of customers")
    ax.set_xticks(range(0, max(values) + 1))  
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)             


plot_distribution(city_counts(customers), "output/customer_distribution.png", "Customers by city")

df["tld"] = df["email_domain"].str.split(".").str[-1]
print(df["tld"].value_counts())

tld_counts = df["tld"].value_counts().to_dict()
plot_distribution(tld_counts, "output/email_tld_distribution.png", "Customers by email TLD")


