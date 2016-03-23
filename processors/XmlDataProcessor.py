from BaseProcessor import BaseProcessor
import xml.etree.ElementTree

class XMLDataProcessor(BaseProcessor):
    _xml = None
    def handles_format(self):
        try:
            self._xml = xml.etree.ElementTree.fromstring(self._data['data'])
        except:
            return False
        return True
