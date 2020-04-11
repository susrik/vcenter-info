import React from 'react';
import 'bootstrap'
import './VM.scss';

class VM extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
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
