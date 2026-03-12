import os
import shutil
from unittest.mock import MagicMock
from uuid import uuid4

import h5py
import numpy as np
import pytest
from nomad.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.context import ClientContext, ServerContext

from nomad_em_parser_akfeldhoff.schema_packages.sem import ELNSEMExperiment

# Define constants from your original test
EXPECTED_VOLTAGE = 20.0
EXPECTED_MAGNIFICATION = 250.0
EXPECTED_WD = 15.2
EXPECTED_SCAN_SPEED = 735.0
EXPECTED_EMISSION = 10.0


def _data_dir() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '..', 'data')


def _copy_sample_pairs(target_dir: str) -> None:
    data_dir = _data_dir()
    for name in (
        'HeOx-1004-sg-sps-900C-15min-polished-01.txt',
        'HeOx-1004-sg-sps-900C-15min-polished-01.bmp',
        'HeOx-1004-sg-sps-900C-15min-polished-02.txt',
        'HeOx-1004-sg-sps-900C-15min-polished-02.bmp',
    ):
        shutil.copy(os.path.join(data_dir, name), os.path.join(target_dir, name))

    # Create a 3rd txt file explicitly missing its .bmp pair for testing fallback logic
    with open(
        os.path.join(target_dir, 'HeOx-1004-sg-sps-900C-15min-polished-03.txt'),
        'w',
        encoding='utf-8',
    ) as f:
        f.write('$CM_DATE 01/01/2025\n$CM_TIME 12:00:00\n$CM_ACCEL_VOLT 15.0\n')


def _set_txt_datetime(txt_path: str, date_value: str, time_value: str) -> None:
    with open(txt_path, encoding='utf-8', errors='ignore') as f:
        lines = f.read().splitlines()

    updated_lines = []
    for line in lines:
        if line.startswith('$CM_DATE '):
            updated_lines.append(f'$CM_DATE {date_value}')
        elif line.startswith('$CM_TIME '):
            updated_lines.append(f'$CM_TIME {time_value}')
        else:
            updated_lines.append(line)

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines) + '\n')


def test_manual_collection_and_idempotency():
    data_dir = _data_dir()

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

    # 4. Verify the events
    assert eln_entry.events is not None, 'Events list should be created'

    # We now expect 3 events (the 03.txt file is processed even without a .bmp)
    Events_COUNT = 3
    assert len(eln_entry.events) == Events_COUNT, (
        f'Expected {Events_COUNT} events, got {len(eln_entry.events)}'
    )

    # 5. Verify the data nested inside the first event
    event_01 = eln_entry.events[0]
    assert 'HeOx-1004-sg-sps-900C-15min-polished-01.bmp' in event_01.image
    assert event_01.format == 'Bitmap'
    assert event_01.image_id == '84A93E7F77FB'
    assert not event_01.m_is_set('image_data')

    # Verify the nested settings
    settings = event_01.settings
    assert settings is not None
    assert settings.acceleration_voltage.magnitude == EXPECTED_VOLTAGE
    assert settings.magnification == EXPECTED_MAGNIFICATION
    assert settings.working_distance.magnitude == EXPECTED_WD

    # Verify the fallback logic on the event missing its image
    missing_image_events = [e for e in eln_entry.events if e.image is None]
    assert len(missing_image_events) == 1, 'One event should be missing its image'
    assert not missing_image_events[0].m_is_set('image_data')

    # 6. Verify top-level instrument metadata was extracted
    instrument = eln_entry.instrument_metadata
    assert instrument is not None
    assert instrument.name == 'JSM 6700F NT'
    assert instrument.operator == 'GENERAL'

    # 7. Test Idempotency (Running normalize a second time shouldn't duplicate entries)
    eln_entry.normalize(archive, logger)
    assert len(eln_entry.events) == Events_COUNT, (
        'Idempotency failed: normalizing twice duplicated the events!'
    )


def test_hdf5_graceful_fallback_with_client_context(tmp_path):
    _copy_sample_pairs(str(tmp_path))

    (tmp_path / 'dummy.archive.json').write_text('{"data":{}}\n', encoding='utf-8')

    archive = EntryArchive(metadata=EntryMetadata(mainfile='dummy.archive.json'))
    archive.m_context = ClientContext(local_dir=str(tmp_path))
    entry = ELNSEMExperiment()
    archive.data = entry

    logger = MagicMock()
    entry.normalize(archive, logger)
    serialized = archive.m_to_dict()

    assert 'data' in serialized
    assert len(serialized['data'].get('events', [])) == 3  # Noqa: PLR2004
    assert all(not event.m_is_set('image_data') for event in entry.events)


def test_recursive_discovery_with_client_context(tmp_path):
    data_dir = _data_dir()
    nested_dir = tmp_path / 'nested' / 'sem'
    nested_dir.mkdir(parents=True, exist_ok=True)

    for name in (
        'HeOx-1004-sg-sps-900C-15min-polished-01.txt',
        'HeOx-1004-sg-sps-900C-15min-polished-01.bmp',
        'HeOx-1004-sg-sps-900C-15min-polished-02.txt',
        'HeOx-1004-sg-sps-900C-15min-polished-02.bmp',
    ):
        shutil.copy(os.path.join(data_dir, name), nested_dir / name)

    with open(
        nested_dir / 'HeOx-1004-sg-sps-900C-15min-polished-03.txt',
        'w',
        encoding='utf-8',
    ) as f:
        f.write('$CM_DATE 01/01/2025\n$CM_TIME 12:00:00\n$CM_ACCEL_VOLT 15.0\n')

    (tmp_path / 'dummy.archive.json').write_text('{"data":{}}\n', encoding='utf-8')

    archive = EntryArchive(metadata=EntryMetadata(mainfile='dummy.archive.json'))
    archive.m_context = ClientContext(local_dir=str(tmp_path))
    entry = ELNSEMExperiment()
    archive.data = entry

    entry.normalize(archive, MagicMock())

    assert len(entry.events) == 3  # Noqa: PLR2004
    events_with_image = [event for event in entry.events if event.image]
    assert len(events_with_image) == 2  # noqa: PLR2004
    assert all(not event.m_is_set('image_data') for event in entry.events)


def test_events_are_ordered_by_acquisition_timestamp(tmp_path):
    data_dir = _data_dir()

    txt_a_late = tmp_path / 'a_late.txt'
    txt_b_early = tmp_path / 'b_early.txt'
    bmp_a_late = tmp_path / 'a_late.bmp'
    bmp_b_early = tmp_path / 'b_early.bmp'

    shutil.copy(
        os.path.join(data_dir, 'HeOx-1004-sg-sps-900C-15min-polished-01.txt'),
        txt_a_late,
    )
    shutil.copy(
        os.path.join(data_dir, 'HeOx-1004-sg-sps-900C-15min-polished-02.txt'),
        txt_b_early,
    )
    shutil.copy(
        os.path.join(data_dir, 'HeOx-1004-sg-sps-900C-15min-polished-01.bmp'),
        bmp_a_late,
    )
    shutil.copy(
        os.path.join(data_dir, 'HeOx-1004-sg-sps-900C-15min-polished-02.bmp'),
        bmp_b_early,
    )

    _set_txt_datetime(str(txt_a_late), '12/31/2025', '11:59:59 PM')
    _set_txt_datetime(str(txt_b_early), '01/01/2025', '1:00:00 AM')

    (tmp_path / 'dummy.archive.json').write_text('{"data":{}}\n', encoding='utf-8')

    archive = EntryArchive(metadata=EntryMetadata(mainfile='dummy.archive.json'))
    archive.m_context = ClientContext(local_dir=str(tmp_path))
    entry = ELNSEMExperiment()
    archive.data = entry

    entry.normalize(archive, MagicMock())

    assert len(entry.events) == 2  # noqa: PLR2004
    ordered_images = [os.path.basename(event.image) for event in entry.events]
    assert ordered_images == ['b_early.bmp', 'a_late.bmp']


def test_hdf5_serialization_with_server_context(tmp_path):
    pytest.importorskip('zipstream')
    from nomad import files, processing

    source_dir = tmp_path / 'raw_source'
    source_dir.mkdir(parents=True, exist_ok=True)
    _copy_sample_pairs(str(source_dir))
    (source_dir / 'dummy.archive.json').write_text('{"data":{}}\n', encoding='utf-8')

    upload_id = f'semhdf5{uuid4().hex[:8]}'
    entry_id = 'sem_hdf5_entry'
    upload_files = files.StagingUploadFiles(upload_id, create=True)
    try:
        upload_files.add_rawfiles(str(source_dir))
        upload = processing.Upload(upload_id=upload_id)
        archive = EntryArchive(
            metadata=EntryMetadata(
                mainfile='dummy.archive.json', upload_id=upload_id, entry_id=entry_id
            ),
            m_context=ServerContext(upload=upload),
        )
        entry = ELNSEMExperiment()
        archive.data = entry

        entry.normalize(archive, MagicMock())
        serialized = archive.m_to_dict()

        assert len(entry.events) == 3  # noqa: PLR2004
        events_with_image_data = [
            event for event in entry.events if event.m_is_set('image_data')
        ]
        assert len(events_with_image_data) == 2  # noqa: PLR2004

        events_with_axes = [
            event
            for event in entry.events
            if event.m_is_set('x_axis') and event.m_is_set('y_axis')
        ]
        assert len(events_with_axes) == 2  # noqa: PLR2004

        refs = [
            event['image_data']
            for event in serialized['data']['events']
            if 'image_data' in event
        ]
        assert all(
            ref.startswith(f'/uploads/{upload_id}/archive/{entry_id}#/data/events/')
            for ref in refs
        )

        hdf5_path = upload_files.archive_hdf5_location(entry_id)
        assert os.path.exists(hdf5_path)
        with h5py.File(hdf5_path, 'r') as hdf5_file:
            # Dynamically find the first event index that actually contains image_data
            first_valid_index = next(
                i
                for i, event in enumerate(entry.events)
                if event.m_is_set('image_data')
            )
            event_group_path = f'/data/events/{first_valid_index}'
            event_group = hdf5_file[event_group_path]

            assert event_group.attrs.get('NX_class') == 'NXdata'
            assert event_group.attrs.get('signal') == 'image_data'
            axes_attr = event_group.attrs.get('axes')
            assert axes_attr is not None
            axes = [
                axis.decode() if isinstance(axis, bytes) else str(axis)
                for axis in np.asarray(axes_attr).tolist()
            ]
            assert axes == ['y_axis', 'x_axis']

            dataset = hdf5_file[f'{event_group_path}/image_data']
            assert dataset.ndim == 2  # noqa: PLR2004
            assert dataset.dtype == np.dtype(np.uint8)
    finally:
        upload_files.delete()
