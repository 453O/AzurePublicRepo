import requests
import pandas as pd
from urllib.parse import urlparse

# Your list of websites (replace with your actual list)
websites = [
    "https://www.example.com",
    "https://contoso.com"
]

# Function to extract domain from URL
def extract_domain(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "") if parsed.netloc else url
    except Exception:
        return url

# Function to get tenant ID and name
def get_entra_id_info(domain):
    # Step 1: Check OpenID configuration for tenant ID
    openid_url = f"https://login.microsoftonline.com/{domain}/.well-known/openid-configuration"
    try:
        response = requests.get(openid_url, timeout=5)
        if response.status_code == 200:
            tenant_id = response.json().get("issuer").split("/")[-2]
        else:
            return None, None
    except requests.RequestException:
        return None, None

    # Step 2: Get tenant name using tenant ID
    if tenant_id:
        tenant_info_url = f"https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration"
        try:
            tenant_response = requests.get(tenant_info_url, timeout=5)
            if tenant_response.status_code == 200:
                # Fallback: Use domain as tenant name if no better info available
                # Note: Real tenant name requires Graph API or additional lookup
                tenant_name = domain  # Placeholder (see notes below)
                return tenant_id, tenant_name
        except requests.RequestException:
            pass
    return tenant_id, None

# Collect data
data = []
for website in websites:
    domain = extract_domain(website)
    tenant_id, tenant_name = get_entra_id_info(domain)
    data.append({
        "Website": website,
        "Domain": domain,
        "Tenant ID": tenant_id,
        "Tenant Name": tenant_name if tenant_name else "Not Found"
    })

# Create Pandas DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)

# Optionally, save to CSV
df.to_csv("entra_id_tenants.csv", index=False)