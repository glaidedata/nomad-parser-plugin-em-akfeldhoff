from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from nomad.config import config
from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.datamodel.metainfo.plot import PlotSection
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


class SEMImage(ArchiveSection):
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
    plot = SubSection(
        section_def=SEMImagePlot,
        description='Image preview plot.',
        a_eln=ELNAnnotation(overview=True),
    )


class SEMEntry(ArchiveSection):
    """
    Top-level entry for an SEM experiment containing multiple images.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            label='SEM Experiment (JEOL)',
            overview=True,
            lane_width='600px',
        ),
    )

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
            getattr(self, 'lab_id', None),
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
        if primary_image:
            # prefer settings values if present
            mag = (
                self.settings.magnification
                if self.settings and self.settings.magnification is not None
                else None
            )
            accel = (
                self.settings.acceleration_voltage
                if self.settings and self.settings.acceleration_voltage is not None
                else None
            )
            wd = (
                self.settings.working_distance
                if self.settings and self.settings.working_distance is not None
                else None
            )
            if mag is not None:
                summary_bits.append(f'{mag:g}x')
            if accel is not None:
                summary_bits.append(f'{accel:g} kV')
            if wd is not None:
                summary_bits.append(f'WD {wd:g} mm')
            if primary_image.date:
                summary_bits.append(f'date {primary_image.date}')
        if self.instrument and self.instrument.operator:
            summary_bits.append(f'operator {self.instrument.operator}')

        if summary_bits:
            summary = ', '.join(summary_bits)
            eln.descriptions = eln.descriptions or []
            if summary not in eln.descriptions:
                eln.descriptions.append(summary)

        # Set lab_id from image_id if missing
        if not self.lab_id and primary_image and primary_image.image_id:
            self.lab_id = primary_image.image_id


m_package.__init_metainfo__()
