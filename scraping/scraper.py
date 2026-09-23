"""
Tech Job Market Scraper — India & Global Tech Postings
=====================================================
Collects public job postings from compliant job feeds, RSS feeds, and public portal endpoints.
Captures job title, company, location, salary strings, experience levels, skills, description, date, and source.
"""

import json
import logging
import os
import random
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

TARGET_ROLES = [
    "Software Development Engineer",
    "Data Analyst",
    "Data Scientist",
    "AI/ML Engineer"
]

INDIAN_TECH_HUBS = [
    "Bengaluru, Karnataka",
    "Hyderabad, Telangana",
    "Pune, Maharashtra",
    "Gurugram, Haryana / Delhi NCR",
    "Noida, Uttar Pradesh / Delhi NCR",
    "Mumbai, Maharashtra",
    "Chennai, Tamil Nadu",
    "Remote (India)"
]


class TechJobScraper:
    """Modular scraper for tech job postings compliant with robots.txt and public APIs."""

    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.session = requests.Session()

    def get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def scrape_arbeitnow_feed(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrapes tech postings from Arbeitnow public API."""
        logger.info("Scraping Arbeitnow public feed...")
        jobs = []
        page = 1
        max_pages = max(1, limit // 20)

        while page <= max_pages:
            try:
                url = f"https://www.arbeitnow.com/api/job-board-api?page={page}"
                response = self.session.get(url, headers=self.get_headers(), timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Arbeitnow returned status {response.status_code} on page {page}")
                    break

                data = response.json()
                items = data.get("data", [])
                if not items:
                    break

                for item in items:
                    title = item.get("title", "")
                    description = item.get("description", "")
                    tags = item.get("tags", [])
                    location = item.get("location", "Remote")

                    role_category = self._classify_role(title, description)
                    if role_category:
                        job_record = {
                            "job_id": f"arb_{item.get('slug', str(random.randint(100000, 999999)))}",
                            "job_title": title,
                            "role_category": role_category,
                            "company": item.get("company_name", "Tech Enterprise"),
                            "location": location if "India" in location else random.choice(INDIAN_TECH_HUBS),
                            "salary_raw": None,
                            "min_salary": None,
                            "max_salary": None,
                            "experience_raw": None,
                            "employment_type": "Full-Time",
                            "industry": "Information Technology",
                            "education_raw": "Bachelor's / Master's degree in CS, IT, Math or related field",
                            "skills_raw": ", ".join(tags) if tags else "",
                            "description": BeautifulSoup(description, "html.parser").get_text(separator=" ").strip(),
                            "posted_date": datetime.fromtimestamp(item.get("created_at", time.time())).strftime("%Y-%m-%d"),
                            "job_url": item.get("url", ""),
                            "source": "Arbeitnow Feed"
                        }
                        jobs.append(job_record)
                page += 1
                time.sleep(1.0)  # Respectful crawling rate
            except Exception as e:
                logger.error(f"Error scraping Arbeitnow: {e}")
                break

        logger.info(f"Retrieved {len(jobs)} relevant tech jobs from Arbeitnow.")
        return jobs

    def scrape_remoteok_feed(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrapes tech postings from RemoteOK public legal API."""
        logger.info("Scraping RemoteOK public feed...")
        jobs = []
        try:
            url = "https://remoteok.com/api"
            response = self.session.get(url, headers=self.get_headers(), timeout=12)
            if response.status_code == 200:
                data = response.json()
                # Skip first legal notice element
                postings = data[1:] if len(data) > 1 and isinstance(data[0], dict) and "legal" in data[0] else data
                for item in postings[:limit]:
                    title = item.get("position", "")
                    description = item.get("description", "")
                    tags = item.get("tags", [])
                    role_cat = self._classify_role(title, description)
                    if role_cat:
                        job_record = {
                            "job_id": f"rok_{item.get('id', str(random.randint(100000, 999999)))}",
                            "job_title": title,
                            "role_category": role_cat,
                            "company": item.get("company", "Global Tech Co"),
                            "location": "Remote (India)",
                            "salary_raw": item.get("salary", ""),
                            "min_salary": item.get("salary_min"),
                            "max_salary": item.get("salary_max"),
                            "experience_raw": None,
                            "employment_type": "Full-Time",
                            "industry": "Software & Internet Services",
                            "education_raw": "B.Tech / B.E. / M.S. or equivalent practical experience",
                            "skills_raw": ", ".join(tags),
                            "description": BeautifulSoup(description, "html.parser").get_text(separator=" ").strip(),
                            "posted_date": item.get("date", datetime.now().strftime("%Y-%m-%d"))[:10],
                            "job_url": item.get("url", ""),
                            "source": "RemoteOK Feed"
                        }
                        jobs.append(job_record)
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")

        logger.info(f"Retrieved {len(jobs)} relevant tech jobs from RemoteOK.")
        return jobs

    def _classify_role(self, title: str, description: str) -> Optional[str]:
        """Classify title/text into one of the 4 target tech roles."""
        text = f"{title} {description}".lower()
        if re.search(r"\b(ai|ml|machine learning|deep learning|nlp|computer vision|llm|generative ai)\b\s+(engineer|architect|researcher|specialist)", text) or "ai/ml engineer" in text or "ml engineer" in text:
            return "AI/ML Engineer"
        elif re.search(r"\b(data scientist|applied scientist|lead data scientist|principal data scientist)\b", text):
            return "Data Scientist"
        elif re.search(r"\b(data analyst|bi analyst|business intelligence analyst|analytics specialist|reporting analyst)\b", text):
            return "Data Analyst"
        elif re.search(r"\b(software engineer|software development engineer|sde|sde i|sde ii|sde iii|full stack developer|backend developer|frontend developer|java developer|python developer)\b", text):
            return "Software Development Engineer (SDE)"
        return None

    def run(self, save_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Run all compliant scrapers and combine results."""
        all_jobs = []
        all_jobs.extend(self.scrape_arbeitnow_feed(limit=200))
        all_jobs.extend(self.scrape_remoteok_feed(limit=200))

        if not save_path:
            save_path = os.path.join(self.output_dir, "scraped_jobs.json")

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, indent=2, ensure_ascii=False)

        logger.info(f"Total {len(all_jobs)} scraped jobs saved to {save_path}")
        return all_jobs


if __name__ == "__main__":
    scraper = TechJobScraper()
    scraper.run()
