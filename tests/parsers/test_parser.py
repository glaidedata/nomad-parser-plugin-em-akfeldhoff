import logging
import os

import pytest
from nomad.datamodel import EntryArchive

from nomad_em_parser_akfeldhoff.parsers.sem_parser import SEMParser

# Define constants
EXPECTED_VOLTAGE = 20.0
EXPECTED_MAGNIFICATION = 250.0
EXPECTED_WD = 15.2


def test_sem_parser():
    # 1. ROBUST PATH CALCULATION
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_file_path = os.path.join(
        current_dir, '..', 'data', 'HeOx-1004-sg-sps-900C-15min-polished-01.txt'
    )
    mainfile = os.path.abspath(target_file_path)

    assert os.path.exists(mainfile), f'Test file not found at: {mainfile}'

    # 2. Setup the Parser and Archive
    archive = EntryArchive()
    parser = SEMParser()

    # 3. Run the Parser
    parser.parse(mainfile, archive, logging.getLogger())

    # 4. Verify the Results
    sem_entry = archive.data
    assert sem_entry is not None, 'Parser failed to create an entry in archive.data'

    assert len(sem_entry.images) == 1, (
        f'Expected 1 image, but found {len(sem_entry.images)}'
    )

    image_data = sem_entry.images[0]
    instrument = sem_entry.instrument

    assert image_data.acceleration_voltage.magnitude == EXPECTED_VOLTAGE
    assert image_data.acceleration_voltage.units == 'kilovolt'
    assert image_data.magnification == EXPECTED_MAGNIFICATION
    assert image_data.working_distance.magnitude == EXPECTED_WD
    assert image_data.working_distance.units == 'millimeter'

    assert image_data.image == 'HeOx-1004-sg-sps-900C-15min-polished-01.bmp'
    assert image_data.format == 'Bitmap'
    assert image_data.version == '1.5'
    assert image_data.signal == 'LEI'
    assert image_data.date == '10/29/2025'
    assert image_data.time == '9:33:41 AM'
    assert image_data.image_resolution == '1280x1024'
    assert image_data.scan_speed == 735.0
    assert image_data.scan_average == 1.0
    assert image_data.emission == 10.0
    assert image_data.probe_current == 'C4 F0'
    assert image_data.stage_position is not None
    assert image_data.stage_position.x.magnitude == pytest.approx(37.1761)
    assert image_data.stage_position.x.units == 'millimeter'
    assert image_data.stage_position.y.magnitude == pytest.approx(44.9344)
    assert image_data.stage_position.y.units == 'millimeter'
    assert image_data.stage_position.r.magnitude == pytest.approx(354.9968)
    assert image_data.stage_position.r.units == 'degree'
    assert image_data.stage_position.z.magnitude == pytest.approx(16.90)
    assert image_data.stage_position.z.units == 'millimeter'
    assert image_data.stage_position.t.magnitude == pytest.approx(0.0)
    assert image_data.stage_position.t.units == 'degree'

    assert instrument is not None
    assert instrument.name == 'JSM 6700F NT'
    assert instrument.instrument_type == '6700'
    assert instrument.company == 'UNI-H-PCI'
    assert instrument.operator == 'GENERAL'

    expected_keys = {
        '$$SM_COLUMN_MODE',
        '$$SM_DISPLAY_MODE',
        '$$SM_FILM_NUMBER',
        '$$SM_FONT_SIZE',
        '$$SM_MICRON_BAR',
        '$$SM_MICRON_MARKER',
        '$$SM_SEI_DETECTOR_LEVEL',
        '$$SM_SEI_DETECTOR_MODE',
        '$$SM_WD',
        '$CM_ACCEL_VOLT',
        '$CM_COMMENT',
        '$CM_COMPANY',
        '$CM_DATE',
        '$CM_EMISSION',
        '$CM_FORMAT',
        '$CM_IMAGEID',
        '$CM_IMAGE_RES',
        '$CM_INSTRUMENT',
        '$CM_INSTRUMENT_TYPE',
        '$CM_MAG',
        '$CM_OPERATOR',
        '$CM_PROBE_CURRENT',
        '$CM_SCAN_ANGLE',
        '$CM_SCAN_AVERAGE',
        '$CM_SCAN_SPEED',
        '$CM_SIGNAL',
        '$CM_STAGE_POSITION',
        '$CM_TIME',
        '$CM_TITLE',
        '$CM_VERSION',
        '$SM_COLUM_ECP_ANGLE',
        '$SM_GB_BIAS_VOLT',
        '$SM_GB_GUN_VOLT',
    }
    parsed_keys = {kv.key for kv in image_data.metadata}
    assert parsed_keys == expected_keys
    assert len(image_data.metadata) == len(expected_keys)

    # Overview data populated in results.eln
    assert archive.results is not None
    assert archive.results.eln is not None
    eln = archive.results.eln
    assert 'SEMEntry' in eln.sections
    assert 'SEM' in eln.methods
    assert 'JSM 6700F NT' in eln.instruments
    assert any('20 kV' in desc for desc in eln.descriptions)
