import os
from unittest.mock import MagicMock
import pytest

from nomad.datamodel import EntryArchive, EntryMetadata
from nomad_em_parser_akfeldhoff.schema_packages.sem import ELNSEMExperiment

# Define constants from your original test
EXPECTED_VOLTAGE = 20.0
EXPECTED_MAGNIFICATION = 250.0
EXPECTED_WD = 15.2
EXPECTED_SCAN_SPEED = 735.0
EXPECTED_EMISSION = 10.0

def test_manual_collection_and_idempotency():
    # 1. Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')

    # 2. Mock the NOMAD context so the schema knows which folder to scan
    archive = EntryArchive(metadata=EntryMetadata(mainfile='dummy.archive.json'))
    archive.m_context = MagicMock()

    mock_file = MagicMock()
    mock_file.name = os.path.join(data_dir, 'dummy.archive.json')
    # When normalize() calls archive.m_context.raw_file(...), it returns our mocked file
    archive.m_context.raw_file.return_value.__enter__.return_value = mock_file

    logger = MagicMock()

    # 3. Create the entry and trigger normalization (Scanning the folder)
    eln_entry = ELNSEMExperiment()
    eln_entry.normalize(archive, logger)

    # 4. Verify the acquisitions
    assert eln_entry.acquisitions is not None, "Acquisitions list should be created"

    # We expect 2 acquisitions (the 03.txt file should be skipped because it lacks a .bmp)
    assert len(eln_entry.acquisitions) == 2, f"Expected 2 acquisitions, got {len(eln_entry.acquisitions)}"

    # 5. Verify the data nested inside the first acquisition
    acq_01 = eln_entry.acquisitions[0]
    assert 'HeOx-1004-sg-sps-900C-15min-polished-01.bmp' in acq_01.image
    assert acq_01.format == 'Bitmap'
    assert acq_01.image_id == '84A93E7F77FB'

    # Verify the nested settings
    settings = acq_01.settings
    assert settings is not None
    assert settings.acceleration_voltage.magnitude == EXPECTED_VOLTAGE
    assert settings.magnification == EXPECTED_MAGNIFICATION
    assert settings.working_distance.magnitude == EXPECTED_WD

    # 6. Verify top-level instrument metadata was extracted
    instrument = eln_entry.instrument_metadata
    assert instrument is not None
    assert instrument.name == 'JSM 6700F NT'
    assert instrument.operator == 'GENERAL'

    # 7. Test Idempotency (Running normalize a second time shouldn't duplicate entries)
    eln_entry.normalize(archive, logger)
    assert len(eln_entry.acquisitions) == 2, "Idempotency failed: normalizing twice duplicated the acquisitions!"
