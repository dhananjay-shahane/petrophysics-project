import DataGrid from '../DataGrid';

export default function DataGridExample() {
  const columns = [
    { id: 'id', label: 'ID', width: '60px' },
    { id: 'name', label: 'Name', width: '200px' },
    { id: 'value', label: 'Value' },
  ];

  const data = [
    { id: '1', name: 'Item 1', value: '100.00' },
    { id: '2', name: 'Item 2', value: '250.50' },
    { id: '3', name: 'Item 3', value: '75.25' },
  ];

  return (
    <DataGrid
      columns={columns}
      data={data}
      onRowClick={(row) => console.log('Row clicked:', row)}
    />
  );
}
