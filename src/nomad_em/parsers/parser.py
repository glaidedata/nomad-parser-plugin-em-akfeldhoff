import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad.config import config
from nomad.parsing.parser import MatchingParser
from nomad.units import ureg

from nomad_em.schema_packages.schema_package import SEMEntry, SEMImage

configuration = config.get_plugin_entry_point('nomad_em.parsers:parser_entry_point')


class SEMParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        logger.info('SEMParser.parse')

        # 1. Create the main Entry structure
        sem_entry = SEMEntry()
        sem_entry.images = []

        # 2. Get the directory of the uploaded file
        mainfile_dir = os.path.dirname(mainfile)
        # Sort files to ensure deterministic order
        files = sorted(os.listdir(mainfile_dir))

        # 3. Loop through all files to find .txt metadata files with JEOL SEM signature
        for filename in files:
            if filename.endswith('.txt'):
                txt_path = os.path.join(mainfile_dir, filename)

                # Check if a matching .bmp exists (same name, different extension)
                bmp_name = filename.replace('.txt', '.bmp')
                if bmp_name not in files:
                    continue  # Skip orphan txt files

                # 4. Parse the text file (Pass the logger here!)
                metadata = self.read_jeol_txt(txt_path, logger)

                # 5. Populate the SEMImage schema
                image_section = SEMImage()
                image_section.image = bmp_name

                # Map keys from .txt to Schema Fields
                if '$CM_ACCEL_VOLT' in metadata:
                    image_section.acceleration_voltage = (
                        float(metadata['$CM_ACCEL_VOLT']) * ureg.kV
                    )

                if '$CM_MAG' in metadata:
                    image_section.magnification = float(metadata['$CM_MAG'])

                # Note: WD key often has double $ signs in JEOL files
                if '$$SM_WD' in metadata:
                    image_section.working_distance = (
                        float(metadata['$$SM_WD']) * ureg.mm
                    )
                elif '$SM_WD' in metadata:
                    image_section.working_distance = float(metadata['$SM_WD']) * ureg.mm

                if '$CM_DATE' in metadata:
                    image_section.date = metadata['$CM_DATE']

                sem_entry.images.append(image_section)

        # 6. Store the populated entry into the archive
        archive.data = sem_entry

    def read_jeol_txt(self, filepath, logger=None):
        """
        Reads the JEOL SEM txt file.
        """
        data = {}
        try:
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line_content = line.strip()
                    if not line_content:
                        continue
                    # Split by first space
                    parts = line_content.split(' ', 1)
                    if len(parts) == 2:  # noqa: PLR2004
                        key = parts[0].strip()
                        value = parts[1].strip()
                        data[key] = value
        except Exception as e:
            if logger:
                logger.error(f'Error reading {filepath}: {e}')
            else:
                print(f'Error reading {filepath}: {e}')
        return data
