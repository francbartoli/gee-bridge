import React from 'react';
import MapBase from './MapBase.jsx'
import ReactDOM from 'react-dom'
import $ from 'jquery'
 
// map socket url
var map_sock = 'ws://' + window.location.host + "/map/"
// preset the current_user
var current_user = null
 
// renders out the base component
function render_component(){
    ReactDOM.render(<MapBase current_user={current_user} socket={map_sock}/>, document.getElementById('map_component'))
}
 
 
render_component()