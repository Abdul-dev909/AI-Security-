import type { ReactNode } from 'react';
import './DataTable.css';

interface DataTableColumn<T> {
  key: string;
  header: string;
  width?: string;
  render?: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: DataTableColumn<T>[];
  data: T[];
  emptyTitle?: string;
  emptyDescription?: string;
  keyExtractor: (row: T) => string;
}

export function DataTable<T>({
  columns,
  data,
  emptyTitle = 'No Data',
  emptyDescription = 'No records to display.',
  keyExtractor,
}: DataTableProps<T>) {
  if (data.length === 0) {
    /* Inline empty state to avoid circular dep */
    return (
      <div className="data-table__empty">
        <p className="data-table__empty-title">{emptyTitle}</p>
        <p className="data-table__empty-desc">{emptyDescription}</p>
      </div>
    );
  }

  return (
    <div className="data-table__wrapper">
      <table className="data-table" role="table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className="data-table__th"
                style={col.width ? { width: col.width } : undefined}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <tr
              key={keyExtractor(row)}
              className="data-table__row"
              style={{ animationDelay: `${rowIndex * 50}ms` }}
            >
              {columns.map((col) => (
                <td key={col.key} className="data-table__td">
                  {col.render
                    ? col.render(row)
                    : String((row as Record<string, unknown>)[col.key] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
