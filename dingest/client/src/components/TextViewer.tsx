interface TextViewerProps {
  blocks: string[];
  label?: string;
  isEditing?: boolean;
  onBlockChange?: (index: number, value: string) => void;
}

export const TextViewer = ({
  blocks,
  label = "Block",
  isEditing = false,
  onBlockChange,
}: TextViewerProps) => {
  return (
    <div className={`viewer text-viewer ${isEditing ? "viewer--editing" : ""}`}>
      {blocks.map((block, i) => (
        <div key={i} className="text-block">
          <span className="text-block__label">
            {label} {i + 1}
          </span>

          {isEditing ? (
            <textarea
              className="edit-textarea"
              value={block}
              onChange={(e) => onBlockChange?.(i, e.target.value)}
              rows={Math.max(3, (block.match(/\n/g) || []).length + 1)}
            />
          ) : (
            <p>{block || <em className="empty">— empty —</em>}</p>
          )}
        </div>
      ))}
    </div>
  );
};
