from compressor.filters import FilterBase

class ModuleTypeFilter(FilterBase):
    def process_content(self, content):
        return content.replace('<script ', '<script type=\"module\" ')