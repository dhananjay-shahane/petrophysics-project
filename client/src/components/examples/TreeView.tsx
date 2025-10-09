import TreeView from '../TreeView';

export default function TreeViewExample() {
  const treeData = [
    {
      id: '1',
      label: 'Project Root',
      type: 'folder' as const,
      children: [
        {
          id: '1-1',
          label: 'src',
          type: 'folder' as const,
          children: [
            { id: '1-1-1', label: 'index.ts', type: 'file' as const },
            { id: '1-1-2', label: 'app.ts', type: 'file' as const },
          ],
        },
        { id: '1-2', label: 'package.json', type: 'file' as const },
      ],
    },
  ];

  return <TreeView data={treeData} />;
}
