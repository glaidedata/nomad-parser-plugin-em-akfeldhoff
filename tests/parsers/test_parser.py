import os

import pytest
from nomad.client import normalize_all, parse
from nomad.utils import hash as m_hash

from nomad_em_parser_akfeldhoff.schema_packages.sem import RawFileSEMData

# Define constants
EXPECTED_VOLTAGE = 20.0
EXPECTED_MAGNIFICATION = 250.0
EXPECTED_WD = 15.2
EXPECTED_SCAN_SPEED = 735.0
EXPECTED_EMISSION = 10.0


def test_sem_parser():  # noqa: PLR0915
    # 1. ROBUST PATH CALCULATION
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_file_path = os.path.join(
        current_dir, '..', 'data', 'HeOx-1004-sg-sps-900C-15min-polished-01.txt'
    )
    mainfile = os.path.abspath(target_file_path)

    assert os.path.exists(mainfile), f'Test file not found at: {mainfile}'

    # 2. Use nomad.client.parse to properly set up the context
    file_archive = parse(mainfile)[0]

    # 3. Verify the data file entry was created
    assert file_archive.data is not None, (
        'Parser failed to create an entry in archive.data'
    )
    assert isinstance(file_archive.data, RawFileSEMData), (
        'Expected RawFileSEMData entry'
    )

    # 4. Verify the measurement reference was created
    rel_measurement_archive_path = os.path.join(
        mainfile.rsplit('.', 1)[0] + '.archive.json'
    )
    upload_id = None
    expected_ref = (
        f'../uploads/{upload_id}/archive/'
        f'{m_hash(upload_id, os.path.basename(rel_measurement_archive_path))}#data'
    )
    assert file_archive.data.measurement.m_proxy_value == expected_ref, (
        f'Expected measurement reference {expected_ref}, '
        f'got {file_archive.data.measurement.m_proxy_value}'
    )

    # 5. Parse the measurement archive (the ELN entry)
    measurement_archive = parse(rel_measurement_archive_path)[0]

    # 5a. Normalize the measurement archive to populate results
    normalize_all(measurement_archive)

    sem_entry = measurement_archive.data

    # 6. Verify the measurement entry
    assert sem_entry is not None, 'Parser failed to create measurement entry'

    assert len(sem_entry.images) == 1, (
        f'Expected 1 image, but found {len(sem_entry.images)}'
    )

    image_data = sem_entry.images[0]
    instrument = sem_entry.instrument

    # image-level metadata
    assert image_data.image == 'HeOx-1004-sg-sps-900C-15min-polished-01.bmp'
    assert image_data.format == 'Bitmap'
    assert image_data.version == '1.5'
    assert image_data.date == '10/29/2025'
    assert image_data.time == '9:33:41 AM'
    assert image_data.comment == ''
    assert image_data.title == ''
    assert image_data.image_id == '84A93E7F77FB'
    # Check that Scale Bar logic worked
    assert image_data.pixel_size is not None
    assert image_data.pixel_size.magnitude > 0

    settings = sem_entry.settings
    assert settings is not None
    assert settings.signal == 'LEI'
    assert settings.acceleration_voltage.magnitude == EXPECTED_VOLTAGE
    assert settings.acceleration_voltage.units == 'kilovolt'
    assert settings.magnification == EXPECTED_MAGNIFICATION
    assert settings.working_distance.magnitude == EXPECTED_WD
    assert settings.working_distance.units == 'millimeter'
    assert settings.image_resolution == '1280x1024'
    assert settings.scan_speed == EXPECTED_SCAN_SPEED
    assert settings.scan_average == 1.0
    assert settings.emission == EXPECTED_EMISSION
    assert settings.probe_current == 'C4 F0'
    assert settings.stage_position is not None
    assert settings.stage_position.x.magnitude == pytest.approx(37.1761)
    assert settings.stage_position.x.units == 'millimeter'
    assert settings.stage_position.y.magnitude == pytest.approx(44.9344)
    assert settings.stage_position.y.units == 'millimeter'
    assert settings.stage_position.r.magnitude == pytest.approx(354.9968)
    assert settings.stage_position.r.units == 'degree'
    assert settings.stage_position.z.magnitude == pytest.approx(16.90)
    assert settings.stage_position.z.units == 'millimeter'
    assert settings.stage_position.t.magnitude == pytest.approx(0.0)
    assert settings.stage_position.t.units == 'degree'

    assert instrument is not None
    assert instrument.name == 'JSM 6700F NT'
    assert instrument.instrument_type == '6700'
    assert instrument.company == 'UNI-H-PCI'
    assert instrument.operator == 'GENERAL'

    # Overview data populated in results.eln
    assert measurement_archive.results is not None
    assert measurement_archive.results.eln is not None
    eln = measurement_archive.results.eln
    assert 'ELNSEMExperiment' in eln.sections
    assert 'SEM' in eln.methods
    assert 'JSM 6700F NT' in eln.instruments
    assert any('20' in desc for desc in eln.descriptions)
    assert eln.names is not None and len(eln.names) > 0

    # Clean up the created .archive.json file
    try:
        os.remove(rel_measurement_archive_path)
    except FileNotFoundError:
        pass
