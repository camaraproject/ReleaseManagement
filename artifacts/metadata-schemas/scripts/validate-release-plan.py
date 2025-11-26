#!/usr/bin/env python3
"""
CAMARA Release Metadata Validator

Validates release-plan.yaml and release-metadata.yaml files against their
respective JSON schemas. Performs basic schema validation and semantic checks.

Usage:
    python3 validate-release-plan.py <metadata-file> [--schema <schema-file>] [--check-files]

Examples:
    # Validate release plan with auto-detected schema
    python3 validate-release-plan.py release-plan.yaml

    # Validate with explicit schema
    python3 validate-release-plan.py release-plan.yaml --schema ../schemas/release-plan-schema.yaml

    # Validate with file existence checks
    python3 validate-release-plan.py release-plan.yaml --check-files
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import yaml
except ImportError:
    print("Error: pyyaml package is required. Install with: pip install pyyaml")
    sys.exit(1)

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("Error: jsonschema package is required. Install with: pip install jsonschema")
    sys.exit(1)


class MetadataValidator:
    """Validator for CAMARA release metadata files."""

    def __init__(self, metadata_file: Path, schema_file: Optional[Path] = None,
                 check_files: bool = False):
        self.metadata_file = metadata_file
        self.schema_file = schema_file
        self.check_files = check_files
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse YAML file."""
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error in {file_path}: {e}")
            return {}
        except FileNotFoundError:
            self.errors.append(f"File not found: {file_path}")
            return {}

    def detect_schema_type(self, metadata: Dict[str, Any]) -> str:
        """Detect whether this is a release-plan or release-metadata file."""
        if not metadata.get('repository'):
            return 'unknown'

        repo = metadata['repository']
        # release-metadata has release_date and src_commit_sha
        if 'release_date' in repo and 'src_commit_sha' in repo:
            return 'release-metadata'
        # release-plan has release_readiness
        elif 'release_readiness' in repo:
            return 'release-plan'

        return 'unknown'

    def find_schema_file(self, schema_type: str) -> Optional[Path]:
        """Find schema file relative to script location."""
        script_dir = Path(__file__).parent
        schema_dir = script_dir.parent / 'schemas'

        if schema_type == 'release-plan':
            schema_file = schema_dir / 'release-plan-schema.yaml'
        elif schema_type == 'release-metadata':
            schema_file = schema_dir / 'release-metadata-schema.yaml'
        else:
            return None

        if schema_file.exists():
            return schema_file
        return None

    def validate_schema(self, metadata: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate metadata against JSON schema."""
        try:
            validate(instance=metadata, schema=schema)
            return True
        except ValidationError as e:
            self.errors.append(f"Schema validation error: {e.message}")
            if e.path:
                path_str = '.'.join(str(p) for p in e.path)
                self.errors.append(f"  at path: {path_str}")
            return False

    def check_semantic_rules(self, metadata: Dict[str, Any]) -> None:
        """Check semantic rules beyond schema validation."""
        repo = metadata.get('repository', {})
        apis = metadata.get('apis', [])

        # Check release readiness consistency
        release_readiness = repo.get('release_readiness')
        if release_readiness:
            self._check_readiness_consistency(release_readiness, apis)

        # Check API status progression
        for api in apis:
            self._check_api_status(api)

    def _check_readiness_consistency(self, readiness: str, apis: List[Dict]) -> None:
        """Check that API statuses align with repository release readiness."""
        api_statuses = [api.get('api_status') for api in apis]

        if readiness == 'none':
            if any(status not in ['planned'] for status in api_statuses if status):
                self.warnings.append(
                    "release_readiness is 'none' but some APIs have status beyond 'planned'"
                )

        elif readiness == 'pre-release-rc':
            if any(status in ['planned', 'alpha'] for status in api_statuses):
                self.errors.append(
                    "release_readiness is 'pre-release-rc' but some APIs are 'planned' or 'alpha'"
                )

        elif readiness == 'public-release':
            if any(status != 'public' for status in api_statuses if status):
                self.errors.append(
                    "release_readiness is 'public-release' but not all APIs are 'public'"
                )

    def _check_api_status(self, api: Dict) -> None:
        """Check individual API status consistency."""
        status = api.get('api_status')
        version = api.get('target_version') or api.get('version')

        if not status or not version:
            return

        # Check version format consistency with status
        if status == 'public' and version.startswith('0.'):
            self.warnings.append(
                f"API '{api.get('api_name')}' has 'public' status but version {version} starts with 0.x"
            )

    def check_file_existence(self, metadata: Dict[str, Any]) -> None:
        """Check if referenced API files exist (optional check)."""
        if not self.check_files:
            return

        apis = metadata.get('apis', [])
        metadata_dir = self.metadata_file.parent

        for api in apis:
            api_name = api.get('api_name')
            api_status = api.get('api_status')

            # Skip file checks for planned APIs
            if api_status == 'planned':
                continue

            # Look for API definition file
            api_file = metadata_dir / 'code' / 'API_definitions' / f'{api_name}.yaml'
            if not api_file.exists():
                self.warnings.append(
                    f"API definition file not found: {api_file} (status: {api_status})"
                )

    def validate(self) -> bool:
        """Run full validation and return success status."""
        # Load metadata file
        metadata = self.load_yaml(self.metadata_file)
        if self.errors:
            return False

        # Detect schema type
        schema_type = self.detect_schema_type(metadata)
        if schema_type == 'unknown':
            self.errors.append(
                "Cannot determine metadata type (release-plan or release-metadata)"
            )
            return False

        print(f"Detected metadata type: {schema_type}")

        # Find or use provided schema file
        if not self.schema_file:
            self.schema_file = self.find_schema_file(schema_type)
            if not self.schema_file:
                self.errors.append(
                    f"Cannot find schema file for type '{schema_type}'"
                )
                return False

        print(f"Using schema: {self.schema_file}")

        # Load schema
        schema = self.load_yaml(self.schema_file)
        if self.errors:
            return False

        # Validate against schema
        if not self.validate_schema(metadata, schema):
            return False

        # Run semantic checks
        self.check_semantic_rules(metadata)

        # Check file existence if requested
        self.check_file_existence(metadata)

        return len(self.errors) == 0

    def report(self) -> None:
        """Print validation report."""
        if self.errors:
            print("\nValidation FAILED:")
            for error in self.errors:
                print(f"  ERROR: {error}")

        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  WARNING: {warning}")

        if not self.errors and not self.warnings:
            print("\nValidation PASSED: No errors or warnings")
        elif not self.errors:
            print("\nValidation PASSED with warnings")


def main():
    parser = argparse.ArgumentParser(
        description='Validate CAMARA release metadata files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        'metadata_file',
        type=Path,
        help='Path to release-plan.yaml or release-metadata.yaml file'
    )
    parser.add_argument(
        '--schema',
        type=Path,
        help='Path to schema file (auto-detected if not provided)'
    )
    parser.add_argument(
        '--check-files',
        action='store_true',
        help='Check if referenced API definition files exist'
    )

    args = parser.parse_args()

    if not args.metadata_file.exists():
        print(f"Error: Metadata file not found: {args.metadata_file}")
        sys.exit(1)

    validator = MetadataValidator(
        args.metadata_file,
        args.schema,
        args.check_files
    )

    success = validator.validate()
    validator.report()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
