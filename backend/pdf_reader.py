from pypdf import PdfReader


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text


pdf_file = "papers/research.pdf"

content = extract_text(pdf_file)

print(content[:2000])