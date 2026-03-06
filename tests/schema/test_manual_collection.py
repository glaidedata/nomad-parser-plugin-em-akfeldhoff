import os
import shutil
from unittest.mock import MagicMock

from nomad.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.context import ClientContext

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
    archive.m_context.raw_path = None

    mock_file = MagicMock()
    mock_file.name = os.path.join(data_dir, 'dummy.archive.json')
    # When normalize() calls archive.m_context.raw_file(...), it returns our mocked file
    archive.m_context.raw_file.return_value.__enter__.return_value = mock_file

    logger = MagicMock()

    # 3. Create the entry and trigger normalization (Scanning the folder)
    eln_entry = ELNSEMExperiment()
    eln_entry.normalize(archive, logger)

    # 4. Verify the acquisitions
    assert eln_entry.acquisitions is not None, 'Acquisitions list should be created'

    # We expect 2 acquisitions (the 03.txt file should be skipped because it lacks a .bmp)
    Acquisitions_COUNT = 2
    assert len(eln_entry.acquisitions) == Acquisitions_COUNT, (
        f'Expected 2 acquisitions, got {len(eln_entry.acquisitions)}'
    )

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

    # 6b. Verify entry-level gallery figures and acquisition index links
    assert len(eln_entry.figures) == Acquisitions_COUNT
    assert all(acq.plot is None for acq in eln_entry.acquisitions)
    assert [acq.gallery_figure_index for acq in eln_entry.acquisitions] == [0, 1]
    assert [fig.index for fig in eln_entry.figures] == [0, 1]

    # 7. Test Idempotency (Running normalize a second time shouldn't duplicate entries)
    Acquisitions_COUNT = 2
    eln_entry.normalize(archive, logger)
    assert len(eln_entry.acquisitions) == Acquisitions_COUNT, (
        'Idempotency failed: normalizing twice duplicated the acquisitions!'
    )
    assert len(eln_entry.figures) == Acquisitions_COUNT
    assert [acq.gallery_figure_index for acq in eln_entry.acquisitions] == [0, 1]


def test_gallery_serialization_with_client_context(tmp_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')

    for name in (
        'HeOx-1004-sg-sps-900C-15min-polished-01.txt',
        'HeOx-1004-sg-sps-900C-15min-polished-01.bmp',
        'HeOx-1004-sg-sps-900C-15min-polished-02.txt',
        'HeOx-1004-sg-sps-900C-15min-polished-02.bmp',
    ):
        shutil.copy(os.path.join(data_dir, name), tmp_path / name)

    (tmp_path / 'dummy.archive.json').write_text('{"data":{}}\n', encoding='utf-8')

    archive = EntryArchive(metadata=EntryMetadata(mainfile='dummy.archive.json'))
    archive.m_context = ClientContext(local_dir=str(tmp_path))
    entry = ELNSEMExperiment()
    archive.data = entry

    entry.normalize(archive, MagicMock())
    serialized = archive.m_to_dict()

    assert 'data' in serialized
    assert len(serialized['data'].get('acquisitions', [])) == 2  # Noqa: PLR2004
    assert len(serialized['data'].get('figures', [])) == 2  # Noqa: PLR2004


def test_recursive_discovery_with_client_context(tmp_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')
    nested_dir = tmp_path / 'nested' / 'sem'
    nested_dir.mkdir(parents=True, exist_ok=True)

    for name in (
        'HeOx-1004-sg-sps-900C-15min-polished-01.txt',
        'HeOx-1004-sg-sps-900C-15min-polished-01.bmp',
        'HeOx-1004-sg-sps-900C-15min-polished-02.txt',
        'HeOx-1004-sg-sps-900C-15min-polished-02.bmp',
    ):
        shutil.copy(os.path.join(data_dir, name), nested_dir / name)

    (tmp_path / 'dummy.archive.json').write_text('{"data":{}}\n', encoding='utf-8')

    archive = EntryArchive(metadata=EntryMetadata(mainfile='dummy.archive.json'))
    archive.m_context = ClientContext(local_dir=str(tmp_path))
    entry = ELNSEMExperiment()
    archive.data = entry

    entry.normalize(archive, MagicMock())

    assert len(entry.acquisitions) == 2  # Noqa: PLR2004
    assert len(entry.figures) == 2  # Noqa: PLR2004
    assert all(acq.image for acq in entry.acquisitions)
    assert [acq.gallery_figure_index for acq in entry.acquisitions] == [0, 1]
