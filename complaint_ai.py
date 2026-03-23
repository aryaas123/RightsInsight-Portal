def generate_complaint(category, incident, username):
    authority_map = {
        "Workplace Discrimination": "The Labour Commissioner",
        "Harassment": "The Station House Officer, Local Police Station",
        "Privacy Violation": "The Cyber Crime Cell",
        "Denial of Education": "The Education Department",
        "Violation of Fundamental Rights": "The Human Rights Commission"
    }

    authority = authority_map.get(category, "The Concerned Authority")

    template = f"""
To,
{authority}

Subject: Complaint regarding {category}

Respected Sir/Madam,

I, {username}, would like to bring to your attention an incident related to {category.lower()}.

Incident Description:
{incident}

This act appears to be a violation of my fundamental rights and has caused mental distress.

I kindly request you to look into this matter and take appropriate action at the earliest.

Thanking you.

Yours sincerely,
{username}
"""

    return template.strip()
