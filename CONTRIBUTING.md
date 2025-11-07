# Contributing to Pashto Processing Pipeline

Thank you for your interest in contributing to the Pashto Processing Pipeline! This document provides guidelines and instructions for contributing.

## 🌟 How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
   - Code samples if applicable

### Submitting Changes

1. **Fork the repository**
   ```bash
   git clone https://github.com/tasal9/Pashto-Processing-pipeline.git
   cd Pashto-Processing-pipeline
   ```

2. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make your changes**
   - Follow the coding style (see below)
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Run tests
   pytest
   
   # Run linting
   black .
   flake8
   isort .
   
   # Run installation test
   python test_installation.py
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature" # or "fix: resolve bug"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Wait for review

## 📝 Coding Standards

### Python Style

- Follow **PEP 8** guidelines
- Use **Black** for code formatting (line length: 100)
- Use **isort** for import sorting
- Use **type hints** where applicable
- Write **docstrings** for all public functions/classes

### Code Example

```python
"""
Module docstring explaining purpose.
"""

from typing import List, Optional


def process_text(
    text: str,
    normalize: bool = True,
    lowercase: Optional[bool] = None
) -> List[str]:
    """
    Process Pashto text.
    
    Args:
        text: Input text to process
        normalize: Whether to normalize the text
        lowercase: Optional lowercase conversion
        
    Returns:
        List of processed tokens
        
    Example:
        >>> process_text("سلام دنیا")
        ['سلام', 'دنیا']
    """
    # Implementation
    pass
```

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use meaningful test names
- Test edge cases

```python
def test_normalizer_removes_extra_spaces():
    """Test that normalizer removes multiple consecutive spaces."""
    normalizer = PashtoNormalizer(normalize_whitespace=True)
    result = normalizer.normalize("سلام   دنیا")
    assert "  " not in result
```

### Documentation

- Update README.md if adding features
- Add docstrings to all public APIs
- Include usage examples
- Update relevant guide documents in `docs/`

## 🔍 Development Setup

```bash
# Clone and setup
git clone https://github.com/tasal9/Pashto-Processing-pipeline.git
cd Pashto-Processing-pipeline

# Install in development mode
bash install.sh --dev

# Activate environment
source venv/bin/activate

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pashto_pipeline --cov-report=html

# Run specific test file
pytest tests/unit/test_normalizer.py

# Run linting
black --check .
flake8
isort --check-only .
```

## 📋 Pull Request Guidelines

### PR Title Format

Use conventional commits format:
- `feat: add new tokenization algorithm`
- `fix: resolve unicode normalization issue`
- `docs: update installation guide`
- `test: add tests for stopwords remover`
- `refactor: improve pipeline performance`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Added/updated tests
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
```

## 🎯 Areas for Contribution

We especially welcome contributions in:

1. **Pashto NLP Features**
   - Part-of-speech tagging
   - Named entity recognition
   - Sentiment analysis
   - Dialect detection

2. **Performance Improvements**
   - Optimization of existing code
   - Parallel processing enhancements
   - Memory usage reduction

3. **Documentation**
   - Usage examples
   - Tutorials
   - API documentation
   - Translation to Pashto

4. **Testing**
   - Unit tests
   - Integration tests
   - Test data creation

5. **Dataset Tools**
   - New data sources
   - Quality assessment metrics
   - Export formats

## 💬 Communication

- **Issues**: For bug reports and feature requests
- **Pull Requests**: For code contributions
- **Discussions**: For questions and general discussion

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints
- Prioritize community well-being

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Appreciated in the community!

## ❓ Questions?

If you have questions:
1. Check the [FAQ](docs/troubleshooting/faq.md)
2. Search existing issues
3. Open a new discussion
4. Ask in your PR/issue

Thank you for contributing to Pashto Processing Pipeline! 🙏
