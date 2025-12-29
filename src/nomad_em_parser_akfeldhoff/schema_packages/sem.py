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


class SEMImage(ArchiveSection):
    """
    Section representing a single SEM image and its extracted metadata.
    """

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


m_package.__init_metainfo__()
