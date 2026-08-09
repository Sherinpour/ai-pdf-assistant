from app.services.embedding_service import create_embedding


text = "این قرارداد درباره شرایط فسخ قرارداد است."

embedding = create_embedding(text)

print("Embedding created successfully!")
print("Vector dimensions:", len(embedding))
print("First 5 values:", embedding[:5])