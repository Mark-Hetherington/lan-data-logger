from lib.db import session, DataPath, DataPoint

class BaseProcessor(object):
    def __init__(self, data):
        self._data = data

    def dbsession(self):
        return session
    # Quick initial sanity check of data. If this is no less expensive then processing the data it could either just
    # return true or preprocess it.
    def handles_format(self):
        return False

    # process data
    def process(self):
        raise NotImplementedError('Processing of this format not implemented.')

    def storeDataPoint(self, path, value, units):
        #raise NotImplementedError('Processing of this format not implemented.')
        db = session() # with session() as db:
        data_path = db.query(DataPath).filter(DataPath.path==path).first()
        if data_path is None:
            data_path = DataPath(path=path, units=units)
            db.add(data_path)
        data_path.units = units
        point = DataPoint(path=data_path.path,value=value, when=self._data['time'])
        db.add(point)
        db.commit()
        db.close()
