# -*- coding: UTF-8 -*-
from XmlDataProcessor import XMLDataProcessor


class CurrentCostProcessor(XMLDataProcessor):
    def handles_format(self):
        XMLDataProcessor.handles_format(self)
        return self._xml is not None and self._xml.find('src') is not None \
               and self._xml.find('src').text[0:5] == 'CC128'

    def process(self):
        if self._xml.find('id') is not None:
            sensor_id = self._xml.find('id').text
            type = self._xml.find('type').text
            if type != '1':
                raise ValueError('Sensor type "' + type + '" not supported.')
            temp = self._xml.find('tmpr').text
            self.storeDataPoint('CC128/temp', float(temp), '°C')
            channel_index = 1
            while (not self._xml.find('ch' + str(channel_index)) is None):
                channel = self._xml.find('ch' + str(channel_index))
                self.storeDataPoint('CC128/'+sensor_id+'/ch'+str(channel_index),int(channel.find('watts').text), 'W')
                channel_index += 1
        else:
            #could be a history transmission, which we can ignore. If not error.
            if self._xml.find('hist') is None:
                raise ValueError('CC128 - received unknown packet type. ' + self._data['data'])
