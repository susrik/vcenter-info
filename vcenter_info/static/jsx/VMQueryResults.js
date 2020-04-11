import React from 'react';
import Paper from '@material-ui/core/Paper';
import {
  FilteringState,
  IntegratedFiltering,
} from '@devexpress/dx-react-grid';
import {
  Grid,
  Table,
  TableHeaderRow,
  TableFilterRow,
} from '@devexpress/dx-react-grid-material-ui';
import './VMQueryResults.scss';

class VMQueryResults extends React.Component {

    constructor() {
        super();
        this.state = {
            columns: [
                { name: 'datacenter', title: 'Data Center' },
                { name: 'name', title: 'Name' },
                { name: 'state', title: 'State' },
                { name: 'annotation', title: 'Annotation' }
                ],
            rows: []
        };
        this.loadVMs();
    }

    async loadVMs() {
      console.log('starting loadVMs()');

      const response = await fetch(
          window.location.origin + '/api/vms'
      );

      const rsp_json = await response.json();
      this.setState({
          rows: rsp_json
      });
    }

    render() {
        return (
            <Paper>
              <Grid
                rows={this.state.rows}
                columns={this.state.columns}
              >
                <FilteringState defaultFilters={[]} />
                <IntegratedFiltering />
                <Table />
                <TableHeaderRow />
                <TableFilterRow />
              </Grid>
            </Paper>
        );
    }
}

export default VMQueryResults;
