import React from 'react';
import { ChevronLeft, ChevronRight, Search, Filter, Download } from 'lucide-react';
import { Button } from '../ui/Button';
import { ButtonVariant } from '../../types';

interface Column<T> {
  header: string;
  accessor: keyof T | ((row: T) => React.ReactNode);
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  actions?: React.ReactNode;
  pagination?: {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
  };
}

export function DataTable<T extends { id: string | number }>({
  columns,
  data,
  onRowClick,
  searchPlaceholder = "Rechercher...",
  onSearch,
  actions,
  pagination
}: DataTableProps<T>) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col h-full">
      {/* Toolbar */}
      <div className="p-4 border-b border-gray-100 flex flex-col md:flex-row md:items-center justify-between gap-4 flex-shrink-0">
        <div className="flex items-center flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input 
              type="text" 
              placeholder={searchPlaceholder}
              className="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-ilma-primary/20 focus:outline-none"
              onChange={(e) => onSearch && onSearch(e.target.value)}
            />
          </div>
          <button className="ml-2 p-2 text-gray-500 hover:bg-gray-100 rounded-lg border border-gray-200">
            <Filter size={18} />
          </button>
        </div>
        
        <div className="flex items-center space-x-2">
            {actions}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-auto flex-1 min-h-0">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 z-10">
            <tr className="bg-gray-50 border-b border-gray-200">
              {columns.map((col, idx) => (
                <th key={idx} className="px-6 py-3 text-xs uppercase text-gray-500 font-bold tracking-wider whitespace-nowrap">
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.length > 0 ? (
              data.map((row) => (
                <tr 
                  key={row.id} 
                  onClick={() => onRowClick && onRowClick(row)}
                  className={`hover:bg-amber-50/50 transition-colors ${onRowClick ? 'cursor-pointer' : ''}`}
                >
                  {columns.map((col, idx) => (
                    <td key={idx} className={`px-6 py-3 text-sm text-gray-700 whitespace-nowrap ${col.className || ''}`}>
                      {typeof col.accessor === 'function' 
                        ? col.accessor(row) 
                        : (row[col.accessor] as React.ReactNode)}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="px-6 py-12 text-center text-gray-500 text-sm">
                  Aucune donnée trouvée.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && (
        <div className="p-4 border-t border-gray-100 flex items-center justify-between">
          <span className="text-xs text-gray-500">
            Page {pagination.currentPage} sur {pagination.totalPages}
          </span>
          <div className="flex space-x-2">
            <Button 
                variant={ButtonVariant.GHOST} 
                size="sm" 
                disabled={pagination.currentPage === 1}
                onClick={() => pagination.onPageChange(pagination.currentPage - 1)}
            >
              <ChevronLeft size={16} />
            </Button>
            <Button 
                variant={ButtonVariant.GHOST} 
                size="sm"
                disabled={pagination.currentPage === pagination.totalPages}
                onClick={() => pagination.onPageChange(pagination.currentPage + 1)}
            >
              <ChevronRight size={16} />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}