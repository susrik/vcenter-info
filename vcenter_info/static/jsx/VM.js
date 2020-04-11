import React from 'react';
import 'bootstrap'
import './VM.scss';

class VM extends React.Component {

    constructor(props) {
        super(props);
    }

    renderTableHeader() {
        return (
            <tr>
              <th scope="col">datacenter</th>
              <th scope="col">name</th>
              <th scope="col">state</th>
              <th scope="col">annotation</th>
            </tr>
        );
    }
    render() {
        if (this.props.info == null) {
            return this.renderTableHeader()
        }

        return (
            <tr>
              <td>{this.props.info.datacenter}</td>
              <td>{this.props.info.name}</td>
              <td>{this.props.info.state}</td>
              <td>{this.props.info.annotation}</td>
            </tr>
        );
    }
}

export default VM;
