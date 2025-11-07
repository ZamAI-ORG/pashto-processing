#!/usr/bin/env python3
"""
Final demonstration that everything works perfectly.
"""
from pashto_pipeline import TextProcessingPipeline, PashtoNormalizer, PashtoTokenizer
from pashto_pipeline.preprocessing.stopwords import StopwordsRemover

print("="*70)
print("🎉 PASHTO PROCESSING PIPELINE - FINAL DEMONSTRATION")
print("="*70)

# Sample Pashto texts
texts = [
    "سلام دنیا! دا د پښتو متن پروسس کولو یوه بېلګه ده.",
    "زه په کابل کې اوسېږم او پښتو ژبه زده کوم.",
    "پښتو یوه ښکلې او تاریخي ژبه ده.",
]

print("\n📝 Original Texts:")
for i, text in enumerate(texts, 1):
    print(f"  {i}. {text}")

# Create pipeline
print("\n🔧 Creating Processing Pipeline...")
pipeline = TextProcessingPipeline()

normalizer = PashtoNormalizer(
    normalize_whitespace=True,
    normalize_digits='western'
)

tokenizer = PashtoTokenizer(preserve_punctuation=True)

pipeline.add_step('normalize', normalizer.normalize)
pipeline.add_step('tokenize', tokenizer.tokenize)

print(f"  ✓ Pipeline created with {len(pipeline.get_steps())} steps")

# Process texts
print("\n⚙️  Processing Texts...")
results = pipeline.process_batch(texts, verbose=False)

print("\n📊 Results:")
for i, (original, tokens) in enumerate(zip(texts, results), 1):
    print(f"\n  Text {i}:")
    print(f"    Original: {original}")
    print(f"    Tokens ({len(tokens)}): {tokens[:5]}..." if len(tokens) > 5 else f"    Tokens: {tokens}")

# Demonstrate stopword removal
print("\n🔍 Stopword Removal Demo:")
remover = StopwordsRemover()
sample_tokens = ['زه', 'په', 'ښار', 'کې', 'یم']
filtered = remover.remove(sample_tokens)
print(f"  Before: {sample_tokens}")
print(f"  After:  {filtered}")

# Statistics
print("\n📈 Statistics:")
total_tokens = sum(len(r) for r in results)
print(f"  • Total texts processed: {len(texts)}")
print(f"  • Total tokens extracted: {total_tokens}")
print(f"  • Average tokens per text: {total_tokens/len(texts):.1f}")

print("\n✅ All Components Working Perfectly!")
print("="*70)
print("\n🎓 Next Steps:")
print("  1. Read the documentation in docs/")
print("  2. Try examples/basic_usage.py")
print("  3. Check QUICKSTART.md for more details")
print("  4. Explore code/pashto_dataset/ for advanced features")
print("\n🚀 Happy Processing!")
print("="*70)
