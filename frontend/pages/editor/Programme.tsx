/**
 * Editor Programme page — reuses the admin Content page for curriculum management.
 * Editors get the same tree view and CRUD without admin-only features.
 */
import React from 'react';
import { AdminContentPage } from '../admin/Content';

export const EditorProgramme: React.FC = () => {
  return <AdminContentPage />;
};
