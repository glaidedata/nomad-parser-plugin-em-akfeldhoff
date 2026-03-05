import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

import numpy as np
from nomad.config import config
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    SectionProperties,
)
from nomad.datamodel.metainfo.basesections import Measurement, ReadableIdentifiers
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.datamodel.results import ELN, Results
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection
from nomad.units import ureg
from PIL import Image

configuration = config.get_plugin_entry_point(
    'nomad_em_parser_akfeldhoff.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()


class SEMInstrument(ArchiveSection):
    """
    Instrument information for the SEM.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            overview=True,
            lane_width='400px',
        )
    )

    name = Quantity(
        type=str,
        description='Instrument model name (e.g., JSM 6700F NT)',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            overview=True,
        ),
    )
    instrument_type = Quantity(
        type=str,
        description='Instrument type identifier.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            overview=True,
        ),
    )
    company = Quantity(
        type=str,
        description='Operating company or institution.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )
    operator = Quantity(
        type=str,
        description='Instrument operator recorded by SEM.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )


class SEMStagePosition(ArchiveSection):
    """
    Stage coordinates captured during acquisition.
    """

    x = Quantity(
        type=float,
        unit='mm',
        description='Stage X position.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    y = Quantity(
        type=float,
        unit='mm',
        description='Stage Y position.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    r = Quantity(
        type=float,
        unit='deg',
        description='Stage rotation.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    z = Quantity(
        type=float,
        unit='mm',
        description='Stage Z position.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    t = Quantity(
        type=float,
        unit='deg',
        description='Stage tilt.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )


class SEMSettings(ArchiveSection):
    """
    Instrument settings captured during acquisition (per entry).
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            overview=True,
            lane_width='400px',
        )
    )

    display_mode = Quantity(
        type=str,
        description='Display mode ($$SM_DISPLAY_MODE).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            overview=True,
        ),
    )
    column_mode = Quantity(
        type=str,
        description='Column mode ($$SM_COLUMN_MODE).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            overview=True,
        ),
    )
    signal = Quantity(
        type=str,
        description='Signal mode ($CM_SIGNAL).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            overview=True,
        ),
    )
    acceleration_voltage = Quantity(
        type=float,
        unit='kV',
        description='Acceleration Voltage ($CM_ACCEL_VOLT)',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=True
        ),
    )
    magnification = Quantity(
        type=float,
        description='Magnification ($CM_MAG)',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=True
        ),
    )
    working_distance = Quantity(
        type=float,
        unit='mm',
        description='Working Distance ($$SM_WD)',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=True
        ),
    )
    image_resolution = Quantity(
        type=str,
        description='Image resolution ($CM_IMAGE_RES).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            overview=True,
        ),
    )
    sei_detector_mode = Quantity(
        type=float,
        description='SEI detector mode ($$SM_SEI_DETECTOR_MODE).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=False
        ),
    )
    sei_detector_level = Quantity(
        type=float,
        description='SEI detector level ($$SM_SEI_DETECTOR_LEVEL).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=False
        ),
    )
    scan_angle = Quantity(
        type=str,
        description='Scan angle ($CM_SCAN_ANGLE).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity, overview=False
        ),
    )
    scan_speed = Quantity(
        type=float,
        description='Scan speed ($CM_SCAN_SPEED).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=False
        ),
    )
    scan_average = Quantity(
        type=float,
        description='Scan average ($CM_SCAN_AVERAGE).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=False
        ),
    )
    probe_current = Quantity(
        type=str,
        description='Probe current configuration ($CM_PROBE_CURRENT).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity, overview=False
        ),
    )
    emission = Quantity(
        type=float,
        description='Emission current ($CM_EMISSION).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=False
        ),
    )
    gun_voltage = Quantity(
        type=float,
        description='Gun voltage ($SM_GB_GUN_VOLT).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=False
        ),
    )
    bias_voltage = Quantity(
        type=float,
        description='Bias voltage ($SM_GB_BIAS_VOLT).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=False
        ),
    )
    column_ecp_angle = Quantity(
        type=float,
        description='Column ECP angle ($SM_COLUM_ECP_ANGLE).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, overview=False
        ),
    )
    stage_position = SubSection(
        section_def=SEMStagePosition,
        description='Stage position during acquisition.',
        a_eln=ELNAnnotation(overview=False),
    )


class SEMImagePlot(PlotSection):
    """
    Plot wrapper to render the SEM image via Plotly (data URI).
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            overview=True,
            lane_width='400px',
        )
    )


class SEMAcquisition(ArchiveSection):
    """
    Section representing a single SEM image and its extracted metadata.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            overview=True,
            lane_width='400px',
        )
    )

    title = Quantity(
        type=str,
        description='Title ($CM_TITLE).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity, overview=True
        ),
    )
    image = Quantity(
        type=str,
        description='The image file (.bmp) associated with this metadata.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.FileEditQuantity,
            label='SEM Image',
            overview=True,
        ),
        a_browser=dict(
            adaptor='RawFileAdaptor',
            label='SEM image',
            mime_types=['image/bmp', 'image/png', 'image/jpeg'],
        ),
    )
    image_id = Quantity(
        type=str,
        description='Image identifier ($CM_IMAGEID).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity, overview=True
        ),
    )
    date = Quantity(
        type=str,
        description='Date of acquisition ($CM_DATE)',
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )
    time = Quantity(
        type=str,
        description='Acquisition time ($CM_TIME).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity, overview=True
        ),
    )
    comment = Quantity(
        type=str,
        description='Comment ($CM_COMMENT).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity, overview=True
        ),
    )
    format = Quantity(type=str, description='Image format identifier ($CM_FORMAT).')
    version = Quantity(type=str, description='Format version ($CM_VERSION).')
    film_number = Quantity(type=float, description='Film number ($$SM_FILM_NUMBER).')
    micron_bar = Quantity(type=float, description='Micron bar size ($$SM_MICRON_BAR).')
    micron_marker = Quantity(
        type=str, description='Micron marker label ($$SM_MICRON_MARKER).'
    )
    font_size = Quantity(type=str, description='Font size settings ($$SM_FONT_SIZE).')
    pixel_size = Quantity(
        type=float,
        unit='m',
        description='Physical size of one pixel. Necessary for drawing scale bars.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    plot = SubSection(
        section_def=SEMImagePlot,
        description='Image preview plot.',
        a_eln=ELNAnnotation(overview=True),
    )


    settings = SubSection(
        section_def=SEMSettings,
        description='Instrument settings captured during this specific acquisition.',
        a_eln=ELNAnnotation(overview=True),
    )


class SEMExperiment(Measurement):
    """
    Base class for an SEM experiment containing multiple images.
    Can be used standalone or through the ELN interface.
    """

    m_def = Section()

    name = Quantity(
        type=str,
        description='Display name for this SEM entry.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity, overview=True
        ),
    )
    lab_id = Quantity(
        type=str,
        description='Lab/sample identifier.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity, overview=True
        ),
    )
    description = Quantity(
        type=str,
        description='Description of this SEM collection.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.RichTextEditQuantity,
            props={'height': 200},
        ),
    )

    acquisitions = SubSection(
        section_def=SEMAcquisition,
        repeats=True,
        label='Acquisitions',
        a_eln=ELNAnnotation(overview=True),
    )

    instrument_metadata = SubSection(
        section_def=SEMInstrument,
        description='Instrument metadata captured from the JEOL txt.',
        a_eln=ELNAnnotation(overview=True),
    )

    def normalize(self, archive, logger):  # noqa: PLR0912, PLR0915
        super().normalize(archive, logger)

        # Ensure results.eln exists so the GUI overview can surface sample/instrument info
        if archive.results is None:
            archive.results = Results()
        if archive.results.eln is None:
            archive.results.eln = ELN()

        eln = archive.results.eln
        eln.sections = eln.sections or []
        if self.m_def.name not in eln.sections:
            eln.sections.append(self.m_def.name)

        eln.methods = eln.methods or []
        if 'SEM' not in eln.methods:
            eln.methods.append('SEM')

        if self.instrument_metadata and self.instrument_metadata.name:
            eln.instruments = eln.instruments or []
            if self.instrument_metadata.name not in eln.instruments:
                eln.instruments.append(self.instrument_metadata.name)

        primary_acquisition = self.acquisitions[0] if self.acquisitions else None
        candidate_name = None
        for candidate in (
            getattr(self, 'name', None),
            getattr(self, 'lab_id', None),
            getattr(primary_acquisition, 'title', None),
            getattr(primary_acquisition, 'image', None),
        ):
            if candidate:
                candidate_name = candidate
                break

        if candidate_name:
            if not self.name:
                stripped = (
                    candidate_name.rsplit('.', 1)[0]
                    if candidate_name.lower().endswith(
                        ('.bmp', '.png', '.jpg', '.jpeg')
                    )
                    else candidate_name
                )
                self.name = stripped
            eln.names = eln.names or []
            if candidate_name not in eln.names:
                eln.names.append(candidate_name)
            if (
                getattr(archive, 'metadata', None) is not None
                and getattr(archive.metadata, 'entry_name', None) is None
            ):
                archive.metadata.entry_name = candidate_name

        summary_bits = []
        if primary_acquisition:
            # Extract summary data from the nested settings of the first acquisition
            settings = primary_acquisition.settings
            mag = settings.magnification if settings and settings.magnification is not None else None
            accel = settings.acceleration_voltage if settings and settings.acceleration_voltage is not None else None
            wd = settings.working_distance if settings and settings.working_distance is not None else None

            if mag is not None:
                summary_bits.append(f'{mag:g}x')
            if accel is not None:
                summary_bits.append(f'{accel:g} kV')
            if wd is not None:
                summary_bits.append(f'WD {wd:g} mm')
            if primary_acquisition.date:
                summary_bits.append(f'date {primary_acquisition.date}')

        if self.instrument_metadata and self.instrument_metadata.operator:
            summary_bits.append(f'operator {self.instrument_metadata.operator}')

        if summary_bits:
            summary = ', '.join(summary_bits)
            eln.descriptions = eln.descriptions or []
            if summary not in eln.descriptions:
                eln.descriptions.append(summary)

        # Set lab_id from image_id if missing
        if not self.lab_id and primary_acquisition and primary_acquisition.image_id:
            self.lab_id = primary_acquisition.image_id


class ELNSEMExperiment(SEMExperiment, EntryData, PlotSection):
    """
    ELN-compatible SEM experiment entry that can be edited in the GUI.
    """

    m_def = Section(
        label='SEM Experiment (JEOL)',
        a_eln=ELNAnnotation(
            overview=True,
            lane_width='800px',
            properties=SectionProperties(
                order=[
                    'name',
                    'datetime',
                    'lab_id',
                    'location',
                    'description',
                ]
            ),
        ),
        a_template={
            'measurement_identifiers': {},
        },
    )

    measurement_identifiers = SubSection(
        section_def=ReadableIdentifiers,
    )

    @staticmethod
    def _read_jeol_txt(filepath, logger=None):
        data = {}
        try:
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line_content = line.strip()
                    if not line_content:
                        continue
                    parts = line_content.split(' ', 1)
                    if len(parts) == 2:  # noqa: PLR2004
                        key = parts[0].strip()
                        value = parts[1].strip()
                        data[key] = value
                    elif len(parts) == 1 and line_content.startswith('$'):
                        key = parts[0].strip()
                        data[key] = ''
        except Exception as exc:
            if logger:
                logger.error(f'Error reading {filepath}: {exc}')
            else:
                print(f'Error reading {filepath}: {exc}')
        return data

    @staticmethod
    def _to_float(value: str | None) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except Exception:
            return None

    @staticmethod
    def _parse_stage_position(position: str) -> SEMStagePosition | None:
        parts = [p.strip() for p in position.split(',') if '=' in p]
        if not parts:
            return None

        stage_section = SEMStagePosition()
        found = False
        for part in parts:
            axis, raw_value = (p.strip() for p in part.split('=', 1))
            value = ELNSEMExperiment._to_float(raw_value)
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
    def _build_instrument(metadata: dict[str, str]) -> SEMInstrument | None:
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

    @staticmethod
    def _build_settings(metadata: dict[str, str]) -> SEMSettings | None:
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
        settings.sei_detector_mode = ELNSEMExperiment._to_float(
            metadata.get('$$SM_SEI_DETECTOR_MODE')
        )
        settings.sei_detector_level = ELNSEMExperiment._to_float(
            metadata.get('$$SM_SEI_DETECTOR_LEVEL')
        )
        settings.acceleration_voltage = ELNSEMExperiment._to_float(
            metadata.get('$CM_ACCEL_VOLT')
        )
        settings.magnification = ELNSEMExperiment._to_float(metadata.get('$CM_MAG'))
        if '$$SM_WD' in metadata:
            settings.working_distance = ELNSEMExperiment._to_float(
                metadata.get('$$SM_WD')
            )
        elif '$SM_WD' in metadata:
            settings.working_distance = ELNSEMExperiment._to_float(
                metadata.get('$SM_WD')
            )
        settings.image_resolution = metadata.get('$CM_IMAGE_RES')
        settings.scan_angle = metadata.get('$CM_SCAN_ANGLE')
        settings.scan_speed = ELNSEMExperiment._to_float(metadata.get('$CM_SCAN_SPEED'))
        settings.scan_average = ELNSEMExperiment._to_float(
            metadata.get('$CM_SCAN_AVERAGE')
        )
        settings.probe_current = metadata.get('$CM_PROBE_CURRENT')
        settings.emission = ELNSEMExperiment._to_float(metadata.get('$CM_EMISSION'))
        settings.gun_voltage = ELNSEMExperiment._to_float(
            metadata.get('$SM_GB_GUN_VOLT')
        )
        settings.bias_voltage = ELNSEMExperiment._to_float(
            metadata.get('$SM_GB_BIAS_VOLT')
        )
        settings.column_ecp_angle = ELNSEMExperiment._to_float(
            metadata.get('$SM_COLUM_ECP_ANGLE')
        )

        stage_position_raw = metadata.get('$CM_STAGE_POSITION')
        if stage_position_raw:
            stage = ELNSEMExperiment._parse_stage_position(stage_position_raw)
            if stage is not None:
                settings.stage_position = stage

        return settings

    @staticmethod
    def _raw_file_reference(file_path: str, archive, base_dir: str) -> str | None:
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
        try:
            with Image.open(file_path) as img:
                rgb = img.convert('RGB')
                z = np.asarray(rgb).tolist()

            fig_section = SEMImagePlot()
            plotly_fig = PlotlyFigure()
            plotly_fig.label = 'SEM image'

            dx = 1
            dy = 1
            unit_label = 'pixels'
            if pixel_size:
                dx = pixel_size * 1e6
                dy = pixel_size * 1e6
                unit_label = 'um'

            plotly_fig.figure = {
                'data': [{'type': 'image', 'z': z, 'dx': dx, 'dy': dy}],
                'layout': {
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
                    'margin': {'l': 50, 'r': 0, 't': 0, 'b': 50},
                    'height': rgb.height,
                    'width': rgb.width,
                },
            }
            fig_section.figures = [plotly_fig]
            return fig_section
        except Exception:
            return None

    @staticmethod
    def _build_acquisition_section(
        metadata: dict[str, str],
        bmp_name: str,
        bmp_path: str,
        archive,
        base_dir: str,
    ) -> SEMAcquisition:
        acquisition = SEMAcquisition()
        acquisition.image = (
            ELNSEMExperiment._raw_file_reference(bmp_path, archive, base_dir)
            or bmp_name
        )

        width = None
        if os.path.exists(bmp_path):
            try:
                with Image.open(bmp_path) as img:
                    width, _ = img.size
            except Exception:
                pass

        acquisition.format = metadata.get('$CM_FORMAT')
        acquisition.version = metadata.get('$CM_VERSION')
        acquisition.comment = metadata.get('$CM_COMMENT')
        acquisition.title = metadata.get('$CM_TITLE')
        acquisition.date = metadata.get('$CM_DATE')
        acquisition.time = metadata.get('$CM_TIME')
        acquisition.image_id = metadata.get('$CM_IMAGEID', '').lstrip(': ').strip()
        acquisition.film_number = ELNSEMExperiment._to_float(
            metadata.get('$$SM_FILM_NUMBER')
        )
        acquisition.micron_bar = ELNSEMExperiment._to_float(
            metadata.get('$$SM_MICRON_BAR')
        )
        acquisition.micron_marker = metadata.get('$$SM_MICRON_MARKER')
        acquisition.font_size = metadata.get('$$SM_FONT_SIZE')

        if acquisition.micron_bar and width:
            fov_width = acquisition.micron_bar * ureg.um
            acquisition.pixel_size = fov_width / width

        pixel_size_val = (
            acquisition.pixel_size.magnitude if acquisition.pixel_size else None
        )
        plot_section = ELNSEMExperiment._build_image_plot(bmp_path, pixel_size_val)
        if plot_section is not None:
            acquisition.plot = plot_section

        return acquisition


    def _scan_and_populate_acquisitions(self, archive, logger) -> None:
        """
        Scan the directory of this ELN entry for JEOL .txt files and matching .bmp files.
        Populate the acquisitions list idempotently.
        """
        # 1. Resolve the directory containing this ELN schema entry
        try:
            with archive.m_context.raw_file(archive.metadata.mainfile) as file:
                eln_abs_path = file.name
        except Exception as exc:
            logger.warning(f'Could not resolve ELN file path: {exc}')
            return

        base_dir = os.path.dirname(eln_abs_path)

        # 2. Enumerate candidate .txt files in a stable sorted order
        try:
            txt_files = sorted([f for f in os.listdir(base_dir) if f.lower().endswith('.txt')])
        except Exception as exc:
            logger.warning(f'Error reading directory {base_dir}: {exc}')
            return

        self.acquisitions = self.acquisitions or []

        # Idempotency safeguard: use the extracted image file name as the unique key
        existing_images = {acq.image for acq in self.acquisitions if acq.image}
        new_acquisitions = []

        for txt_name in txt_files:
            txt_path = os.path.join(base_dir, txt_name)

            # Parse metadata and verify JEOL signature
            metadata = ELNSEMExperiment._read_jeol_txt(txt_path, logger)
            if not any(k.startswith('$CM_') or k.startswith('$$SM_') for k in metadata.keys()):
                continue  # Skip non-JEOL files

            # Find corresponding .bmp. Policy: skip if missing
            bmp_name = txt_name.rsplit('.', 1)[0] + '.bmp'
            bmp_path = os.path.join(base_dir, bmp_name)

            if not os.path.exists(bmp_path):
                logger.warning(f'Missing matching .bmp for {txt_name}, skipping acquisition.')
                continue

            # Idempotency check
            expected_image_ref = ELNSEMExperiment._raw_file_reference(bmp_path, archive, base_dir) or bmp_name
            if expected_image_ref in existing_images:
                continue

            # Build the acquisition section and nest its specific settings
            acquisition = ELNSEMExperiment._build_acquisition_section(
                metadata, bmp_name, bmp_path, archive, base_dir
            )
            settings = ELNSEMExperiment._build_settings(metadata)
            if settings is not None:
                acquisition.settings = settings

            new_acquisitions.append(acquisition)
            existing_images.add(expected_image_ref)

        self.acquisitions.extend(new_acquisitions)

        # Populate entry-level instrument metadata from the first valid scan (if not already set)
        if not self.instrument_metadata and txt_files:
            for txt_name in txt_files:
                txt_path = os.path.join(base_dir, txt_name)
                metadata = ELNSEMExperiment._read_jeol_txt(txt_path, logger)
                inst_meta = ELNSEMExperiment._build_instrument(metadata)
                if inst_meta:
                    self.instrument_metadata = inst_meta
                    break

    def normalize(self, archive, logger):
        self._scan_and_populate_acquisitions(archive, logger)
        super().normalize(archive, logger)


class RawFileSEMData(EntryData):
    """
    Section for a SEM data file entry.
    This entry stores the parsed data from the .txt/.bmp files
    and references the corresponding ELN measurement entry.
    """

    measurement = Quantity(
        type=ELNSEMExperiment,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


m_package.__init_metainfo__()
