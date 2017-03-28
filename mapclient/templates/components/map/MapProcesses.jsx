import React from 'react'

class MapProcesses extends React.Component{
  constructor(props) {
      super(props)
      this.state = {
        process_list: this.props.process_list
      }

      // bind button click
     this.onCreateProcessClick = this.onCreateProcessClick.bind(this);
     this.renderButton = this.renderButton.bind(this);
     //this.renderOpponent = this.renderOpponent.bind(this)
    }

    onCreateProcessClick(event) {
        this.props.sendSocketMessage({action: "create_process"})
    }


    componentWillReceiveProps(newProp){
        this.setState({process_list: newProp.process_list})
    }

    renderButton(process){
         if (process.completed){
            return "View"
         } else if (!(process.algorithm == null) && !(process.completed)){
             return "Waiting..."
         } else{
             return "Start"
         }
                                     
    }

    renderAlgorithm(process){
        console.log(process)
        if (process.algorithm != null){
            return process.algorithm.name
        } else {
            return "???"
        }
    }

    renderProcessesList(){
        console.log(this.props);
        if (this.props.process_list.length > 0){
            return this.props.process_list.map(function(process){
                    return <li key={process.id} className="list-group-item">
                                <span className="badge pull-left">{process.id}</span>&nbsp;&nbsp;
                                <span>{process.creator.username}</span> triggers <span>{this.renderAlgorithm(process)}</span>

                                <a className="btn btn-sm btn-primary pull-right" href={"/process/"+process.id+"/"}>{this.renderButton(process)}</a>
                            </li>
                    }, this)

        }else{
            return ("No Processes")
        }
    }

    render() {
      return (
        <div>
          <div className="panel panel-primary">
                <div className="panel-heading">
                    <span>Your Processes</span>
                    <a href="#" className="pull-right badge" onClick={this.onCreateProcessClick} id="create_process">Start New Process</a>
                </div>
                <div className="panel-body">
                    <div>
                        <ul className="list-group processes-list">
                            {this.renderProcessesList()}
                        </ul>
                    </div>
                </div>
            </div>

        </div>
      )
    }
}

MapProcesses.defaultProps = {

};

MapProcesses.propTypes = {
    process_list: React.PropTypes.array,
    user: React.PropTypes.object
};


export default MapProcesses
