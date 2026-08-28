"""Seed the database with established civic knowledge so the app works from day one."""
from .database import SessionLocal, engine, Base
from . import models


RIGHTS = [
    {"title": "Right to remain silent during arrest", "description": "You are not obligated to answer police questions beyond identifying yourself until a legal representative is present.", "source_ref": "Constitution • Article 28", "category": "police", "article_ref": "Article 28"},
    {"title": "Right to be informed of the reason for arrest", "description": "Police must tell you the grounds of your arrest in a language you understand, at the time of arrest.", "source_ref": "Constitution • Article 23(1)", "category": "police", "article_ref": "Article 23(1)"},
    {"title": "Right to legal representation", "description": "You have the right to contact and consult a lawyer of your choice promptly upon arrest or detention.", "source_ref": "Constitution • Article 28(2)", "category": "police", "article_ref": "Article 28(2)"},
    {"title": "Right to be produced in court within 48 hours", "description": "A person arrested must be brought to court within 48 hours of arrest, or released.", "source_ref": "Constitution • Article 23(4)(b)", "category": "police", "article_ref": "Article 23(4)"},
    {"title": "Right to refuse an unwarranted search", "description": "Officers may not search your home or devices without a valid warrant naming the exact premises. Consent is not required.", "source_ref": "Constitution • Article 27", "category": "privacy", "article_ref": "Article 27"},
    {"title": "Right to access personal data", "description": "Citizens may request all stored digital profiles held about them and demand deletion of non-essential records.", "source_ref": "Data Protection Act • Sec. 18", "category": "privacy", "article_ref": "DPA Sec. 18"},
    {"title": "Right to consent before data processing", "description": "Organisations must obtain your explicit consent before collecting or processing your personal data.", "source_ref": "Data Protection Act • Sec. 5", "category": "privacy", "article_ref": "DPA Sec. 5"},
    {"title": "Right to a written employment contract", "description": "Employers must issue written terms within 12 weeks of a role starting, covering pay, hours, and dispute resolution.", "source_ref": "Employment Act • Sec. 41", "category": "labor", "article_ref": "Sec. 41"},
    {"title": "Right to timely payment of wages", "description": "Wages must be paid as contracted. Unpaid wages beyond agreed dates are recoverable through a labour officer.", "source_ref": "Employment Act • Sec. 36", "category": "labor", "article_ref": "Sec. 36"},
    {"title": "Right to fair termination procedures", "description": "Dismissal requires valid reason and fair procedure. Unfair dismissal entitles you to compensation.", "source_ref": "Employment Act • Sec. 58", "category": "labor", "article_ref": "Sec. 58"},
    {"title": "Right to maternity leave", "description": "Female employees are entitled to 60 working days of fully paid maternity leave.", "source_ref": "Employment Act • Sec. 56", "category": "labor", "article_ref": "Sec. 56"},
    {"title": "Right to own land", "description": "Every Ugandan citizen has the right to acquire and own land under the four land tenure systems.", "source_ref": "Constitution • Article 237", "category": "land", "article_ref": "Article 237"},
    {"title": "Protection against illegal eviction", "description": "No person may be evicted from registered land without a court order. Verbal threats are not lawful notice.", "source_ref": "Land Act • Sec. 33", "category": "land", "article_ref": "Sec. 33"},
    {"title": "Rights of lawful and bona fide occupants", "description": "Occupants on land for 12+ years before 1995 enjoy security of occupancy and cannot be evicted without compensation.", "source_ref": "Land Act • Sec. 29", "category": "land", "article_ref": "Sec. 29"},
    {"title": "Right to equality and freedom from discrimination", "description": "All persons are equal before and under the law and deserve equal protection regardless of gender, race, tribe, or religion.", "source_ref": "Constitution • Article 21", "category": "constitutional", "article_ref": "Article 21"},
    {"title": "Freedom of expression", "description": "Every person has the right to hold opinions and to receive and impart ideas and information freely.", "source_ref": "Constitution • Article 29(1)(a)", "category": "constitutional", "article_ref": "Article 29"},
    {"title": "Right to privacy of person and home", "description": "No person shall be subjected to interference with privacy of home, correspondence, communication, or other property.", "source_ref": "Constitution • Article 27", "category": "constitutional", "article_ref": "Article 27"},
]

BILLS = [
    {"title": "Data Protection & Privacy Amendment Bill", "description": "Establishes clear guidelines on platform data retention, user consent requirements, and commercial compliance penalties.", "stage": "PASSED SECOND READING", "current_stage": 2, "total_stages": 4, "article_ref": "Right to Privacy • Art. 27", "topic": "privacy", "source_name": "Parliament of Uganda", "source_url": "https://www.parliament.go.ug"},
    {"title": "National Employment & Fair Wages Policy Motion", "description": "Debating structural shifts in minimum wage indices and gig economy worker protections across commercial sectors.", "stage": "UNDER COMMITTEE REVIEW", "current_stage": 1, "total_stages": 4, "article_ref": "Right to Fair Wages • Art. 40", "topic": "labor", "source_name": "Parliament of Uganda", "source_url": "https://www.parliament.go.ug"},
    {"title": "Public Land Use & Boundary Reform Bill", "description": "Introduces digitized land title verification and dispute resolution timelines.", "stage": "FIRST READING", "current_stage": 1, "total_stages": 4, "article_ref": "Land Protection • Art. 237", "topic": "land", "source_name": "Ministry of Lands", "source_url": "https://www.mlhud.go.ug"},
]

ARTICLES = [
    {
        "title": "Data Protection Amendment Bill tabled",
        "category": "PARLIAMENT",
        "topic": "privacy",
        "summary": "New compliance mandates introduced for digital service providers regarding user consent.",
        "full_text": "The Data Protection Amendment Bill introduces strict compliance regulations for mobile financial tools and tech platforms operating in Uganda. Key updates mandate explicit user opt-in before processing biometrics or location logs.",
        "source_name": "Parliamentary Hansard Records",
        "source_url": "https://www.parliament.go.ug",
        "rights_impact": "Article 27: Digital Data Sovereignty",
        "dyk_text": "Did you know? Parliament discussed a Bill that could affect your digital privacy.",
        "sms_text": "CivicPulse: Parliament discussed changes that may affect digital privacy. Know what this could mean for you.",
        "is_live": True,
    },
    {
        "title": "Land Rights Regulations Update",
        "category": "PUBLIC GAZETTE",
        "topic": "land",
        "summary": "Ministry of Lands releases statutory guidelines on customary land registration rights.",
        "full_text": "The Ministry of Housing and Urban Development has gazetted new administrative procedures simplifying customary land ownership certificates for rural families.",
        "source_name": "Uganda Official Gazette Vol. CXVII",
        "source_url": "https://www.gazette.go.ug",
        "rights_impact": "Article 237: Land Ownership Protections",
        "dyk_text": "Did you know? New land registration guidelines were just released by the Ministry.",
        "sms_text": "CivicPulse: New land registration guidelines were gazetted today. See what changed for rural families.",
        "is_live": True,
    },
]

NOTIFICATIONS = [
    {"title": "Digital Eye alert", "message": "New urgent motion on data protection tabled in Parliament.", "tag": "PARLIAMENT", "is_read": False},
    {"title": "Law update", "message": "Employment Act amendment guidelines published.", "tag": "LABOR LAW", "is_read": False},
]

GUIDANCE = [
    {
        "title": "What do I do if I am stopped or arrested by police?",
        "category": "Police Action",
        "steps": [
            "Remain calm and request official police identification.",
            "State clearly that you are exercising your right to remain silent.",
            "Ask for the specific reason or offense for your arrest.",
            "Request immediate access to your advocate or legal representation.",
        ],
        "legal_ref": "Article 28 • Constitutional Safeguards",
    },
    {
        "title": "What do I do if my landlord threatens illegal eviction?",
        "category": "Housing Rights",
        "steps": [
            "Do not vacate under verbal threats; demand a formal written notice.",
            "Verify if the tenancy agreement specifies notice period obligations.",
            "Document all communications and rental receipt proof.",
            "Report unlawful lockouts or utility shutoffs to local legal aid authorities.",
        ],
        "legal_ref": "Landlord & Tenant Act • Notice Provisions",
    },
    {
        "title": "What do I do if my employer fails to pay my salary?",
        "category": "Employment Issue",
        "steps": [
            "Issue a written formal inquiry to your HR or management team.",
            "Keep copies of bank statements, contract agreements, and timesheets.",
            "File an official complaint with your local labor officer if unpaid past 7 days.",
        ],
        "legal_ref": "Employment Act • Wage Protection Provisions",
    },
    {
        "title": "What do I do if my rights have been violated?",
        "category": "Rights Violation",
        "steps": [
            "Document everything: dates, names, locations, and any evidence.",
            "Report the violation to the Uganda Human Rights Commission.",
            "Seek legal aid from an authorized legal aid provider.",
            "File a constitutional petition if fundamental rights are infringed.",
        ],
        "legal_ref": "Article 50 • Enforcement of Rights",
    },
]

SOURCES = [
    {"name": "Parliament of Uganda — Bills", "url": "https://www.parliament.go.ug/index.php/business/bills", "kind": "parliament"},
    {"name": "Parliament of Uganda — News", "url": "https://www.parliament.go.ug/index.php/news", "kind": "parliament"},
    {"name": "Uganda Government Portal — Announcements", "url": "https://www.statehouse.go.ug/news", "kind": "government"},
    {"name": "Uganda Legal Information Institute", "url": "https://ulii.org/", "kind": "legal"},
    {"name": "Uganda Police Force — News", "url": "https://upf.go.ug/", "kind": "police"},
    {"name": "Kenya Law — National Council for Law Reporting", "url": "https://new.kenyalaw.org/", "kind": "comparative"},
    {"name": "South African Legal Information Institute", "url": "https://www.saflii.org/", "kind": "comparative"},
    {"name": "UK Legislation", "url": "https://www.legislation.gov.uk/", "kind": "comparative"},
]


def seed():
    Base.metadata.create_all(bind=engine)
    # create_all does not add columns to existing installations.
    from sqlalchemy import inspect, text
    with engine.begin() as connection:
        columns = {column["name"] for column in inspect(engine).get_columns("notifications")}
        if "sms_text" not in columns:
            connection.execute(text("ALTER TABLE notifications ADD COLUMN sms_text TEXT DEFAULT ''"))
        if "image_url" not in columns:
            connection.execute(text("ALTER TABLE notifications ADD COLUMN image_url VARCHAR(1000) DEFAULT ''"))
        subscriber_columns = {column["name"] for column in inspect(engine).get_columns("sms_subscribers")}
        if "language" not in subscriber_columns:
            connection.execute(text("ALTER TABLE sms_subscribers ADD COLUMN language VARCHAR(20) DEFAULT 'eng'"))
        columns = {column["name"] for column in inspect(engine).get_columns("articles")}
        article_columns = {
            "jurisdiction": "VARCHAR(100) DEFAULT 'Uganda'",
            "plain_explanation": "TEXT DEFAULT ''",
            "original_wording": "TEXT DEFAULT ''",
            "law_citation": "VARCHAR(500) DEFAULT ''",
            "amendment_history": "TEXT DEFAULT ''",
        }
        for name, definition in article_columns.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE articles ADD COLUMN {name} {definition}"))
        if "image_url" not in columns:
            connection.execute(text("ALTER TABLE articles ADD COLUMN image_url VARCHAR(1000) DEFAULT ''"))
        columns = {column["name"] for column in inspect(engine).get_columns("sms_subscribers")}
        if "cadence_minutes" not in columns:
            connection.execute(text("ALTER TABLE sms_subscribers ADD COLUMN cadence_minutes INTEGER DEFAULT 30"))
        if "next_delivery_at" not in columns:
            connection.execute(text("ALTER TABLE sms_subscribers ADD COLUMN next_delivery_at DATETIME"))
    db = SessionLocal()
    try:
        if db.query(models.Right).count() == 0:
            db.add_all([models.Right(**r) for r in RIGHTS])
        if db.query(models.Bill).count() == 0:
            db.add_all([models.Bill(**b) for b in BILLS])
        if db.query(models.Article).count() == 0:
            db.add_all([models.Article(**a) for a in ARTICLES])
        if db.query(models.Notification).count() == 0:
            db.add_all([models.Notification(**n) for n in NOTIFICATIONS])
        if db.query(models.GuidanceItem).count() == 0:
            db.add_all([models.GuidanceItem(**g) for g in GUIDANCE])
        if db.query(models.Source).count() == 0:
            db.add_all([models.Source(**s) for s in SOURCES])
        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
