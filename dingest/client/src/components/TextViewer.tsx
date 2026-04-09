interface TextViewerProps {
  blocks: string[];
  label?: string; // "Page" or "Paragraph"
}

export const TextViewer = ({ blocks, label = "Block" }: TextViewerProps) => {
  return (
    <div className="viewer text-viewer">
      {blocks.map((block, i) => (
        <div key={i} className="text-block">
          <span className="text-block__label">{label} {i + 1}</span>
          <p>{block || <em className="empty">— empty —</em>}</p>
        </div>
      ))}
    </div>
  );
};
