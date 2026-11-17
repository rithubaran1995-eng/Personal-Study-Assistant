
import pymupdf

doc = pymupdf.open()
page = doc.new_page()

page.insert_text(
    (72, 72),
    "Personal RAG System PDF Test"
)

doc.save("documents/test.pdf")
doc.close()

doc = pymupdf.open("documents/test.pdf")

print("PDF pages:", len(doc))
print("Extracted text:", doc[0].get_text())

doc.close()
