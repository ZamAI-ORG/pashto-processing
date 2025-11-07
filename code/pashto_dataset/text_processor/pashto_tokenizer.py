"""
Pashto Tokenizer

Advanced tokenization for Pashto text handling:
- Right-to-left script tokenization
- Pashto-specific word boundaries
- Sentence splitting
- Cursive script handling
"""

import re
from typing import List, Dict, Tuple, Set
import unicodedata

class PashtoTokenizer:
    """Pashto text tokenizer with script-aware processing"""
    
    def __init__(self):
        # Pashto specific punctuation and symbols
        self.pashto_punctuation = set([
            '،', '؛', '؟', '!', '.', ',', ';', ':', '"', "'", '(', ')', 
            '[', ']', '{', '}', '<', '>', '/', '\\', '|', '-', '–', '—',
            '_', '=', '+', '*', '%', '$', '#', '@', '^', '~', '`'
        ])
        
        # Pashto sentence ending punctuation
        self.sentence_endings = set(['.', '!', '؟', '۔', '۔'])
        
        # Common Pashto abbreviations
        self.pashto_abbreviations = {
            'ډاکټر', 'ډکټر',  # Doctor
            'پروفیسور',        # Professor
            'زموږ', 'زهږ', 'تهږ',  # Pronouns
            'د', 'تر', 'پر',   # Prepositions
        }
        
        # Unicode script detection
        self.arabic_script_chars = set()
        for char in range(0x0600, 0x06FF + 1):
            self.arabic_script_chars.add(chr(char))
        for char in range(0x0750, 0x077F + 1):
            self.arabic_script_chars.add(chr(char))
        for char in range(0x08A0, 0x08FF + 1):
            self.arabic_script_chars.add(chr(char))
        
        # Tokenization patterns
        # Create a pattern that matches Arabic script characters
        arabic_chars = ''.join(self.arabic_script_chars)
        self.word_pattern = re.compile(
            f'([{re.escape(arabic_chars)}]+)', 
            re.UNICODE
        )
        self.punctuation_pattern = re.compile(
            r'([\s' + re.escape(''.join(self.pashto_punctuation)) + r']+)', 
            re.UNICODE
        )
        
    def is_arabic_script_text(self, text: str) -> bool:
        """Check if text primarily contains Arabic script characters"""
        if not text:
            return False
            
        arabic_count = sum(1 for char in text if char in self.arabic_script_chars)
        total_count = len(text)
        
        return arabic_count / total_count > 0.5 if total_count > 0 else False
    
    def find_word_boundaries(self, text: str) -> List[Tuple[int, int, str]]:
        """
        Find word boundaries in Pashto text
        
        Returns:
            List of (start, end, word) tuples
        """
        words = []
        matches = self.word_pattern.finditer(text)
        
        for match in matches:
            word = match.group(1)
            if word.strip():  # Only non-empty words
                words.append((match.start(), match.end(), word))
        
        return words
    
    def find_sentence_boundaries(self, text: str) -> List[Tuple[int, int, str]]:
        """
        Find sentence boundaries in Pashto text
        """
        sentences = []
        
        # Split on sentence ending punctuation
        sentence_pattern = re.compile(
            r'([.!?؟۔]+)', 
            re.UNICODE
        )
        
        current_pos = 0
        for match in sentence_pattern.finditer(text):
            sentence_end = match.end()
            sentence = text[current_pos:sentence_end].strip()
            
            if sentence:
                sentences.append((current_pos, sentence_end, sentence))
            
            current_pos = sentence_end
        
        # Add remaining text as last sentence
        if current_pos < len(text):
            remaining = text[current_pos:].strip()
            if remaining:
                sentences.append((current_pos, len(text), remaining))
        
        return sentences
    
    def tokenize_words(self, text: str) -> List[Dict[str, any]]:
        """
        Tokenize text into words with metadata
        """
        if not text or not text.strip():
            return []
        
        words = []
        word_boundaries = self.find_word_boundaries(text)
        
        for start, end, word in word_boundaries:
            # Remove surrounding punctuation
            clean_word = self._clean_word(word)
            
            if clean_word:
                word_info = {
                    'text': clean_word,
                    'original': word,
                    'start': start,
                    'end': end,
                    'length': len(clean_word),
                    'is_pashto': self._is_pashto_word(clean_word),
                    'script_type': self._get_script_type(clean_word)
                }
                words.append(word_info)
        
        return words
    
    def tokenize_sentences(self, text: str) -> List[Dict[str, any]]:
        """
        Tokenize text into sentences
        """
        if not text or not text.strip():
            return []
        
        sentences = []
        sentence_boundaries = self.find_sentence_boundaries(text)
        
        for i, (start, end, sentence) in enumerate(sentence_boundaries):
            sentence_info = {
                'text': sentence,
                'start': start,
                'end': end,
                'length': len(sentence),
                'word_count': len(self.tokenize_words(sentence)),
                'sentence_number': i + 1,
                'is_complete': self._is_complete_sentence(sentence)
            }
            sentences.append(sentence_info)
        
        return sentences
    
    def tokenize_complete(self, text: str) -> Dict[str, any]:
        """
        Complete tokenization with all levels
        """
        if not text or not text.strip():
            return {
                'text': text,
                'sentences': [],
                'words': [],
                'tokens': [],
                'metadata': self._get_empty_metadata()
            }
        
        sentences = self.tokenize_sentences(text)
        words = self.tokenize_words(text)
        
        # Create individual tokens (words + punctuation)
        tokens = self._create_tokens(text, words)
        
        metadata = self._calculate_metadata(text, sentences, words, tokens)
        
        return {
            'text': text,
            'sentences': sentences,
            'words': words,
            'tokens': tokens,
            'metadata': metadata
        }
    
    def _clean_word(self, word: str) -> str:
        """Clean word by removing surrounding punctuation"""
        # Remove leading and trailing punctuation
        cleaned = word.strip(''.join(self.pashto_punctuation))
        return cleaned
    
    def _is_pashto_word(self, word: str) -> bool:
        """Determine if word is likely Pashto based on characteristics"""
        if not word:
            return False
        
        # Check for Pashto-specific characters
        pashto_chars = 'ځڅډړګڼ'
        has_pashto_chars = any(char in word for char in pashto_chars)
        
        if has_pashto_chars:
            return True
        
        # Check if primarily Arabic script
        script_ratio = sum(1 for char in word if char in self.arabic_script_chars) / len(word)
        return script_ratio > 0.7
    
    def _get_script_type(self, word: str) -> str:
        """Determine the script type of the word"""
        if not word:
            return 'empty'
        
        arabic_count = sum(1 for char in word if char in self.arabic_script_chars)
        latin_count = sum(1 for char in word if char.isascii() and char.isalpha())
        
        if arabic_count > latin_count:
            return 'arabic_script'
        elif latin_count > arabic_count:
            return 'latin_script'
        else:
            return 'mixed_script'
    
    def _is_complete_sentence(self, sentence: str) -> bool:
        """Check if sentence appears to be complete"""
        if not sentence:
            return False
        
        # Check for sentence ending punctuation
        has_ending = any(sentence.strip().endswith(char) for char in self.sentence_endings)
        
        # Check minimum length for a complete sentence
        min_length = len(sentence.strip()) >= 5
        
        # Check if contains verbs or meaningful structure (simple heuristic)
        contains_verb = any(verb in sentence for verb in ['دي', 'دی', 'لري', 'ورکړل', 'کول'])
        
        return has_ending and min_length and contains_verb
    
    def _create_tokens(self, text: str, words: List[Dict]) -> List[Dict]:
        """Create individual tokens from text and word positions"""
        tokens = []
        
        # Sort words by position
        words = sorted(words, key=lambda x: x['start'])
        
        # Process each word with surrounding context
        for i, word_info in enumerate(words):
            start, end = word_info['start'], word_info['end']
            
            # Add punctuation before word if any
            if i == 0 and start > 0:
                before_text = text[:start]
                if before_text.strip():
                    tokens.append({
                        'text': before_text.strip(),
                        'start': 0,
                        'end': start,
                        'type': 'punctuation'
                    })
            
            # Add the word
            tokens.append({
                'text': word_info['text'],
                'start': start,
                'end': end,
                'type': 'word',
                'is_pashto': word_info['is_pashto'],
                'script_type': word_info['script_type']
            })
            
            # Add text between this word and next word
            if i < len(words) - 1:
                next_start = words[i + 1]['start']
                between_text = text[end:next_start]
                if between_text.strip():
                    tokens.append({
                        'text': between_text.strip(),
                        'start': end,
                        'end': next_start,
                        'type': 'punctuation'
                    })
            else:
                # Add text after last word to end of text
                if end < len(text):
                    after_text = text[end:]
                    if after_text.strip():
                        tokens.append({
                            'text': after_text.strip(),
                            'start': end,
                            'end': len(text),
                            'type': 'punctuation'
                        })
        
        return tokens
    
    def _get_empty_metadata(self) -> Dict:
        """Return empty metadata structure"""
        return {
            'total_sentences': 0,
            'total_words': 0,
            'total_tokens': 0,
            'pashto_word_ratio': 0.0,
            'script_distribution': {},
            'average_sentence_length': 0.0,
            'average_word_length': 0.0
        }
    
    def _calculate_metadata(self, text: str, sentences: List, words: List, tokens: List) -> Dict:
        """Calculate tokenization metadata"""
        total_sentences = len(sentences)
        total_words = len(words)
        total_tokens = len(tokens)
        
        # Count script distribution
        script_dist = {'arabic_script': 0, 'latin_script': 0, 'mixed_script': 0}
        pashto_word_count = 0
        
        for word in words:
            script_type = word['script_type']
            if script_type in script_dist:
                script_dist[script_type] += 1
            if word['is_pashto']:
                pashto_word_count += 1
        
        # Calculate averages
        avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
        avg_word_length = sum(word['length'] for word in words) / total_words if total_words > 0 else 0
        
        return {
            'total_sentences': total_sentences,
            'total_words': total_words,
            'total_tokens': total_tokens,
            'pashto_word_ratio': pashto_word_count / total_words if total_words > 0 else 0.0,
            'script_distribution': script_dist,
            'average_sentence_length': round(avg_sentence_length, 2),
            'average_word_length': round(avg_word_length, 2),
            'text_length': len(text),
            'pashto_score': self._calculate_pashto_indicator_score(text)
        }
    
    def _calculate_pashto_indicator_score(self, text: str) -> float:
        """Calculate Pashto indicator score for the text"""
        if not text:
            return 0.0
        
        pashto_chars = 'ځڅډړګڼ'
        pashto_count = sum(text.count(char) for char in pashto_chars)
        
        return (pashto_count / len(text)) * 10 if len(text) > 0 else 0.0
    
    def batch_tokenize(self, texts: List[str]) -> List[Dict[str, any]]:
        """Tokenize multiple texts in batch"""
        return [self.tokenize_complete(text) for text in texts]