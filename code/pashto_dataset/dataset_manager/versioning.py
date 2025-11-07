"""
Dataset Versioning
=================

Handles dataset versioning and history management.
"""

import json
import logging
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from packaging import version
from datasets import Dataset

from .config import DatasetConfig


class DatasetVersioning:
    """Manages dataset versioning and history."""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        self.versions_file = self.config.metadata_path / "versions.json"
        self.logger = logging.getLogger(f"Versioning[{config.dataset_name}]")
    
    def generate_version(self, major: Optional[int] = None, 
                        minor: Optional[int] = None, 
                        patch: Optional[int] = None,
                        tag: Optional[str] = None) -> str:
        """
        Generate a new version string.
        
        Args:
            major: Major version number
            minor: Minor version number
            patch: Patch version number
            tag: Version tag (alpha, beta, rc, etc.)
            
        Returns:
            Version string in semver format
        """
        # Get latest version
        latest = self.get_latest_version()
        
        if latest:
            # Parse latest version
            parsed = self._parse_version(latest)
            
            # Use provided numbers or increment
            major = major or parsed['major']
            minor = minor or parsed['minor']
            patch = patch or parsed['patch'] + 1
        else:
            # First version
            major = major or 1
            minor = minor or 0
            patch = patch or 0
        
        # Build version string
        version_parts = [str(major), str(minor), str(patch)]
        
        # Add tag if provided
        if tag:
            version_parts.append(f"-{tag}")
        
        version_str = ".".join(version_parts)
        
        self.logger.info(f"Generated new version: {version_str}")
        return version_str
    
    def create_version(self, dataset: Dataset, version: str, 
                      description: str = "", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a new version of the dataset.
        
        Args:
            dataset: Dataset to version
            version: Version string
            description: Version description
            metadata: Additional metadata
            
        Returns:
            Version information dictionary
        """
        self.logger.info(f"Creating version: {version}")
        
        # Calculate dataset hash for integrity
        dataset_hash = self._calculate_dataset_hash(dataset)
        
        # Create version information
        version_info = {
            "version": version,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "dataset_hash": dataset_hash,
            "num_samples": len(dataset),
            "size_mb": dataset.dataset_size / (1024 * 1024),
            "memory_usage_mb": dataset.nbytes / (1024 * 1024),
            "columns": list(dataset.column_names),
            "features": dataset.features.to_dict(),
            "metadata": metadata or {}
        }
        
        # Save version information
        self._save_version_info(version, version_info)
        
        # Update versions registry
        self._update_versions_registry(version_info)
        
        self.logger.info(f"Version {version} created successfully")
        return version_info
    
    def get_version_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific version."""
        version_file = self.config.metadata_path / f"version_{version}.json"
        
        if not version_file.exists():
            return None
        
        with open(version_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_latest_version(self) -> Optional[str]:
        """Get the latest version number."""
        versions = self.list_all_versions()
        return versions[0] if versions else None
    
    def list_all_versions(self) -> List[str]:
        """List all available versions in chronological order."""
        versions_registry = self._load_versions_registry()
        
        if not versions_registry or "versions" not in versions_registry:
            return []
        
        # Sort versions using semantic versioning
        versions = []
        for version_info in versions_registry["versions"]:
            version_str = version_info["version"]
            if self._is_valid_semver(version_str):
                versions.append((version_str, version_info.get("created_at", "")))
        
        # Sort by version number and then by creation date
        def sort_key(item):
            version_str, created_at = item
            parsed = self._parse_version(version_str)
            return (parsed['major'], parsed['minor'], parsed['patch'], created_at)
        
        versions.sort(key=sort_key, reverse=True)
        return [v[0] for v in versions]
    
    def compare_versions(self, version1: str, version2: str) -> Dict[str, Any]:
        """
        Compare two versions and return differences.
        
        Args:
            version1: First version
            version2: Second version
            
        Returns:
            Comparison results
        """
        info1 = self.get_version_info(version1)
        info2 = self.get_version_info(version2)
        
        if not info1 or not info2:
            return {"error": "One or both versions not found"}
        
        comparison = {
            "version1": version1,
            "version2": version2,
            "samples_diff": info2["num_samples"] - info1["num_samples"],
            "size_diff_mb": info2["size_mb"] - info1["size_mb"],
            "columns_added": list(set(info2["columns"]) - set(info1["columns"])),
            "columns_removed": list(set(info1["columns"]) - set(info2["columns"])),
            "created_at_diff": self._calculate_time_diff(info1["created_at"], info2["created_at"])
        }
        
        return comparison
    
    def revert_to_version(self, version: str) -> Optional[Dataset]:
        """
        Revert to a previous version of the dataset.
        
        Note: This requires the original dataset files to still exist.
        """
        self.logger.info(f"Reverting to version: {version}")
        
        # Check if version exists
        version_info = self.get_version_info(version)
        if not version_info:
            raise ValueError(f"Version {version} not found")
        
        # Load dataset from the specific version
        version_dir = self.config.data_path / f"v{version}"
        if not version_dir.exists():
            raise ValueError(f"Dataset files for version {version} not found")
        
        # This would need to be implemented in the DatasetCreator
        # For now, return None to indicate the operation
        self.logger.warning("Revert operation requires DatasetCreator integration")
        return None
    
    def create_branch(self, base_version: str, branch_name: str, 
                     description: str = "") -> str:
        """
        Create a new branch from an existing version.
        
        Args:
            base_version: Base version for the branch
            branch_name: Name of the new branch
            description: Branch description
            
        Returns:
            New version string
        """
        self.logger.info(f"Creating branch '{branch_name}' from version {base_version}")
        
        # Generate new version with branch tag
        new_version = self.generate_version(tag=branch_name)
        
        # Get base version info
        base_info = self.get_version_info(base_version)
        if not base_info:
            raise ValueError(f"Base version {base_version} not found")
        
        # Create branch version
        branch_info = {
            "version": new_version,
            "description": description or f"Branch from {base_version}",
            "created_at": datetime.now().isoformat(),
            "base_version": base_version,
            "branch": branch_name,
            "dataset_hash": base_info["dataset_hash"],  # Same as base
            "num_samples": base_info["num_samples"],
            "size_mb": base_info["size_mb"],
            "columns": base_info["columns"],
            "features": base_info["features"]
        }
        
        # Save branch version
        self._save_version_info(new_version, branch_info)
        self._update_versions_registry(branch_info)
        
        self.logger.info(f"Branch '{branch_name}' created as version {new_version}")
        return new_version
    
    def tag_version(self, version: str, tag: str, description: str = "") -> str:
        """
        Tag a version with a semantic tag.
        
        Args:
            version: Version to tag
            tag: Tag name
            description: Tag description
            
        Returns:
            New version string with tag
        """
        self.logger.info(f"Tagging version {version} with '{tag}'")
        
        # Parse version and add tag
        parsed = self._parse_version(version)
        tagged_version = f"{parsed['major']}.{parsed['minor']}.{parsed['patch']}-{tag}"
        
        # Copy version info
        original_info = self.get_version_info(version)
        if not original_info:
            raise ValueError(f"Version {version} not found")
        
        # Create tagged version
        tagged_info = original_info.copy()
        tagged_info.update({
            "version": tagged_version,
            "tag": tag,
            "description": description or f"Tagged version of {version}",
            "created_at": datetime.now().isoformat()
        })
        
        # Save tagged version
        self._save_version_info(tagged_version, tagged_info)
        self._update_versions_registry(tagged_info)
        
        self.logger.info(f"Version {version} tagged as {tagged_version}")
        return tagged_version
    
    def _calculate_dataset_hash(self, dataset: Dataset) -> str:
        """Calculate a hash for the dataset for integrity checking."""
        # Create a string representation of the dataset
        # This is a simplified approach - in practice, you might want to hash
        # the actual data in a more sophisticated way
        dataset_str = f"{len(dataset)}_{len(dataset.column_names)}_{dataset.dataset_size}"
        return hashlib.sha256(dataset_str.encode()).hexdigest()[:16]
    
    def _save_version_info(self, version: str, version_info: Dict[str, Any]):
        """Save version information to file."""
        version_file = self.config.metadata_path / f"version_{version}.json"
        
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)
    
    def _load_versions_registry(self) -> Dict[str, Any]:
        """Load the versions registry."""
        if not self.versions_file.exists():
            return {"versions": []}
        
        with open(self.versions_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _update_versions_registry(self, version_info: Dict[str, Any]):
        """Update the versions registry."""
        registry = self._load_versions_registry()
        
        # Check if version already exists
        existing_idx = None
        for i, v in enumerate(registry["versions"]):
            if v["version"] == version_info["version"]:
                existing_idx = i
                break
        
        if existing_idx is not None:
            registry["versions"][existing_idx] = version_info
        else:
            registry["versions"].append(version_info)
        
        # Save registry
        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def _parse_version(self, version_str: str) -> Dict[str, int]:
        """Parse version string into components."""
        # Handle tags
        if '-' in version_str:
            version_part, tag = version_str.split('-', 1)
        else:
            version_part = version_str
            tag = None
        
        # Parse version numbers
        parts = version_part.split('.')
        major = int(parts[0]) if len(parts) > 0 else 1
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        
        return {"major": major, "minor": minor, "patch": patch, "tag": tag}
    
    def _is_valid_semver(self, version_str: str) -> bool:
        """Check if version string is valid semantic version."""
        try:
            self._parse_version(version_str)
            return True
        except:
            return False
    
    def _calculate_time_diff(self, time1: str, time2: str) -> str:
        """Calculate time difference between two ISO timestamps."""
        try:
            dt1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
            dt2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
            
            diff = abs(dt2 - dt1)
            days = diff.days
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Unknown"