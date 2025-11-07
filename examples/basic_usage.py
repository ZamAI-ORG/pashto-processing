"""
Basic example of using the Pashto Processing Pipeline.
"""

from pashto_pipeline import PashtoNormalizer, PashtoTokenizer, TextProcessingPipeline


def main():
    # Sample Pashto text
    text = "سلام   دنیا! دا د پښتو متن پروسس کولو یوه ساده بېلګه ده."
    
    print("Original text:")
    print(text)
    print("\n" + "="*50 + "\n")
    
    # Initialize components
    normalizer = PashtoNormalizer(
        normalize_whitespace=True,
        normalize_digits='western'
    )
    tokenizer = PashtoTokenizer(preserve_punctuation=True)
    
    # Method 1: Use components directly
    print("Method 1: Direct usage")
    print("-" * 50)
    
    normalized = normalizer.normalize(text)
    print(f"Normalized: {normalized}")
    
    tokens = tokenizer.tokenize(normalized)
    print(f"Tokens: {tokens}")
    
    print("\n" + "="*50 + "\n")
    
    # Method 2: Use pipeline
    print("Method 2: Using Pipeline")
    print("-" * 50)
    
    pipeline = TextProcessingPipeline()
    pipeline.add_step('normalize', normalizer.normalize)
    pipeline.add_step('tokenize', tokenizer.tokenize)
    
    result = pipeline.process(text, verbose=True)
    print(f"Pipeline result: {result}")
    
    print("\n" + "="*50 + "\n")
    
    # Method 3: Batch processing
    print("Method 3: Batch Processing")
    print("-" * 50)
    
    texts = [
        "زه په کابل کې اوسېږم.",
        "پښتو یوه ښکلې ژبه ده.",
        "نن ډېره ښه ورځ ده."
    ]
    
    # Simple pipeline for normalization only
    simple_pipeline = TextProcessingPipeline()
    simple_pipeline.add_step('normalize', normalizer.normalize)
    
    results = simple_pipeline.process_batch(texts, verbose=True)
    
    print("\nBatch results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result}")


if __name__ == "__main__":
    main()
