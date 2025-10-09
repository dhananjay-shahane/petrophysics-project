import FeedbackPanel from '../FeedbackPanel';

export default function FeedbackPanelExample() {
  return (
    <FeedbackPanel
      onClose={() => console.log('Close feedback')}
      onMinimize={() => console.log('Minimize feedback')}
      onMaximize={() => console.log('Maximize feedback')}
    />
  );
}
