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