# Project Context: nomad-em-parser-akfeldhoff

## Overview
This project is a NOMAD parser plugin for JEOL SEM data, designed to work within the NOMAD distribution (distro-dev) environment. It is structured as a Python package and submodule, and is intended to parse SEM metadata and image associations from JEOL instrument exports (typically .txt and .bmp files).

## Key Features
- **Parser for JEOL SEM data**: Detects and parses .txt metadata files with JEOL SEM format, and associates them with corresponding .bmp image files.
- **Batch Processing**: Scans the entire upload directory for all valid txt+bmp pairs, not just the mainfile.
- **Metadata Extraction**: Extracts key fields such as acceleration voltage, magnification, working distance, and acquisition date from the .txt file.
- **Schema Structure**: Stores results in a top-level `SEMEntry` with a list of `SEMImage` sections, each containing metadata and the image filename.
- **NOMAD Plugin Integration**: Registered as a parser entry point for the NOMAD platform, using the `ParserEntryPoint` interface.

## File Structure
- `src/nomad_em_parser_akfeldhoff/parsers/sem_parser.py`: Main SEM parser logic (class `SEMParser`).
- `src/nomad_em_parser_akfeldhoff/parsers/__init__.py`: Parser entry point registration.
- `src/nomad_em_parser_akfeldhoff/schema_packages/sem.py`: Defines `SEMEntry` and `SEMImage` schema classes.
- `tests/parsers/test_parser.py`: Unit test for the parser.
- `tests/data/`: Example .txt and .bmp files for testing.
- `pyproject.toml`: Package configuration (renamed to `nomad-em-parser-akfeldhoff`).

## Parser Logic
- **Mainfile Matching**: Triggers on any `.txt` file, but only processes those with JEOL SEM signature (`$CM_FORMAT Bitmap` and `$CM_VERSION` in the first lines).
- **Directory Scan**: For each valid .txt file, checks for a matching .bmp file (same basename).
- **Metadata Parsing**: Reads key-value pairs from the .txt file, mapping specific keys to schema fields.
- **Data Storage**: Populates `archive.data.images[]` with `SEMImage` objects, each referencing the image filename and extracted metadata.

## Example Metadata Keys Parsed
- `$CM_ACCEL_VOLT` → acceleration_voltage (kV)
- `$CM_MAG` → magnification
- `$$SM_WD` or `$SM_WD` → working_distance (mm)
- `$CM_DATE` → date

## Test Example
- `tests/parsers/test_parser.py` runs the parser on a sample .txt file and checks that the correct metadata and image filename are extracted.

## Development Notes
- The parser is currently limited to a small set of metadata fields, but the .txt format contains many more that could be mapped in the future.
- Only .txt files with the correct JEOL SEM signature are processed, reducing false positives.
- The package was renamed from `nomad-em` to `nomad-em-parser-akfeldhoff` and is developed on a `test-refine` branch.

## Integration
- The package is referenced in the main distro's `pyproject.toml` as a workspace member and dependency.
- The parser is registered as a NOMAD plugin entry point for automatic discovery.

---

This file summarizes the technical and organizational context of the `nomad-em-parser-akfeldhoff` project as of December 2025.
