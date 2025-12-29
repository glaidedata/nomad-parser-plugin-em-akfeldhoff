from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from nomad.config import config
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    SectionProperties,
)
from nomad.datamodel.results import ELN, Results
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

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
            properties=SectionProperties(
                order=['name', 'instrument_type', 'company', 'operator'],
                overview=True,
                lane_width='400px',
            )
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

    x = Quantity(type=float, unit='mm', description='Stage X position.')
    y = Quantity(type=float, unit='mm', description='Stage Y position.')
    r = Quantity(type=float, unit='deg', description='Stage rotation.')
    z = Quantity(type=float, unit='mm', description='Stage Z position.')
    t = Quantity(type=float, unit='deg', description='Stage tilt.')


class SEMSettings(ArchiveSection):
    """
    Instrument settings captured during acquisition (per entry).
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'display_mode',
                    'column_mode',
                    'image_resolution',
                    'scan_speed',
                    'scan_average',
                    'probe_current',
                    'emission',
                    'gun_voltage',
                    'bias_voltage',
                    'column_ecp_angle',
                    'stage_position',
                ],
                overview=True,
                lane_width='400px',
            )
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
    sei_detector_mode = Quantity(
        type=float,
        description='SEI detector mode ($$SM_SEI_DETECTOR_MODE).',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    sei_detector_level = Quantity(
        type=float,
        description='SEI detector level ($$SM_SEI_DETECTOR_LEVEL).',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    image_resolution = Quantity(
        type=str,
        description='Image resolution ($CM_IMAGE_RES).',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            overview=True,
        ),
    )
    scan_angle = Quantity(type=str, description='Scan angle ($CM_SCAN_ANGLE).')
    scan_speed = Quantity(
        type=float,
        description='Scan speed ($CM_SCAN_SPEED).',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    scan_average = Quantity(
        type=float,
        description='Scan average ($CM_SCAN_AVERAGE).',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    probe_current = Quantity(
        type=str,
        description='Probe current configuration ($CM_PROBE_CURRENT).',
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )
    emission = Quantity(
        type=float,
        description='Emission current ($CM_EMISSION).',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    gun_voltage = Quantity(
        type=float,
        description='Gun voltage ($SM_GB_GUN_VOLT).',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    bias_voltage = Quantity(
        type=float,
        description='Bias voltage ($SM_GB_BIAS_VOLT).',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    column_ecp_angle = Quantity(
        type=float,
        description='Column ECP angle ($SM_COLUM_ECP_ANGLE).',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    stage_position = SubSection(
        section_def=SEMStagePosition,
        description='Stage position during acquisition.',
        a_eln=ELNAnnotation(overview=True),
    )


class SEMImage(ArchiveSection):
    """
    Section representing a single SEM image and its extracted metadata.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'image',
                    'image_id',
                    'format',
                    'version',
                    'signal',
                    'magnification',
                    'acceleration_voltage',
                    'working_distance',
                    'date',
                    'time',
                ],
                overview=True,
                lane_width='400px',
            )
        )
    )

    format = Quantity(type=str, description='Image format identifier ($CM_FORMAT).')
    version = Quantity(type=str, description='Format version ($CM_VERSION).')
    comment = Quantity(type=str, description='Comment ($CM_COMMENT).')
    title = Quantity(type=str, description='Title ($CM_TITLE).')
    time = Quantity(type=str, description='Acquisition time ($CM_TIME).')
    image_id = Quantity(type=str, description='Image identifier ($CM_IMAGEID).')

    image = Quantity(
        type=str,
        description='The image file (.bmp) associated with this metadata.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.FileEditQuantity,
            label='SEM Image',
            overview=True,
        ),
        a_browser=dict(adaptor='RawFileAdaptor', label='SEM image'),
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

    date = Quantity(
        type=str,
        description='Date of acquisition ($CM_DATE)',
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )

    signal = Quantity(type=str, description='Signal mode ($CM_SIGNAL).')
    film_number = Quantity(type=float, description='Film number ($$SM_FILM_NUMBER).')
    micron_bar = Quantity(type=float, description='Micron bar size ($$SM_MICRON_BAR).')
    micron_marker = Quantity(
        type=str, description='Micron marker label ($$SM_MICRON_MARKER).'
    )
    font_size = Quantity(type=str, description='Font size settings ($$SM_FONT_SIZE).')


class SEMEntry(EntryData):
    """
    Top-level entry for an SEM experiment containing multiple images.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            label='SEM Experiment (JEOL)',
            properties=SectionProperties(
                order=['name', 'instrument', 'settings', 'images', 'description'],
                overview=True,
                lane_width='600px',
            ),
        ),
    )

    name = Quantity(
        type=str,
        description='Display name for this SEM entry.',
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

    # This SubSection holds the list of images found in the folder
    images = SubSection(
        section_def=SEMImage,
        repeats=True,
        label='images',
        a_eln=ELNAnnotation(overview=True),
    )
    instrument = SubSection(
        section_def=SEMInstrument,
        description='Instrument metadata captured from the JEOL txt.',
        a_eln=ELNAnnotation(overview=True),
    )
    settings = SubSection(
        section_def=SEMSettings,
        description='Instrument settings captured from the JEOL txt.',
        a_eln=ELNAnnotation(overview=True),
    )

    def normalize(self, archive, logger):
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

        if self.instrument and self.instrument.name:
            eln.instruments = eln.instruments or []
            if self.instrument.name not in eln.instruments:
                eln.instruments.append(self.instrument.name)

        primary_image = self.images[0] if self.images else None
        candidate_name = None
        for candidate in (
            getattr(self, 'name', None),
            getattr(primary_image, 'title', None),
            getattr(primary_image, 'image', None),
        ):
            if candidate:
                candidate_name = candidate
                break
        if candidate_name:
            if not self.name:
                # strip known image suffixes when using filename as fallback name
                stripped = (
                    candidate_name.rsplit('.', 1)[0]
                    if candidate_name.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg'))
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
        if primary_image:
            if primary_image.magnification is not None:
                summary_bits.append(f'{primary_image.magnification:g}x')
            if primary_image.acceleration_voltage is not None:
                summary_bits.append(
                    f'{primary_image.acceleration_voltage.magnitude:g} kV'
                )
            if primary_image.working_distance is not None:
                summary_bits.append(
                    f'WD {primary_image.working_distance.magnitude:g} mm'
                )
            if primary_image.date:
                summary_bits.append(f'date {primary_image.date}')
        if self.instrument and self.instrument.operator:
            summary_bits.append(f'operator {self.instrument.operator}')

        if summary_bits:
            summary = ', '.join(summary_bits)
            eln.descriptions = eln.descriptions or []
            if summary not in eln.descriptions:
                eln.descriptions.append(summary)


m_package.__init_metainfo__()
