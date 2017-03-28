import React from 'react';
import ReactDOM from 'react-dom';
import Websocket from 'react-websocket'
import $ from 'jquery'
import ol from 'openlayers'
import enLocaleData from 'react-intl/locale-data/en'
import enMessages from 'boundless-sdk/locale/en'
import getMuiTheme from 'material-ui/styles/getMuiTheme'
import { addLocaleData, IntlProvider } from 'react-intl'
import MapPanel from 'boundless-sdk/components/MapPanel'
import LayerList from 'boundless-sdk/components/LayerList'
import HomeButton from 'boundless-sdk/components/HomeButton'
import Zoom from 'boundless-sdk/components/Zoom'
import injectTapEventPlugin from 'react-tap-event-plugin'
import RBOverlayMapConfigService from '../services/RBOverlayMapConfigService'
import RBService from '../services/RBService'
import MapProcesses from './MapProcesses'

// Needed for onTouchTap
// Can go away when react 1.0 release
// Check this repo:
// https://github.com/zilverline/react-tap-event-plugin
injectTapEventPlugin();

// addLocaleData(
//   enLocaleData
// );
var apikey = '';

var groupBase = new ol.layer.Group({
  type: 'base-group',
  title: 'Base maps'
});

const initialLayer = 'OSM';

var map = new ol.Map({
  loadTilesWhileAnimating: true,
  layers: [groupBase],
  controls: [new ol.control.Attribution({collapsible: true})],
  view: new ol.View({
    center: [42, 12],
    zoom: 3
  })
});

class MapBase extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            map_process_list: [],
            completed_process_list: [],
            tileServices: []
        }

        // bind button click
        this.sendSocketMessage = this.sendSocketMessage.bind(this);
    }

    getMapProcesses(){
        this.serverRequest = $.get('http://localhost:8000/process/?format=json', function (result) {
           this.setState({
            map_process_list: result,
             })
        }.bind(this))
    }

    static childContextTypes = {
      muiTheme: React.PropTypes.object,
    }

    getChildContext() {
        return {
            muiTheme: getMuiTheme()
        };
    }

    componentDidMount() {
        var me = this;
        RBService.getTileServices(apikey, function(tileServices) {
          for (var i = 0, ii = tileServices.length; i < ii; ++i) {
            if (tileServices[i].name === initialLayer) {
              groupBase.getLayers().push(RBOverlayMapConfigService.createLayer(tileServices[i]));
              break;
            }
          }
          me.setState({
            tileServices: tileServices
          });
        });
        this.getMapProcesses()
    }

    componentWillUnmount() {
        this.serverRequest.abort();
    }

    handleData(data) {
        //receives messages from the connected websocket
        let result = JSON.parse(data)
        // new processes, so get an updated list of this processes's map
        this.getMapProcesses()
        // we've received an updated list of completed process
        this.setState({completed_process_list: result})
    }

    sendSocketMessage(message){
        // sends message to channels back-end
       const socket = this.refs.socket
       socket.state.ws.send(JSON.stringify(message))
    }

    render() {
        return (
          <IntlProvider locale="en">
            <div className="row">
              <Websocket ref="socket" url={this.props.socket}
                  onMessage={this.handleData.bind(this)} reconnect={true}/>
              <div className="row">
                <div className="col-lg-4">
                  <MapProcesses user={this.props.current_user} process_list={this.state.map_process_list}
                               sendSocketMessage={this.sendSocketMessage} />
                </div>
              </div>
              <div className="row">
                <MapPanel id='map' map={map} useHistory={false} />
                <div><LayerList addBaseMap={{tileServices: this.state.tileServices}} showOnStart={true} showZoomTo={true} allowReordering={true} expandOnHover={false} map={map} /></div>
                <div id='home-button'><HomeButton map={map} /></div>
                <div id='zoom-buttons'><Zoom map={map} /></div>
              </div>
            </div>
          </IntlProvider>
        )
    }
}

MapBase.propTypes = {
    socket: React.PropTypes.string,
    muiTheme: React.PropTypes.object
};

export default MapBase;
