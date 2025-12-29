import logging
import os

from nomad.datamodel import EntryArchive

from nomad_em_parser_akfeldhoff.parsers.parser import SEMParser

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

    assert image_data.acceleration_voltage.magnitude == EXPECTED_VOLTAGE
    assert image_data.acceleration_voltage.units == 'kilovolt'
    assert image_data.magnification == EXPECTED_MAGNIFICATION
    assert image_data.working_distance.magnitude == EXPECTED_WD
    assert image_data.working_distance.units == 'millimeter'

    assert image_data.image == 'HeOx-1004-sg-sps-900C-15min-polished-01.bmp'
