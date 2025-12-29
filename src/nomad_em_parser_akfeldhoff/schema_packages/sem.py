from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from nomad.config import config
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

configuration = config.get_plugin_entry_point(
    'nomad_em_parser_akfeldhoff.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()


class SEMInstrument(ArchiveSection):
    """
    Instrument information for the SEM.
    """

    name = Quantity(type=str, description='Instrument model name (e.g., JSM 6700F NT)')
    instrument_type = Quantity(type=str, description='Instrument type identifier.')
    company = Quantity(type=str, description='Operating company or institution.')
    operator = Quantity(type=str, description='Instrument operator recorded by SEM.')


class SEMStagePosition(ArchiveSection):
    """
    Stage coordinates captured during acquisition.
    """

    x = Quantity(type=float, unit='mm', description='Stage X position.')
    y = Quantity(type=float, unit='mm', description='Stage Y position.')
    r = Quantity(type=float, unit='deg', description='Stage rotation.')
    z = Quantity(type=float, unit='mm', description='Stage Z position.')
    t = Quantity(type=float, unit='deg', description='Stage tilt.')


class KeyValueMetadata(ArchiveSection):
    """
    Raw key/value metadata captured from the JEOL txt file.
    """

    key = Quantity(type=str, description='Metadata key from JEOL txt.')
    value = Quantity(type=str, description='Metadata value from JEOL txt.')


class SEMImage(ArchiveSection):
    """
    Section representing a single SEM image and its extracted metadata.
    """

    format = Quantity(type=str, description='Image format identifier ($CM_FORMAT).')
    version = Quantity(type=str, description='Format version ($CM_VERSION).')
    comment = Quantity(type=str, description='Comment ($CM_COMMENT).')
    title = Quantity(type=str, description='Title ($CM_TITLE).')
    time = Quantity(type=str, description='Acquisition time ($CM_TIME).')
    operator = Quantity(type=str, description='Operator recorded for the image.')
    company = Quantity(type=str, description='Company recorded for the image.')
    image_id = Quantity(type=str, description='Image identifier ($CM_IMAGEID).')
    instrument_type = Quantity(
        type=str, description='Instrument type reported with the image.'
    )
    instrument_name = Quantity(
        type=str, description='Instrument name reported with the image.'
    )

    image = Quantity(
        type=str,
        description='The image file (.bmp) associated with this metadata.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.FileEditQuantity, label='SEM Image'
        ),
    )

    acceleration_voltage = Quantity(
        type=float,
        unit='kV',
        description='Acceleration Voltage ($CM_ACCEL_VOLT)',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )

    magnification = Quantity(
        type=float,
        description='Magnification ($CM_MAG)',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )

    working_distance = Quantity(
        type=float,
        unit='mm',
        description='Working Distance ($$SM_WD)',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
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
    font_size = Quantity(
        type=str, description='Font size settings ($$SM_FONT_SIZE).'
    )
    display_mode = Quantity(type=str, description='Display mode ($$SM_DISPLAY_MODE).')
    column_mode = Quantity(type=str, description='Column mode ($$SM_COLUMN_MODE).')
    sei_detector_mode = Quantity(
        type=float, description='SEI detector mode ($$SM_SEI_DETECTOR_MODE).'
    )
    sei_detector_level = Quantity(
        type=float, description='SEI detector level ($$SM_SEI_DETECTOR_LEVEL).'
    )
    gun_voltage = Quantity(type=float, description='Gun voltage ($SM_GB_GUN_VOLT).')
    bias_voltage = Quantity(type=float, description='Bias voltage ($SM_GB_BIAS_VOLT).')
    column_ecp_angle = Quantity(
        type=float, description='Column ECP angle ($SM_COLUM_ECP_ANGLE).'
    )
    image_resolution = Quantity(type=str, description='Image resolution ($CM_IMAGE_RES).')
    scan_angle = Quantity(type=str, description='Scan angle ($CM_SCAN_ANGLE).')
    scan_speed = Quantity(type=float, description='Scan speed ($CM_SCAN_SPEED).')
    scan_average = Quantity(type=float, description='Scan average ($CM_SCAN_AVERAGE).')
    probe_current = Quantity(
        type=str, description='Probe current configuration ($CM_PROBE_CURRENT).'
    )
    emission = Quantity(type=float, description='Emission current ($CM_EMISSION).')

    stage_position = SubSection(
        section_def=SEMStagePosition, description='Stage position during acquisition.'
    )

    metadata = SubSection(
        section_def=KeyValueMetadata, repeats=True, description='Raw metadata pairs.'
    )


class SEMEntry(EntryData):
    """
    Top-level entry for an SEM experiment containing multiple images.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            label='SEM Experiment (JEOL)',
        )
    )

    description = Quantity(
        type=str,
        description='Description of this SEM collection.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )

    # This SubSection holds the list of images found in the folder
    images = SubSection(section_def=SEMImage, repeats=True, label='Detected Images')
    instrument = SubSection(
        section_def=SEMInstrument,
        description='Instrument metadata captured from the JEOL txt.',
    )


m_package.__init_metainfo__()
