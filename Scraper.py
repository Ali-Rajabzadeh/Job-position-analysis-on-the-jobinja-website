# PACKAGES
import pandas as pd
import requests
from bs4 import BeautifulSoup

# INPUTS
## example:
# url = "https://jobinja.ir/jobs?&filters%5Bkeywords%5D%5B0%5D=Data%20specialist&filters%5Bkeywords%5D%5B0%5D=Data%20specialist&preferred_before=1782977022&sort_by=published_at_desc"
# maximum_page_number = 2

url = input("Enter your url from jobinja website: ")
maximum_page_number = input("Enter number of pages: ")

url = str(url)
maximum_page_number = int(maximum_page_number)

# LISTS FOR DATA
links = []
titles = []
company = []
location = []
contract_type = []

# GET ALL PAGES
print("\n" + "="*70)
print("PHASE 1: Scraping job listings from all pages")
print("="*70 + "\n")

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://jobinja.ir/",
}

for i in range(maximum_page_number):
    if i == 0:
        url_page = url
    else:
        url_page = url + f"&page={i+1}"

    try:
        page = requests.get(url_page, headers=headers, timeout=15)
        page.raise_for_status()
    except requests.RequestException:
        continue

    if page.status_code != 200:
        continue
    soup = BeautifulSoup(page.text, 'html.parser')

    # ATTENTION: Our selector requires all five classes but we search using only the stable classes
    items = soup.select("li.c-jobListView__item")

    # GETTING TITLE, LINK, COMPANY NAME, LOCATION AND TYPE OF CONTRACT OF POSTS
    for item in items:
        
        title = item.find("a", class_="c-jobListView__titleLink")
        if title:
            links.append(title["href"])
            titles.append(title.get_text(strip=True))

        for meta in item.select("li.c-jobListView__metaItem"):
            icon = meta.find("i")

            if "c-icon--construction" in icon.get("class", []):
                comp = meta.find("span").get_text(strip=True).replace("\u200c", " ")
                company.append(comp if comp else None)

            elif "c-icon--place" in icon.get("class", []):
                loc = meta.find("span").get_text(strip=True).replace("\u200c", " ")
                location.append(loc if loc else None)

            elif "c-icon--resume" in icon.get("class", []):
                contract = meta.find("span").find("span").get_text(" ", strip=True)
                contract = " ".join(contract.split()).replace("\u200c", " ")
                contract_type.append(contract if contract else None)

# CREATE DATA FRAME
JobOffers = pd.DataFrame({"links": links,
                          "title": titles,
                          "company": company,
                          "location": location,
                          "contract_type": contract_type})

# SUMMARY OF PHASE 1
print("     PHASE 1 COMPLETE")
print(f"        Total job listing found: {len(JobOffers)}")

# ADD DETAILED FEATURES
columns = [
    "definition",
    "experience",
    "salary",
    "sex",
    "military_status",
    "degree_requir",
    "skills",
]
JobOffers[columns] = None

# GET ALL DETAILED FEATURES FOR ALL POSTS
print("\n" + "="*70)
print("PHASE 2: Scraping detailed job descriptions")
print("="*70 + "\n")

headers_post = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://jobinja.ir/",
}

for i in range(len(JobOffers)):
    url_post = str(JobOffers["links"][i])

    try:
        page_post = requests.get(url_post, headers=headers_post, timeout=15)
    except requests.RequestException:
        continue

    if page_post.status_code != 200:
        continue
    else:

        soup_post = BeautifulSoup(page_post.text, 'html.parser')

        # JOB_DEFINITINN
        job_definition = soup_post.find("div", class_="o-box__text")
        if job_definition:
            JobOffers.at[i, "definition"] = job_definition.get_text(strip=True)

        # EXPERIENCE & SALARY
        up_btn = soup_post.find("ul", class_="c-jobView__firstInfoBox c-infoBox")
        if up_btn:   
            for li in up_btn.find_all("li", class_="c-infoBox__item"):
                title = li.find("h4", class_="c-infoBox__itemTitle").get_text(strip=True)

                if title == "حداقل سابقه کار":
                    experience = li.find("span", class_="black").get_text(strip=True)
                    JobOffers.at[i, "experience"] = experience

                elif title == "حقوق":
                    salary = li.find("span", class_="black").get_text(strip=True)
                    JobOffers.at[i, "salary"] = salary

        # GENDER & MILITARY_STATUS & DEGREEE & SKILLS
        down_btn = soup_post.find("ul", class_="c-infoBox u-mB0")
        if down_btn:
            for li in down_btn.find_all("li", class_="c-infoBox__item"):
                title = li.find("h4", class_="c-infoBox__itemTitle").get_text(strip=True)

                if title == "جنسیت":
                    sex = li.find("span", class_="black").get_text(strip=True).replace("\u200c", " ")
                    JobOffers.at[i, "sex"] = sex

                elif title == "وضعیت نظام وظیفه":
                    military_status = li.find("span", class_="black").get_text(strip=True).replace("\u200c", "")
                    JobOffers.at[i, "military_status"] = military_status

                elif title == "حداقل مدرک تحصیلی":
                    degree_requir = li.find("span", class_="black").get_text(strip=True).replace("\u200c", " ")
                    JobOffers.at[i, "degree_requir"] = degree_requir

                elif title == "مهارت‌های مورد نیاز":
                    skills = [span.get_text(strip=True) for span in li.find_all("span", class_="black")]
                    JobOffers.at[i, "skills"] = skills

# EXPORT DATA
JobOffers.to_excel("Scraped_data.xlsx")

# SUMMARY OF PHASE 2
print("3 sample of data and it's detailed features:")
for idx in range(min(3, len(JobOffers))):
    print(f"\n{idx+1}. {JobOffers['title'][idx]}")
    print(f"     Company: {JobOffers['company'][idx]}")
    print(f"     Location: {JobOffers['location'][idx]}")
    print(f"     Contract: {JobOffers['contract_type'][idx]}")
    print(f"     Salary: {JobOffers['salary'][idx]}")

print("\n" + "="*70)
print("SCRAPING COMPLETED SUCCESSFULLY")
print("="*70)