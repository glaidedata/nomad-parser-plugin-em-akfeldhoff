import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad.config import config
from nomad.datamodel.context import ServerContext
from nomad.parsing.parser import MatchingParser

from nomad_em_parser_akfeldhoff.schema_packages.sem import (
    ELNSEMExperiment,
    RawFileSEMData,
)
from nomad_em_parser_akfeldhoff.utils import create_archive

configuration = config.get_plugin_entry_point(
    'nomad_em_parser_akfeldhoff.parsers:parser_entry_point'
)


class SEMParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        logger.info('SEMParser.parse')

        mainfile_name = os.path.basename(mainfile)
        if not mainfile_name.endswith('.txt'):
            logger.warning(
                'SEMParser: mainfile is not a .txt, skipping', mainfile=mainfile
            )
            return

        # Create the measurement entry shell; raw-file parsing happens in normalize.
        eln_entry = ELNSEMExperiment.m_from_dict(
            ELNSEMExperiment.m_def.a_template or {}
        )

        # Determine the data_file path used by ELNSEMExperiment.normalize.
        data_file = mainfile_name
        if isinstance(archive.m_context, ServerContext):
            data_file = (
                mainfile.split('/raw/', 1)[1] if '/raw/' in mainfile else mainfile_name
            )
        eln_entry.data_file = data_file

        # Create the ELN archive and store the reference on the raw-data entry.
        file_name = f'{"".join(mainfile_name.split(".")[:-1])}.archive.json'
        measurement_ref = create_archive(eln_entry, archive, file_name)
        archive.data = RawFileSEMData(measurement=measurement_ref)
        archive.metadata.entry_name = f'{mainfile_name} data file'
