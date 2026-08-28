"""Approved public sources and Google News discovery searches."""
from urllib.parse import quote


def google_news_search(query: str) -> str:
    return f"https://news.google.com/rss/search?q={quote(query)}&hl=en-UG&gl=UG&ceid=UG:en"


APPROVED_SOURCES = [
    {
        "name": "Parliament of Uganda — Bills",
        "url": "https://www.parliament.go.ug/index.php/business/bills",
        "kind": "parliament",
    },
    {
        "name": "Parliament of Uganda — News",
        "url": "https://www.parliament.go.ug/index.php/news",
        "kind": "parliament",
    },
    {
        "name": "State House Uganda — News",
        "url": "https://www.statehouse.go.ug/news",
        "kind": "government",
    },
    {
        "name": "Uganda Legal Information Institute",
        "url": "https://ulii.org/",
        "kind": "legal",
    },
    {
        "name": "Uganda Police Force — News",
        "url": "https://upf.go.ug/",
        "kind": "police",
    },
    {
        "name": "Kenya Law — National Council for Law Reporting",
        "url": "https://new.kenyalaw.org/",
        "kind": "comparative",
    },
    {
        "name": "South African Legal Information Institute",
        "url": "https://www.saflii.org/",
        "kind": "comparative",
    },
    {
        "name": "UK Legislation",
        "url": "https://www.legislation.gov.uk/",
        "kind": "comparative",
    },
    {
        "name": "Google News — Uganda trends",
        "url": google_news_search("Uganda trending civic news OR public policy"),
        "kind": "trending",
    },
    {
        "name": "Google News — X public posts",
        "url": google_news_search("site:x.com/Parliament_Ug OR site:x.com/PoliceUg OR site:x.com/StateHouseUg OR site:x.com/GCICUganda Uganda"),
        "kind": "trending",
    },
    {
        "name": "Google News — Ugandan breaking news",
        "url": google_news_search("site:x.com/NewVisionWire OR site:x.com/DailyMonitor Uganda breaking news"),
        "kind": "trending",
    },
    {
        "name": "Google News — Uganda laws",
        "url": google_news_search("Uganda Constitution law court legal rights"),
        "kind": "law",
    },
    {
        "name": "Google News — global legal comparisons",
        "url": google_news_search("law rights comparison Uganda Kenya South Africa UK"),
        "kind": "comparison",
    },
]
