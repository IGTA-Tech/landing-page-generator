"""
Website Crawler for Landing Page Generator
Crawls brand websites to extract verified content including testimonials, case studies, and company info.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
from datetime import datetime
import re

class WebsiteCrawler:
    def __init__(self, base_url, max_pages=30):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited_urls = set()
        self.content = {
            "crawl_date": datetime.now().isoformat(),
            "base_url": base_url,
            "testimonials": [],
            "case_studies": [],
            "team_members": [],
            "services": [],
            "achievements": [],
            "about_text": "",
            "all_pages": []
        }

    def is_valid_url(self, url):
        """Check if URL belongs to the same domain"""
        return urlparse(url).netloc == urlparse(self.base_url).netloc

    def extract_testimonials(self, soup, url):
        """Extract testimonials from page"""
        testimonials = []

        # Common testimonial patterns
        testimonial_selectors = [
            'div.testimonial',
            'div[class*="testimonial"]',
            'div[class*="review"]',
            'div[class*="quote"]',
            'blockquote',
            'div[class*="client-feedback"]',
            'div[class*="customer-review"]',
        ]

        for selector in testimonial_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if len(text) > 50 and len(text) < 1000:  # Reasonable testimonial length
                    # Try to extract author name
                    author = ""
                    author_selectors = [
                        'cite', 'span.author', 'p.author',
                        'div.name', 'span.name', 'p.name',
                        'div[class*="author"]', 'span[class*="author"]'
                    ]
                    for author_sel in author_selectors:
                        author_elem = elem.select_one(author_sel)
                        if author_elem:
                            author = author_elem.get_text(strip=True)
                            break

                    testimonials.append({
                        "quote": text,
                        "author": author if author else "Anonymous",
                        "source_url": url,
                        "verified": True,
                        "extracted_date": datetime.now().isoformat()
                    })

        return testimonials

    def extract_team_members(self, soup, url):
        """Extract team member information"""
        team = []

        team_selectors = [
            'div[class*="team"]',
            'div[class*="staff"]',
            'div[class*="member"]',
            'div[class*="attorney"]',
            'div[class*="lawyer"]',
            'div[class*="expert"]',
        ]

        for selector in team_selectors:
            elements = soup.select(selector)
            for elem in elements:
                name_elem = elem.select_one('h3, h4, h5, strong, .name, [class*="name"]')
                title_elem = elem.select_one('.title, [class*="title"], [class*="position"]')
                bio_elem = elem.select_one('p, .bio, [class*="bio"]')

                if name_elem:
                    team.append({
                        "name": name_elem.get_text(strip=True),
                        "title": title_elem.get_text(strip=True) if title_elem else "",
                        "bio": bio_elem.get_text(strip=True) if bio_elem else "",
                        "source_url": url
                    })

        return team

    def extract_services(self, soup, url):
        """Extract services or features"""
        services = []

        service_selectors = [
            'div[class*="service"]',
            'div[class*="feature"]',
            'div[class*="offering"]',
            'li[class*="service"]',
        ]

        for selector in service_selectors:
            elements = soup.select(selector)
            for elem in elements:
                title_elem = elem.select_one('h2, h3, h4, strong')
                desc_elem = elem.select_one('p')

                if title_elem:
                    services.append({
                        "title": title_elem.get_text(strip=True),
                        "description": desc_elem.get_text(strip=True) if desc_elem else "",
                        "source_url": url
                    })

        return services

    def extract_achievements(self, soup, url):
        """Extract achievements, metrics, or success stories"""
        achievements = []

        # Look for numbers followed by achievements
        text = soup.get_text()

        # Patterns like "500+ clients", "95% success rate", "$10M raised"
        number_patterns = [
            r'(\d+[\+%]?\s+(?:clients|customers|cases|applications|visas|approvals|years|success))',
            r'(\d+%\s+(?:success|approval|satisfaction|rate))',
            r'(\$[\d,]+[MKB]?\s+(?:raised|funded|saved))',
        ]

        for pattern in number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match not in [a['description'] for a in achievements]:
                    achievements.append({
                        "description": match,
                        "source_url": url,
                        "verified": True
                    })

        return achievements

    def extract_about_text(self, soup):
        """Extract about/mission text"""
        about_selectors = [
            'div[class*="about"]',
            'div[class*="mission"]',
            'div[class*="story"]',
            'section[class*="about"]',
        ]

        for selector in about_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if len(text) > 100:
                    return text[:1000]  # Limit length

        return ""

    def crawl_page(self, url):
        """Crawl a single page"""
        if url in self.visited_urls or len(self.visited_urls) >= self.max_pages:
            return []

        try:
            print(f"Crawling: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            self.visited_urls.add(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all content types
            testimonials = self.extract_testimonials(soup, url)
            team = self.extract_team_members(soup, url)
            services = self.extract_services(soup, url)
            achievements = self.extract_achievements(soup, url)

            # Update content
            self.content['testimonials'].extend(testimonials)
            self.content['team_members'].extend(team)
            self.content['services'].extend(services)
            self.content['achievements'].extend(achievements)

            # Get about text if we don't have it yet
            if not self.content['about_text']:
                about = self.extract_about_text(soup)
                if about:
                    self.content['about_text'] = about

            # Store page info
            self.content['all_pages'].append({
                "url": url,
                "title": soup.title.string if soup.title else "",
                "crawled_date": datetime.now().isoformat()
            })

            # Find links to other pages
            links = []
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                    links.append(full_url)

            # Slight delay to be respectful
            time.sleep(0.5)

            return links

        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            return []

    def crawl(self):
        """Start crawling from base URL"""
        to_visit = [self.base_url]

        while to_visit and len(self.visited_urls) < self.max_pages:
            url = to_visit.pop(0)
            new_links = self.crawl_page(url)
            to_visit.extend([link for link in new_links if link not in to_visit])

        # Remove duplicates
        self.content['testimonials'] = self._remove_duplicate_testimonials(self.content['testimonials'])
        self.content['team_members'] = self._remove_duplicate_team(self.content['team_members'])
        self.content['services'] = self._remove_duplicate_services(self.content['services'])

        print(f"\nCrawl complete!")
        print(f"Pages crawled: {len(self.visited_urls)}")
        print(f"Testimonials found: {len(self.content['testimonials'])}")
        print(f"Team members found: {len(self.content['team_members'])}")
        print(f"Services found: {len(self.content['services'])}")
        print(f"Achievements found: {len(self.content['achievements'])}")

        return self.content

    def _remove_duplicate_testimonials(self, testimonials):
        """Remove duplicate testimonials based on quote text"""
        seen = set()
        unique = []
        for t in testimonials:
            quote_key = t['quote'][:100]  # First 100 chars as key
            if quote_key not in seen:
                seen.add(quote_key)
                unique.append(t)
        return unique

    def _remove_duplicate_team(self, team):
        """Remove duplicate team members"""
        seen = set()
        unique = []
        for t in team:
            if t['name'] not in seen:
                seen.add(t['name'])
                unique.append(t)
        return unique

    def _remove_duplicate_services(self, services):
        """Remove duplicate services"""
        seen = set()
        unique = []
        for s in services:
            if s['title'] not in seen:
                seen.add(s['title'])
                unique.append(s)
        return unique


def crawl_all_brands():
    """Crawl all brand websites"""
    brands = {
        "sherrod-sports-visas": "https://www.sherrodsportsvisas.com",
        "igta": "https://www.innovativeglobaltalent.com",
        "aventus-visa-agents": "https://www.aventusvisaagents.com",
        "camino-immigration": "https://www.caminoimmigration.com",
        "innovative-automations": "https://www.innovativeautomations.dev"
    }

    all_content = {}

    for brand_id, url in brands.items():
        print(f"\n{'='*60}")
        print(f"Crawling {brand_id}: {url}")
        print(f"{'='*60}")

        crawler = WebsiteCrawler(url, max_pages=30)
        content = crawler.crawl()
        all_content[brand_id] = content

        print(f"\n✅ Completed {brand_id}")
        time.sleep(2)  # Delay between sites

    # Save to file
    output_file = "config/verified_content.json"
    with open(output_file, 'w') as f:
        json.dump(all_content, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ All crawling complete!")
    print(f"Data saved to: {output_file}")
    print(f"{'='*60}")

    return all_content


if __name__ == "__main__":
    crawl_all_brands()
