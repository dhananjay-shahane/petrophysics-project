import DockPanel from '../DockPanel';

export default function DockPanelExample() {
  return (
    <DockPanel
      title="Example Panel"
      onClose={() => console.log('Close clicked')}
      onMinimize={() => console.log('Minimize clicked')}
      onMaximize={() => console.log('Maximize clicked')}
    >
      <div className="p-4">
        <p className="text-sm text-card-foreground">Panel content goes here</p>
      </div>
    </DockPanel>
  );
}
