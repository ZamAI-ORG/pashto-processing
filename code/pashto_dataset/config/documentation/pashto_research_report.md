# Pashto Dataset Pipeline Research Report

## Executive Summary

This document presents comprehensive research findings for establishing a Pashto text dataset pipeline, including reliable sources, technical challenges, encoding issues, and processing best practices for Arabic script languages.

## Language Characteristics

### Pashto Language Overview
- **Language Family**: Indo-European, Iranian branch
- **Primary Regions**: Afghanistan, Pakistan (Khyber Pakhtunkhwa), diaspora communities
- **Speakers**: ~50-60 million native speakers
- **Writing System**: Extended Arabic script (Perso-Arabic)
- **Script Direction**: Right-to-left (RTL)
- **Character Set**: 44+ alphabets including 27 standard Arabic letters + extended Pashto-specific characters

### Technical Challenges

#### 1. Character Encoding Issues
- **Unicode Complexity**: Pashto uses extended Arabic Unicode block (U+0600-U+06FF, U+0750-U+077F, U+FB50-U+FDFF, U+FE70-U+FEFF)
- **Multiple Representations**: Same character can be encoded in different Unicode forms
- **Normalization Required**: NFKC, NFC, NFD, or NFKD normalization may be needed
- **Diacritical Marks**: Extensive use of combining diacritical marks

#### 2. Right-to-Left Text Processing
- **Bidirectional Text**: Mixed LTR numbers and English words require careful handling
- **Layout Engine Issues**: Many text processing tools don't handle RTL properly
- **Cursor Movement**: Text editors may not handle RTL cursor positioning
- **Font Rendering**: Complex font substitution and shaping issues

#### 3. Cursive Script Challenges
- **Contextual Forms**: Characters change shape based on position (initial, medial, final, isolated)
- **Character Joining**: Most characters connect in running text
- **Ligature Issues**: Complex ligatures between character combinations
- **OCR Difficulties**: Handwritten and printed text recognition challenges

## Reliable Text Sources

### 1. Academic and Research Sources

#### CC100-Pashto Dataset
- **Source**: Metatext.io (CC-Net repository)
- **Description**: Monolingual data from Commoncrawl snapshots (2018)
- **Access**: Available through Metatext.io
- **Quality**: High-quality web-crawled text
- **Size**: Substantial dataset for training

#### English-Pashto Language Dataset (EPLD)
- **Source**: Kaggle (rabiakhan827)
- **Description**: Parallel corpus for language learning and NLP research
- **Access**: Public dataset on Kaggle
- **Quality**: Curated for educational/research purposes

#### NLPashto Corpus
- **Source**: Research papers and toolkit
- **Description**: 15+ million words corpus
- **Access**: Through research publications
- **Quality**: Manually curated for NLP applications

### 2. Digital Libraries and Archives

#### ACKU Digital Repository (Afghanistan Center at Kabul University)
- **URL**: https://www.afghandata.org/
- **Description**: Premier research institution with extensive primary resources
- **Content**: Books, manuscripts, newspapers, government documents
- **Languages**: Pashto, Dari, English
- **Access**: Online databases and digital archives
- **Quality**: Academic-grade, peer-reviewed materials

#### Afghanistan Digital Library (NYU)
- **URL**: https://findingaids.library.nyu.edu/archives/rg_38_29/
- **Description**: 576 digitized books, documents, and newspapers
- **Period**: Historical and contemporary materials
- **Topics**: Literature, politics, economics, jurisprudence, military
- **Access**: Digital archives
- **Quality**: Professional digitization

#### UCLA Library - Middle Eastern Studies
- **URL**: https://guides.library.ucla.edu/c.php?g=180194&p=1185888
- **Description**: Islamic manuscripts collection
- **Languages**: Arabic, Persian, Ottoman Turkish, some Pashto
- **Quality**: Significant academic collection

#### DigitalCommons@UNO - Dari and Pashto Books
- **URL**: https://digitalcommons.unomaha.edu/daripashtobooks/
- **Description**: Part of Arthur Paul Afghanistan Collection
- **Content**: Selected digitized materials (15% of collection)
- **Access**: Open access
- **Quality**: University-curated materials

### 3. Online Newspapers and Media

#### Afghan Central Press (MENALIB)
- **URL**: https://www.menalib.de/en/vifa/fid-lizenzen/afghan-central-press/
- **Description**: Digital archives of 4 Kabul-based newspapers
- **Content**: Contemporary news in Pashto and Dari
- **Access**: National license, academic access
- **Quality**: Professional journalism

#### Local Pashto News Sources
- **Anis** and **Kabul Times**: Available through various academic databases
- **Online Pashto media**: Multiple contemporary news websites
- **Quality**: Varies, requires filtering

### 4. Specialized Resources

#### Pashto Academy Peshawar
- **URL**: https://pashtoacademy.edu.pk/
- **Description**: Academic journal and research materials
- **Content**: Peer-reviewed Pashto language research
- **Access**: Academic subscription
- **Quality**: High academic standards

#### Archive.org Pashto Collection
- **URL**: https://archive.org/details/12-pashto
- **Description**: Various Pashto books and documents
- **Content**: Educational materials, literature
- **Access**: Open access
- **Quality**: Mixed, requires evaluation

## Scraping Strategies

### 1. Web Scraping Considerations

#### Technical Requirements
```python
# Essential libraries for Pashto web scraping
- requests/httpx: HTTP requests with proper encoding
- beautifulsoup4: HTML parsing with Unicode support
- lxml: XML/HTML parsing
- selenium: Dynamic content handling
- langdetect: Language identification
- python-arabic-reshaper: Arabic text processing
- python-bidi: Bidirectional text handling
```

#### Scraping Best Practices
- **Respect robots.txt**: Check scraping permissions
- **Rate Limiting**: Implement delays between requests
- **User-Agent Rotation**: Avoid detection
- **Session Management**: Maintain cookies and sessions
- **Error Handling**: Robust retry mechanisms

#### Pashto-Specific Challenges
- **Mixed Content**: Handle LTR numbers and English within RTL text
- **Encoding Detection**: Automatic detection of text encoding
- **Language Filtering**: Verify Pashto content using language detection
- **Content Cleaning**: Remove HTML tags while preserving Unicode

### 2. Academic Database Access

#### Library Database Scraping
- **Licensing**: Many require institutional access
- **API Access**: Some provide programmatic access
- **Rate Limits**: Strict request limitations
- **Data Export**: Batch download options when available

#### Government and Official Sources
- **Afghan Government**: Official documents in Pashto
- **Parliamentary Records**: Legislative documents
- **Legal Texts**: Laws and regulations
- **Access**: May require special permissions

### 3. Social Media and User-Generated Content

#### Platform Considerations
- **Twitter/X**: Hashtags and trends in Pashto
- **Facebook**: Community groups and pages
- **YouTube**: Transcripts of Pashto content
- **Accessibility**: Varies by platform

#### Content Quality Issues
- **Spam and Noise**: High volume of low-quality content
- **Language Mix**: Code-switching between Pashto, Dari, English
- **Informal Spelling**: Non-standard orthography
- **Moderation**: Content may require filtering

## Processing Pipeline Configuration

### 1. Text Preprocessing

#### Encoding Normalization
```python
# Unicode normalization pipeline
import unicodedata

def normalize_pashto_text(text):
    # Normalize Unicode forms
    text = unicodedata.normalize('NFC', text)
    
    # Handle Arabic script specific issues
    text = arabic_reshaper.reshape(text)
    text = get_display_layout(text)
    
    return text
```

#### Language Detection
- **Primary**: langdetect library with Pashto-specific training
- **Fallback**: Character-based analysis for Pashto script detection
- **Confidence Thresholds**: Minimum confidence levels for classification

#### Content Filtering
- **Minimum Length**: Filter out very short texts
- **Character Analysis**: Pashto character frequency analysis
- **Spam Detection**: Remove automated or templated content
- **Quality Scoring**: Implement content quality metrics

### 2. Quality Control

#### Automated Quality Checks
- **Character Validation**: Verify valid Pashto Unicode characters
- **Script Analysis**: Confirm RTL text handling
- **Encoding Integrity**: Check for character corruption
- **Language Consistency**: Verify Pashto language content

#### Manual Quality Review
- **Sampling**: Random sampling for human review
- **Expert Review**: Pashto language expert validation
- **Community Feedback**: Crowdsourced quality assessment

## Tools and Libraries

### 1. Pashto-Specific Tools

#### NLPashto Toolkit
- **Installation**: `pip install nlpashto`
- **Features**: Text cleaning, tokenization, stemming
- **Status**: Active development
- **Documentation**: Research paper available

#### Arabic Script Processing
- **python-arabic-reshaper**: Text reshaping for Arabic scripts
- **python-bidi**: Bidirectional text display
- **arabic-ewcl**: Extended word choice library
- **pyarabic**: Arabic text processing toolkit

### 2. General NLP Tools

#### Text Processing
- **NLTK**: Basic text processing with custom tokenization
- **spaCy**: Custom Pashto models needed
- **Transformers**: Hugging Face models for Pashto (limited)
- **Gensim**: Topic modeling and word embeddings

#### Machine Learning
- **scikit-learn**: Traditional ML algorithms
- **TensorFlow/PyTorch**: Deep learning models
- **FastText**: Word embeddings (requires training)
- **Sentence-BERT**: Sentence-level embeddings

## Configuration Templates

### 1. Source Configuration
```json
{
  "sources": {
    "digital_libraries": [
      {
        "name": "ACKU Digital Repository",
        "url": "https://www.afghandata.org/",
        "access_type": "api",
        "rate_limit": 60,
        "authentication": "required",
        "content_types": ["books", "manuscripts", "documents"],
        "languages": ["pashto", "dari"],
        "quality_score": 9
      }
    ],
    "newspapers": [
      {
        "name": "Afghan Central Press",
        "url": "https://www.menalib.de/",
        "access_type": "web",
        "rate_limit": 30,
        "content_types": ["news", "articles"],
        "languages": ["pashto", "dari"],
        "quality_score": 8
      }
    ]
  }
}
```

### 2. Processing Configuration
```json
{
  "processing": {
    "encoding": {
      "normalize_unicode": true,
      "normalization_form": "NFC",
      "handle_rtl": true,
      "font_requirements": ["Noto Sans Pashto", "Jameel Noori Nastaliq"]
    },
    "quality_filters": {
      "min_text_length": 50,
      "max_text_length": 50000,
      "min_pashto_ratio": 0.7,
      "remove_duplicates": true,
      "spam_detection": true
    },
    "output_formats": ["json", "csv", "txt", "xml"]
  }
}
```

## Sample Pashto Text

### Basic Sample
```
پښتو د پښتنو ژبه ده چې د افغانستان او پاکستان په ځینو سیمو کې ویل کېږي. 
دا ژبه د انډو-اروپایي کورنۍ څخه ده او د ایرانی ژبو برخه جوړوي.
```

### Complex Text Sample
```
د سولې د تاسیسولو لپاره، زموږ ټولو ته اړتیا ده چې د ټولنې د ښه والي په خاطر 
خپل ځانونه قرباني کړو. دغه راز د علومو د پراختیا او ټولنیز عدالت د رامنځته 
ولدولو لپاره باید دوامداره هڅې وکړو.
```

### Technical Text Sample
```
د کمپیوټر ټکنالوژۍ په ډېری برخو کې انقلاب رامنځته کړی. لکه څنګه چې 
د مصنوعي ذکاوت سیسټمونه د ژبو د پېژندلو او د معلوماتو د معالېجو 
په بریالیتوب کې ډېر پیشرفته شوي.
```

## Future Work Recommendations

### 1. Data Collection
- Establish partnerships with Afghan universities
- Collaborate with Pashto Academy Peshawar
- Develop API access to major digital libraries
- Create automated monitoring for new sources

### 2. Technical Development
- Enhance NLPashto toolkit capabilities
- Develop Pashto-specific transformer models
- Improve RTL text processing libraries
- Create standardized evaluation benchmarks

### 3. Quality Assurance
- Develop community-driven quality assessment
- Establish expert review panels
- Create automated quality metrics
- Build feedback mechanisms for data improvement

## Conclusion

The Pashto language represents a significant opportunity for NLP research and development, with growing digital resources and active academic communities. Success in building comprehensive Pashto datasets will require careful attention to technical challenges, strong partnerships with academic institutions, and robust quality control mechanisms.

The pipeline configuration provided in this document offers a structured approach to Pashto text collection and processing, addressing the unique challenges of RTL script processing and low-resource language datasets.