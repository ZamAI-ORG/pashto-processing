"""
Utility functions for file I/O operations.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union


def read_text_file(filepath: Union[str, Path], encoding: str = 'utf-8') -> str:
    """
    Read text from a file.
    
    Args:
        filepath: Path to the file
        encoding: File encoding (default: utf-8)
        
    Returns:
        File contents as string
    """
    filepath = Path(filepath)
    with filepath.open('r', encoding=encoding) as f:
        return f.read()


def write_text_file(
    filepath: Union[str, Path],
    content: str,
    encoding: str = 'utf-8'
) -> None:
    """
    Write text to a file.
    
    Args:
        filepath: Path to the file
        content: Content to write
        encoding: File encoding (default: utf-8)
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open('w', encoding=encoding) as f:
        f.write(content)


def read_lines(
    filepath: Union[str, Path],
    encoding: str = 'utf-8',
    strip: bool = True
) -> List[str]:
    """
    Read lines from a file.
    
    Args:
        filepath: Path to the file
        encoding: File encoding (default: utf-8)
        strip: Whether to strip whitespace from lines
        
    Returns:
        List of lines
    """
    filepath = Path(filepath)
    with filepath.open('r', encoding=encoding) as f:
        lines = f.readlines()
        if strip:
            lines = [line.strip() for line in lines]
        return lines


def write_lines(
    filepath: Union[str, Path],
    lines: List[str],
    encoding: str = 'utf-8'
) -> None:
    """
    Write lines to a file.
    
    Args:
        filepath: Path to the file
        lines: List of lines to write
        encoding: File encoding (default: utf-8)
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open('w', encoding=encoding) as f:
        for line in lines:
            f.write(line + '\n')


def read_json(filepath: Union[str, Path], encoding: str = 'utf-8') -> Dict[str, Any]:
    """
    Read JSON from a file.
    
    Args:
        filepath: Path to the JSON file
        encoding: File encoding (default: utf-8)
        
    Returns:
        Parsed JSON data
    """
    filepath = Path(filepath)
    with filepath.open('r', encoding=encoding) as f:
        return json.load(f)


def write_json(
    filepath: Union[str, Path],
    data: Dict[str, Any],
    encoding: str = 'utf-8',
    indent: int = 2
) -> None:
    """
    Write data to JSON file.
    
    Args:
        filepath: Path to the JSON file
        data: Data to write
        encoding: File encoding (default: utf-8)
        indent: JSON indentation level
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open('w', encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
