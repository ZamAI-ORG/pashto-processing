"""
Text Processing Pipeline
Main pipeline class for orchestrating text processing steps.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

from tqdm import tqdm


class TextProcessingPipeline:
    """
    A flexible pipeline for processing Pashto text through multiple stages.
    
    This class allows chaining multiple processing steps and applying them
    to text data in sequence.
    
    Example:
        >>> pipeline = TextProcessingPipeline()
        >>> pipeline.add_step('normalize', normalizer.normalize)
        >>> pipeline.add_step('tokenize', tokenizer.tokenize)
        >>> result = pipeline.process("سلام دنیا")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the pipeline.
        
        Args:
            config: Optional configuration dictionary for the pipeline
        """
        self.steps: List[Tuple[str, Callable, Dict]] = []
        self.config = config or {}
        
    def add_step(self, name: str, function: Callable, **kwargs) -> 'TextProcessingPipeline':
        """
        Add a processing step to the pipeline.
        
        Args:
            name: Name identifier for the step
            function: The function to apply in this step
            **kwargs: Additional arguments to pass to the function
            
        Returns:
            Self for method chaining
        """
        self.steps.append((name, function, kwargs))
        return self
        
    def remove_step(self, name: str) -> 'TextProcessingPipeline':
        """
        Remove a step from the pipeline by name.
        
        Args:
            name: Name of the step to remove
            
        Returns:
            Self for method chaining
        """
        self.steps = [(n, f, k) for n, f, k in self.steps if n != name]
        return self
        
    def process(self, text: str, verbose: bool = False) -> str:
        """
        Process text through all pipeline steps.
        
        Args:
            text: Input text to process
            verbose: Whether to show progress information
            
        Returns:
            Processed text
        """
        result = text
        
        iterator = tqdm(self.steps, desc="Processing") if verbose else self.steps
        
        for name, function, kwargs in iterator:
            if verbose:
                iterator.set_description(f"Processing: {name}")
            result = function(result, **kwargs)
            
        return result
        
    def process_batch(
        self, 
        texts: List[str], 
        verbose: bool = True
    ) -> List[str]:
        """
        Process multiple texts through the pipeline.
        
        Args:
            texts: List of input texts to process
            verbose: Whether to show progress bar
            
        Returns:
            List of processed texts
        """
        results = []
        
        iterator = tqdm(texts, desc="Batch Processing") if verbose else texts
        
        for text in iterator:
            results.append(self.process(text, verbose=False))
            
        return results
        
    def get_steps(self) -> List[str]:
        """
        Get list of step names in the pipeline.
        
        Returns:
            List of step names
        """
        return [name for name, _, _ in self.steps]
        
    def clear(self) -> 'TextProcessingPipeline':
        """
        Clear all steps from the pipeline.
        
        Returns:
            Self for method chaining
        """
        self.steps = []
        return self
        
    def __repr__(self) -> str:
        """String representation of the pipeline."""
        steps_str = ", ".join(self.get_steps())
        return f"TextProcessingPipeline(steps=[{steps_str}])"
