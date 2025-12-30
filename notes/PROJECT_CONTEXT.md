# Project Context: nomad-em-parser-akfeldhoff

## Overview
This project is a NOMAD parser plugin for JEOL SEM data, designed to work within the NOMAD distribution (distro-dev) environment. It is structured as a Python package and submodule, and is intended to parse SEM metadata and image associations from JEOL instrument exports (typically .txt and .bmp files). The parser and schema capture all metadata in the JEOL txt (instrument, settings, stage position) and expose overview metadata, a RawFileAdaptor image link, and a Plotly-rendered image preview in the GUI.

## Key Features
- **Parser for JEOL SEM data**: Detects and parses .txt metadata files with JEOL SEM format, and associates them with corresponding .bmp image files.
- **Batch Processing**: Scans the entire upload directory for all valid txt+bmp pairs, not just the mainfile.
- **Metadata Extraction**: Extracts the full set of key-value metadata from the JEOL txt, including voltages, magnification, working distance, signal, scan settings, detector settings, stage position, etc. Empty values are preserved for mapped fields.
- **Schema Structure**: Stores results in a top-level `SEMEntry` with instrument info, instrument settings (incl. stage position), a list of `SEMImage` sections (image/display metadata), and the BMP image reference (RawFileAdaptor) plus a Plotly image preview. Fields are kept editable in the ELN for inspection.
- **Overview Metadata**: `SEMEntry.normalize` populates `results.eln` (sections, methods, instruments, names, descriptions) so key sample and instrument info appears on the overview page. Images are marked for overview display. The current UI ignores `a_eln.order`, so overview-enabled sections show all quantities.
- **NOMAD Plugin Integration**: Registered as a parser entry point for the NOMAD platform, using the `ParserEntryPoint` interface.

## File Structure
- `src/nomad_em_parser_akfeldhoff/parsers/sem_parser.py`: Main SEM parser logic (class `SEMParser`).
- `src/nomad_em_parser_akfeldhoff/parsers/__init__.py`: Parser entry point registration.
- `src/nomad_em_parser_akfeldhoff/schema_packages/sem.py`: Defines `SEMEntry`, `SEMImage`, `SEMInstrument`, `SEMSettings`, `SEMStagePosition`, and `SEMImagePlot` schema classes.
- `tests/parsers/test_parser.py`: Unit test for the parser.
- `tests/data/`: Example .txt and .bmp files for testing.
- `pyproject.toml`: Package configuration (renamed to `nomad-em-parser-akfeldhoff`).

## Parser Logic
- **Mainfile Matching**: Triggers on any `.txt` file, but only processes those with JEOL SEM signature (`$CM_FORMAT Bitmap` and `$CM_VERSION` in the first lines).
- **Entry Scope**: Each `.txt` mainfile is parsed as a single entry; it links only its matching `.bmp` (same basename).
- **Metadata Parsing**: Reads all key-value pairs from the .txt file, mapping specific keys to typed schema fields (no raw key/value duplicates stored).
- **Data Storage**: Populates `archive.data.instrument` and `archive.data.settings` (including accel. voltage, magnification, working distance), plus `archive.data.images[]` with `SEMImage` objects (RawFileAdaptor image reference and Plotly preview).
- **Overview Population**: Parser calls `SEMEntry.normalize` to fill `results.eln` (sections, methods, instruments, names, descriptions); ELN uses modern `a_eln` annotations (no deprecated SectionProperties). The front end currently ignores `order`, so hiding items requires moving them to a non-overview subsection.

## Example Metadata Keys Parsed
- `$CM_ACCEL_VOLT` → acceleration_voltage (kV, stored in settings)
- `$CM_MAG` → magnification (settings)
- `$$SM_WD` or `$SM_WD` → working_distance (mm, settings)
- `$CM_DATE`, `$CM_TIME`
- `$CM_FORMAT`, `$CM_VERSION`, `$CM_SIGNAL`, `$CM_IMAGE_RES`, `$CM_SCAN_SPEED`, `$CM_SCAN_AVERAGE`, `$CM_PROBE_CURRENT`, `$CM_EMISSION`, `$CM_STAGE_POSITION`, `$SM_*`, `$$SM_*` detector/display settings
- `$CM_INSTRUMENT`, `$CM_INSTRUMENT_TYPE`, `$CM_OPERATOR`, `$CM_COMPANY` → instrument section

## Test Example
- `tests/parsers/test_parser.py` runs the parser on a sample .txt file and checks that all metadata, instrument info, overview fields, stage position, and image reference are extracted correctly.

## Development Notes
- Parser now maps the full txt key set present in the sample file; additional keys can be added similarly if encountered.
- Only .txt files with the correct JEOL SEM signature are processed, reducing false positives.
- Plotly image preview (`SEMImagePlot`) is populated from the BMP so the GUI shows the image without relying solely on RawFileAdaptor.
- The `order` flag was left only for intent; the current UI ignores it. Section-level `overview=True` is what governs visibility.
- The package was renamed from `nomad-em` to `nomad-em-parser-akfeldhoff` and is developed on a `test-refine` branch.

## Integration
- The package is referenced in the main distro's `pyproject.toml` as a workspace member and dependency.
- The parser is registered as a NOMAD plugin entry point for automatic discovery.

---

This file summarizes the technical and organizational context of the `nomad-em-parser-akfeldhoff` project as of January 2026.
