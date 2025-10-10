import WellsPanel from '../WellsPanel';

export default function WellsPanelExample() {
  return <WellsPanel onClose={() => console.log('Close wells panel')} />;
}
