import ProjectPanel from '../ProjectPanel';

export default function ProjectPanelExample() {
  return <ProjectPanel onClose={() => console.log('Close project panel')} />;
}
