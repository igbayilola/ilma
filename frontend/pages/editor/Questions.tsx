/**
 * Editor Questions page — reuses the admin Editorial page for the Kanban workflow.
 * Editors get the same Kanban board, question CRUD, import, comments, and version history.
 */
import React from 'react';
import { AdminEditorialPage } from '../admin/Editorial';

export const EditorQuestions: React.FC = () => {
  return <AdminEditorialPage />;
};
