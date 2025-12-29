import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad.config import config
from nomad.parsing.parser import MatchingParser
from nomad.units import ureg

from nomad_em_parser_akfeldhoff.schema_packages.sem import (
    KeyValueMetadata,
    SEMEntry,
    SEMImage,
    SEMInstrument,
    SEMStagePosition,
)

configuration = config.get_plugin_entry_point(
    'nomad_em_parser_akfeldhoff.parsers:parser_entry_point'
)


class SEMParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        logger.info('SEMParser.parse')

        # 1. Create the main Entry structure
        sem_entry = SEMEntry()
        sem_entry.images = []

        # 2. Get the directory of the uploaded file
        mainfile_dir = os.path.dirname(mainfile)
        # Sort files to ensure deterministic order
        files = sorted(os.listdir(mainfile_dir))

        # 3. Loop through all files to find .txt metadata files with JEOL SEM signature
        for filename in files:
            if filename.endswith('.txt'):
                txt_path = os.path.join(mainfile_dir, filename)

                # Check if a matching .bmp exists (same name, different extension)
                bmp_name = filename.replace('.txt', '.bmp')
                if bmp_name not in files:
                    continue  # Skip orphan txt files

                # 4. Parse the text file (Pass the logger here!)
                metadata = self.read_jeol_txt(txt_path, logger)

                # Populate instrument info once
                if sem_entry.instrument is None:
                    instrument_section = self.build_instrument(metadata)
                    if instrument_section is not None:
                        sem_entry.instrument = instrument_section

                # 5. Populate the SEMImage schema
                bmp_path = os.path.join(mainfile_dir, bmp_name)
                image_section = self.build_image_section(
                    metadata, bmp_name, bmp_path, archive
                )
                sem_entry.images.append(image_section)

        # 6. Store the populated entry into the archive
        archive.data = sem_entry
        # Populate overview-related metadata immediately (normalizer would do this in production)
        if hasattr(sem_entry, 'normalize'):
            sem_entry.normalize(archive, logger)

    def read_jeol_txt(self, filepath, logger=None):
        """
        Reads the JEOL SEM txt file.
        """
        data = {}
        try:
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line_content = line.strip()
                    if not line_content:
                        continue
                    # Split by first space
                    parts = line_content.split(' ', 1)
                    if len(parts) == 2:  # noqa: PLR2004
                        key = parts[0].strip()
                        value = parts[1].strip()
                        data[key] = value
                    elif len(parts) == 1 and line_content.startswith('$'):
                        # Capture keys that have an empty value (e.g., $CM_COMMENT)
                        key = parts[0].strip()
                        data[key] = ''
        except Exception as e:
            if logger:
                logger.error(f'Error reading {filepath}: {e}')
            else:
                print(f'Error reading {filepath}: {e}')
        return data

    def build_instrument(self, metadata: dict[str, str]) -> SEMInstrument | None:
        """
        Build the instrument section from metadata (set once per entry).
        """
        has_data = any(
            key in metadata
            for key in ('$CM_INSTRUMENT', '$CM_INSTRUMENT_TYPE', '$CM_COMPANY')
        )
        if not has_data:
            return None

        instrument_section = SEMInstrument()
        instrument_section.name = metadata.get('$CM_INSTRUMENT')
        instrument_section.instrument_type = metadata.get('$CM_INSTRUMENT_TYPE')
        instrument_section.company = metadata.get('$CM_COMPANY')
        instrument_section.operator = metadata.get('$CM_OPERATOR')
        return instrument_section

    def build_image_section(
        self, metadata: dict[str, str], bmp_name: str, bmp_path: str, archive
    ) -> SEMImage:
        """
        Map metadata to the SEMImage schema, including raw key/value pairs.
        """
        image_section = SEMImage()
        image_section.image = self._raw_file_reference(bmp_path, archive) or bmp_name

        image_section.format = metadata.get('$CM_FORMAT')
        image_section.version = metadata.get('$CM_VERSION')
        image_section.comment = metadata.get('$CM_COMMENT')
        image_section.title = metadata.get('$CM_TITLE')
        image_section.date = metadata.get('$CM_DATE')
        image_section.time = metadata.get('$CM_TIME')
        image_section.operator = metadata.get('$CM_OPERATOR')
        image_section.company = metadata.get('$CM_COMPANY')
        image_section.image_id = metadata.get('$CM_IMAGEID', '').lstrip(': ').strip()
        image_section.instrument_type = metadata.get('$CM_INSTRUMENT_TYPE')
        image_section.instrument_name = metadata.get('$CM_INSTRUMENT')

        # Key numeric parameters
        image_section.signal = metadata.get('$CM_SIGNAL')
        image_section.film_number = self._to_float(metadata.get('$$SM_FILM_NUMBER'))

        image_section.acceleration_voltage = self._to_quantity(
            metadata.get('$CM_ACCEL_VOLT'), ureg.kV
        )
        image_section.magnification = self._to_float(metadata.get('$CM_MAG'))

        if '$$SM_WD' in metadata:
            image_section.working_distance = self._to_quantity(
                metadata.get('$$SM_WD'), ureg.mm
            )
        elif '$SM_WD' in metadata:
            image_section.working_distance = self._to_quantity(
                metadata.get('$SM_WD'), ureg.mm
            )

        image_section.micron_bar = self._to_float(metadata.get('$$SM_MICRON_BAR'))
        image_section.micron_marker = metadata.get('$$SM_MICRON_MARKER')
        image_section.font_size = metadata.get('$$SM_FONT_SIZE')
        image_section.display_mode = metadata.get('$$SM_DISPLAY_MODE')
        image_section.column_mode = metadata.get('$$SM_COLUMN_MODE')
        image_section.sei_detector_mode = self._to_float(
            metadata.get('$$SM_SEI_DETECTOR_MODE')
        )
        image_section.sei_detector_level = self._to_float(
            metadata.get('$$SM_SEI_DETECTOR_LEVEL')
        )

        image_section.gun_voltage = self._to_float(metadata.get('$SM_GB_GUN_VOLT'))
        image_section.bias_voltage = self._to_float(metadata.get('$SM_GB_BIAS_VOLT'))
        image_section.column_ecp_angle = self._to_float(
            metadata.get('$SM_COLUM_ECP_ANGLE')
        )

        image_section.image_resolution = metadata.get('$CM_IMAGE_RES')
        image_section.scan_angle = metadata.get('$CM_SCAN_ANGLE')
        image_section.scan_speed = self._to_float(metadata.get('$CM_SCAN_SPEED'))
        image_section.scan_average = self._to_float(metadata.get('$CM_SCAN_AVERAGE'))
        image_section.probe_current = metadata.get('$CM_PROBE_CURRENT')
        image_section.emission = self._to_float(metadata.get('$CM_EMISSION'))

        stage_position_raw = metadata.get('$CM_STAGE_POSITION')
        if stage_position_raw:
            stage = self._parse_stage_position(stage_position_raw)
            if stage is not None:
                image_section.stage_position = stage

        # Persist all raw metadata pairs
        image_section.metadata = []
        for key, value in metadata.items():
            kv = KeyValueMetadata()
            kv.key = key
            kv.value = value
            image_section.metadata.append(kv)

        return image_section

    @staticmethod
    def _to_float(value: str | None) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except Exception:
            return None

    @staticmethod
    def _to_quantity(value: str | None, unit):
        numeric_value = SEMParser._to_float(value)
        if numeric_value is None:
            return None
        return numeric_value * unit

    @staticmethod
    def _parse_stage_position(position: str) -> SEMStagePosition | None:
        """
        Parse a JEOL stage position string like 'X=37.1761, Y=44.9344, R=354.9968, Z=16.90, T=0.00'.
        """
        parts = [p.strip() for p in position.split(',') if '=' in p]
        if not parts:
            return None

        stage_section = SEMStagePosition()
        found = False
        for part in parts:
            axis, raw_value = [p.strip() for p in part.split('=', 1)]
            value = SEMParser._to_float(raw_value)
            if value is None:
                continue
            match axis.upper():
                case 'X':
                    stage_section.x = value
                case 'Y':
                    stage_section.y = value
                case 'R':
                    stage_section.r = value
                case 'Z':
                    stage_section.z = value
                case 'T':
                    stage_section.t = value
                case _:
                    continue
            found = True

        return stage_section if found else None

    @staticmethod
    def _raw_file_reference(file_path: str, archive) -> str | None:
        """
        Return a path relative to the upload root if available so the GUI can render the file.
        """
        raw_path = getattr(getattr(archive, 'm_context', None), 'raw_path', None)
        if raw_path:
            try:
                return os.path.relpath(file_path, raw_path)
            except Exception:
                pass
        return os.path.basename(file_path)
