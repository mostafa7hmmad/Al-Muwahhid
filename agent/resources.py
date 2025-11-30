import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

def search_site(query, site_url, max_results=3):
    """بحث على الموقع باستخدام Google ورجع نتائج متعددة"""
    try:
        search_query = f"site:{site_url} {query}"
        url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # استخراج النتائج
        results = []
        search_results = soup.find_all("div", class_="g", limit=max_results)
        
        for result in search_results:
            # العنوان
            title_tag = result.find("h3")
            title = title_tag.get_text() if title_tag else ""
            
            # الوصف/المقتطف
            snippet_tag = result.find("div", class_="VwiC3b")
            if not snippet_tag:
                snippet_tag = result.find("span")
            snippet = snippet_tag.get_text() if snippet_tag else ""
            
            # الرابط
            link_tag = result.find("a")
            link = link_tag.get("href") if link_tag else ""
            
            if snippet:
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link,
                    "source": site_url
                })
        
        # دمج النتائج في نص واحد
        combined = ""
        for i, res in enumerate(results, 1):
            combined += f"\n[{i}] من {res['source']}:\n{res['title']}\n{res['snippet']}\n"
        
        return combined if combined else ""
        
    except Exception as e:
        print(f"⚠️ خطأ في البحث على {site_url}: {e}")
        return ""

def fetch_page_content(url):
    """جلب محتوى صفحة ويب كاملة"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # إزالة العناصر غير الضرورية
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # استخراج النص
        text = soup.get_text(separator="\n", strip=True)
        
        # تنظيف النص
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)
        
    except Exception as e:
        print(f"⚠️ خطأ في جلب الصفحة {url}: {e}")
        return ""