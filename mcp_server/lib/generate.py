# This is a placeholder for the actual JD generation function.
def generate_jd(title, department, requirements, similar):
    return {
        "title": title,
        "department": department,
        "sections": {
            "intro": f"Draft JD for {title} in {department}",
            "responsibilities": [],
            "requirements": requirements
        },
        "metadata": {"generated": True}
    } 