from geojson import (GeoJSON,
                     FeatureCollection,
                     Feature
                    )
import json


class GeoUtil(object):
    """Exploit geospatial utilities"""

    def __init__(self):
        pass

    def extract_geojson_obj(self, json_dict):
        """Extract geojson from a defined json key"""
        try:
            if isinstance(json_dict, dict):
                val_inst = GeoJSON.to_instance(json_dict)
                return val_inst
        except KeyError as e:
            raise Exception(e)
    
    def is_featurecollection_valid(self, fc):
            fc_to_validate = FeatureCollection(fc)
            for ft in fc_to_validate:
                ft_to_validate = Feature(ft)
                if ft_to_validate.errors():
                    return False
            return True
        
