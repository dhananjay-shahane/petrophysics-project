import DataBrowserPanel from '../DataBrowserPanel';

export default function DataBrowserPanelExample() {
  return (
    <DataBrowserPanel
      onClose={() => console.log('Close data browser')}
      onMinimize={() => console.log('Minimize data browser')}
      onMaximize={() => console.log('Maximize data browser')}
    />
  );
}
