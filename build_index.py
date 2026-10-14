import time
from pdf_knowledge import extract_all_chunks

print("Indexing all PDFs...")
start = time.time()
data = extract_all_chunks(force_refresh=True)
num_chunks = len(data.get("chunks", []))
print(f"Indexed {num_chunks} chunks in {time.time() - start:.2f} seconds!")
