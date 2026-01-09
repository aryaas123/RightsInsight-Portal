def generate_complaint(category, incident):
    template = f"""
To,
The Concerned Authority

Subject: Complaint regarding {category}

Respected Sir/Madam,

I would like to bring to your attention an incident related to {category.lower()}.

Incident Description:
{incident}

This act appears to be a violation of my fundamental rights and has caused mental distress.

I kindly request you to look into this matter and take appropriate action.

Thanking you.

Yours sincerely,
Concerned Citizen
"""
    return template.strip()
