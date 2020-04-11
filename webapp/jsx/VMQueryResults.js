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

      var dummy_vms = [
        { datacenter: "datacenter #1", name: "vm #1 name", state: "vm #1 state", annotation: "vm #1 annotation" },
        { datacenter: "datacenter #2", name: "vm #2 name", state: "vm #2 state", annotation: "vm #2 annotation" }
      ];

      this.setState({
        vms: dummy_vms.map(x => (
          <table>
          <VM info={x}/>
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
