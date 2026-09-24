import fitz
doc = fitz.open('.tmp/resumes/resume_1.pdf')
text = ""
for page in doc:
    text += page.get_text() + " "
print("Extracted len:", len(text))
print("Excerpt:", text[:200])
