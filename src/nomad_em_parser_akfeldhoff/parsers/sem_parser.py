import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

import numpy as np
from nomad.config import config
from nomad.datamodel.metainfo.plot import PlotlyFigure
from nomad.parsing.parser import MatchingParser
from nomad.units import ureg
from PIL import Image

from nomad_em_parser_akfeldhoff.schema_packages.sem import (
    SEMEntry,
    SEMImage,
    SEMImagePlot,
    SEMInstrument,
    SEMSettings,
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

        mainfile_dir = os.path.dirname(mainfile)
        mainfile_name = os.path.basename(mainfile)
        if not mainfile_name.endswith('.txt'):
            logger.warning(
                'SEMParser: mainfile is not a .txt, skipping', mainfile=mainfile
            )
            return

        # Parse the mainfile text
        metadata = self.read_jeol_txt(mainfile, logger)

        # Populate instrument and settings
        instrument_section = self.build_instrument(metadata)
        if instrument_section is not None:
            sem_entry.instrument = instrument_section
        settings_section = self.build_settings(metadata)
        if settings_section is not None:
            sem_entry.settings = settings_section

        # Attach the matching BMP (same basename)
        bmp_name = mainfile_name.replace('.txt', '.bmp')
        bmp_path = os.path.join(mainfile_dir, bmp_name)
        if os.path.exists(bmp_path):
            image_section = self.build_image_section(
                metadata, bmp_name, bmp_path, archive, mainfile_dir
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

    def build_settings(self, metadata: dict[str, str]) -> SEMSettings | None:
        """
        Build the settings section from metadata (set once per entry).
        """
        has_settings = any(
            key in metadata
            for key in (
                '$$SM_DISPLAY_MODE',
                '$$SM_COLUMN_MODE',
                '$CM_SIGNAL',
                '$CM_ACCEL_VOLT',
                '$CM_MAG',
                '$$SM_WD',
                '$CM_IMAGE_RES',
                '$CM_SCAN_SPEED',
                '$CM_SCAN_AVERAGE',
                '$CM_PROBE_CURRENT',
                '$CM_EMISSION',
                '$SM_GB_GUN_VOLT',
                '$SM_GB_BIAS_VOLT',
                '$SM_COLUM_ECP_ANGLE',
                '$CM_STAGE_POSITION',
            )
        )
        if not has_settings:
            return None

        settings = SEMSettings()
        settings.display_mode = metadata.get('$$SM_DISPLAY_MODE')
        settings.column_mode = metadata.get('$$SM_COLUMN_MODE')
        settings.signal = metadata.get('$CM_SIGNAL')
        settings.sei_detector_mode = self._to_float(
            metadata.get('$$SM_SEI_DETECTOR_MODE')
        )
        settings.sei_detector_level = self._to_float(
            metadata.get('$$SM_SEI_DETECTOR_LEVEL')
        )
        settings.acceleration_voltage = self._to_float(metadata.get('$CM_ACCEL_VOLT'))
        settings.magnification = self._to_float(metadata.get('$CM_MAG'))
        if '$$SM_WD' in metadata:
            settings.working_distance = self._to_float(metadata.get('$$SM_WD'))
        elif '$SM_WD' in metadata:
            settings.working_distance = self._to_float(metadata.get('$SM_WD'))
        settings.image_resolution = metadata.get('$CM_IMAGE_RES')
        settings.scan_angle = metadata.get('$CM_SCAN_ANGLE')
        settings.scan_speed = self._to_float(metadata.get('$CM_SCAN_SPEED'))
        settings.scan_average = self._to_float(metadata.get('$CM_SCAN_AVERAGE'))
        settings.probe_current = metadata.get('$CM_PROBE_CURRENT')
        settings.emission = self._to_float(metadata.get('$CM_EMISSION'))
        settings.gun_voltage = self._to_float(metadata.get('$SM_GB_GUN_VOLT'))
        settings.bias_voltage = self._to_float(metadata.get('$SM_GB_BIAS_VOLT'))
        settings.column_ecp_angle = self._to_float(metadata.get('$SM_COLUM_ECP_ANGLE'))

        stage_position_raw = metadata.get('$CM_STAGE_POSITION')
        if stage_position_raw:
            stage = self._parse_stage_position(stage_position_raw)
            if stage is not None:
                settings.stage_position = stage

        return settings

    def build_image_section(
        self,
        metadata: dict[str, str],
        bmp_name: str,
        bmp_path: str,
        archive,
        base_dir: str,
    ) -> SEMImage:
        """
        Map metadata to the SEMImage schema, including raw key/value pairs.
        """
        image_section = SEMImage()
        image_section.image = (
            self._raw_file_reference(bmp_path, archive, base_dir) or bmp_name
        )

        width = None
        if os.path.exists(bmp_path):
            try:
                with Image.open(bmp_path) as img:
                    width, _ = img.size
            except Exception:
                pass

        image_section.format = metadata.get('$CM_FORMAT')
        image_section.version = metadata.get('$CM_VERSION')
        image_section.comment = metadata.get('$CM_COMMENT')
        image_section.title = metadata.get('$CM_TITLE')
        image_section.date = metadata.get('$CM_DATE')
        image_section.time = metadata.get('$CM_TIME')
        image_section.image_id = metadata.get('$CM_IMAGEID', '').lstrip(': ').strip()

        image_section.film_number = self._to_float(metadata.get('$$SM_FILM_NUMBER'))
        image_section.micron_bar = self._to_float(metadata.get('$$SM_MICRON_BAR'))
        image_section.micron_marker = metadata.get('$$SM_MICRON_MARKER')
        image_section.font_size = metadata.get('$$SM_FONT_SIZE')

        if image_section.micron_bar and width:
            # micron_bar is in microns, convert to meters
            fov_width = image_section.micron_bar * ureg.um
            image_section.pixel_size = fov_width / width

        pixel_size_val = (
            image_section.pixel_size.magnitude if image_section.pixel_size else None
        )

        plot_section = self._build_image_plot(bmp_path, pixel_size_val)
        if plot_section is not None:
            image_section.plot = plot_section

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
            axis, raw_value = (p.strip() for p in part.split('=', 1))
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
    def _raw_file_reference(file_path: str, archive, base_dir: str) -> str | None:
        """
        Return a path relative to the upload root if available so the GUI can render the file.
        """
        raw_path = getattr(getattr(archive, 'm_context', None), 'raw_path', None)
        if raw_path:
            try:
                return os.path.relpath(file_path, raw_path)
            except Exception:
                pass
        try:
            return os.path.relpath(file_path, base_dir)
        except Exception:
            return os.path.basename(file_path)

    @staticmethod
    def _build_image_plot(
        file_path: str, pixel_size: float | None = None
    ) -> SEMImagePlot | None:
        """
        Build a Plotly image figure from the BMP so the GUI can render it without relying
        solely on RawFileAdaptor.
        """
        try:
            with Image.open(file_path) as img:
                rgb = img.convert('RGB')
                z = np.asarray(rgb).tolist()  # nested lists of pixel values

            fig_section = SEMImagePlot()
            plotly_fig = PlotlyFigure()
            plotly_fig.label = 'SEM image'

            # Default: Pixel coordinates
            dx = 1
            dy = 1
            unit_label = 'pixels'

            # If we have a scale, switch to Microns
            if pixel_size:
                dx = pixel_size * 1e6
                dy = pixel_size * 1e6
                unit_label = 'µm'

            plotly_fig.figure = {
                'data': [{'type': 'image', 'z': z, 'dx': dx, 'dy': dy}],
                'layout': {
                    # Turn AXES ON so we can see the scale bar (ruler)
                    'xaxis': {
                        'visible': True,
                        'title': {'text': unit_label},
                        'ticks': 'outside',
                    },
                    'yaxis': {
                        'visible': True,
                        'title': {'text': unit_label},
                        'ticks': 'outside',
                        'scaleanchor': 'x',
                    },
                    'margin': {
                        'l': 50,
                        'r': 0,
                        't': 0,
                        'b': 50,
                    },  # Add margin for axis labels
                    'height': rgb.height,
                    'width': rgb.width,
                },
            }
            fig_section.figures = [plotly_fig]
            return fig_section
        except Exception as exc:  # pragma: no cover - debug fallback
            print(f'Failed to build image plot for {file_path}: {exc}')
            return None
