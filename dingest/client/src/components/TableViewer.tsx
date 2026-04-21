interface TableViewerProps {
  sheets: Record<string, Record<string, unknown>[]>;
  isEditing?: boolean;
  onCellChange?: (
    sheetName: string,
    rowIndex: number,
    column: string,
    value: string
  ) => void;
}

export const TableViewer = ({
  sheets,
  isEditing,
  onCellChange,
}: TableViewerProps) => {
  const sheetNames = Object.keys(sheets);

  return (
    <div className="viewer table-viewer">
      {sheetNames.map((name) => {
        const rows = sheets[name];
        if (!rows.length) return null;

        const columns = Object.keys(rows[0]);

        return (
          <div key={name} className="sheet">
            <h3 className="sheet__name">{name}</h3>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    {columns.map((col) => (
                      <th key={col}>{col}</th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {rows.map((row, i) => (
                    <tr key={i}>
                      {columns.map((col) => (
                        <td key={col}>
                          {isEditing ? (
                            <input
                              className="edit-input"
                              value={String(row[col] ?? "")}
                              onChange={(e) =>
                                onCellChange?.(
                                  name,
                                  i,
                                  col,
                                  e.target.value
                                )
                              }
                            />
                          ) : (
                            String(row[col] ?? "")
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}
    </div>
  );
};