import TabbedPanel from '../TabbedPanel';

export default function TabbedPanelExample() {
  const tabs = [
    {
      id: 'logs',
      label: 'Logs',
      content: <div className="p-3 text-sm">Logs content</div>,
    },
    {
      id: 'values',
      label: 'Log Values',
      content: <div className="p-3 text-sm">Log values content</div>,
    },
    {
      id: 'constants',
      label: 'Constants',
      content: <div className="p-3 text-sm">Constants content</div>,
      closeable: true,
    },
  ];

  return (
    <TabbedPanel
      tabs={tabs}
      defaultTab="logs"
      onTabClose={(id) => console.log('Close tab:', id)}
    />
  );
}
