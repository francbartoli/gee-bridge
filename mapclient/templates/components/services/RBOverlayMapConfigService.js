import ol from 'openlayers';

class RBOverlayMapConfigService {
  createSource(config) {
    if (config.standard === 'XYZ') {
      return new ol.source.XYZ({
        url: config.endpoint,
        attributions: config.attribution ? [
          new ol.Attribution({html: config.attribution})
        ] : undefined
      });
    } else if (config.standard === 'OSM') {
      return new ol.source.OSM();
    }
  }
  createLayer(config) {
    return new ol.layer.Tile({
      type: 'base',
      title: config.description,
      source: this.createSource(config)
    });
  }
}

export default new RBOverlayMapConfigService();