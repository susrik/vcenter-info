import React from 'react';
import Paper from '@material-ui/core/Paper';
import {
  FilteringState,
  IntegratedFiltering,
  SortingState,
  IntegratedSorting
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
                { name: 'overallStatus', title: 'Status'},
                { name: 'state', title: 'Power' },
                { name: 'boot', title: 'Boot Time'},
                { name: 'uptime', title: 'Uptime (s)'},
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
          rows: rsp_json.map(vm => ({
              name: vm.name,
              datacenter: vm.datacenter,
              overallStatus: vm.overallStatus,
              state: vm.state,
              boot: vm.boot,
              uptime: vm.stats.uptimeSeconds,
              annotation: vm.annotation
          }))
      });
    }

    TableRow = ({ row, ...restProps }) => (
      <Table.Row
        {...restProps}
        className={"state-" + row.overallStatus}
        // style={row.overallStatus}
        // style={{ backgroundColor: row.overallStatus }}
      />
    );

    render() {
        return (
            <Paper>
              <Grid
                rows={this.state.rows}
                columns={this.state.columns}
              >
                <FilteringState defaultFilters={[]} />
                <IntegratedFiltering />
                <SortingState defaultSorting={[{ columnName: 'name', direction: 'asc' }]} />
                <IntegratedSorting />
                <Table rowComponent={this.TableRow}/>
                <TableHeaderRow showSortingControls />
                <TableFilterRow />
              </Grid>
            </Paper>
        );
    }
}

export default VMQueryResults;
