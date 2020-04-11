import React from 'react';
import 'bootstrap'
import VM from './VM';
import './VMQueryResults.scss';

class VMQueryResults extends React.Component {

    constructor() {
        super();
        this.state = {vms: []};
        this.loadVMs();
    }

    async loadVMs() {
      console.log('starting loadVMs()');

      const response = await fetch(
          window.location.origin + '/api/vms'
      );

      const rsp_json = await response.json();
      this.setState({
          vms: rsp_json.map(vm => (
              <table>
                  <VM info={vm}/>
              </table>
          ))
      });

    }

    render() {
        return (
            <div>
                {this.state.vms}
            </div>
        );
    }
}

export default VMQueryResults;
