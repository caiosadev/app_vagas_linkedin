import fitz
doc = fitz.open('.tmp/resumes/resume_1.pdf')
page = doc[0]
print("Images:", len(page.get_images()))
print("Drawings:", len(page.get_drawings()))
print("Text length:", len(page.get_text()))
