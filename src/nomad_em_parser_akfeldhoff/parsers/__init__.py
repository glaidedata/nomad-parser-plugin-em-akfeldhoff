from nomad.config.models.plugins import ParserEntryPoint


class SEMParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_em_parser_akfeldhoff.parsers.sem_parser import SEMParser

        return SEMParser(**self.dict())


parser_entry_point = SEMParserEntryPoint(
    name='SEMParser',
    description='Parser for JEOL SEM data (bmp+txt)',
    mainfile_name_re=r'.*\.txt$',
    mainfile_contents_re=r'(?ms)(?=.*^\$CM_FORMAT\s+Bitmap)(?=.*^\$CM_VERSION\b)',
)
