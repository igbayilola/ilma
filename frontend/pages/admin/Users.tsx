import React, { useState, useEffect, useCallback } from 'react';
import { DataTable } from '../../components/admin/DataTable';
import { Drawer } from '../../components/ui/Drawer';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { ButtonVariant } from '../../types';
import { User, Ban, RotateCcw, Mail, CheckCircle2 } from 'lucide-react';
import { Badge } from '../../components/ui/Cards';
import { adminService, AdminUserDTO } from '../../services/adminService';

export const AdminUsersPage: React.FC = () => {
    const [selectedUser, setSelectedUser] = useState<AdminUserDTO | null>(null);
    const [users, setUsers] = useState<AdminUserDTO[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const pageSize = 50;

    const loadUsers = useCallback(async (p: number) => {
        setIsLoading(true);
        try {
            const result = await adminService.listUsers(p, pageSize);
            setUsers(result.items);
            setTotalPages(result.totalPages);
            setPage(result.page);
        } catch {
            setUsers([]);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => { loadUsers(1); }, [loadUsers]);

    const handleSuspend = async (userId: string) => {
        try {
            await adminService.suspendUser(userId);
            await loadUsers(page);
            setSelectedUser(null);
        } catch (err) {
            console.error('Failed to suspend user', err);
        }
    };

    const handleReactivate = async (userId: string) => {
        try {
            await adminService.reactivateUser(userId);
            await loadUsers(page);
            setSelectedUser(null);
        } catch (err) {
            console.error('Failed to reactivate user', err);
        }
    };

    const columns = [
        {
            header: 'Utilisateur',
            accessor: (row: any) => (
                <div className="flex items-center">
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center mr-3 font-bold text-gray-500">
                        {row.name.charAt(0)}
                    </div>
                    <div>
                        <div className="font-bold text-gray-900">{row.name}</div>
                        <div className="text-xs text-gray-500">{row.email}</div>
                    </div>
                </div>
            )
        },
        {
            header: 'Rôle',
            accessor: (row: any) => <Badge label={row.role} color="gray" size="sm" />
        },
        {
            header: 'Statut',
            accessor: (row: any) => (
                <span className={`text-xs font-bold ${row.isActive ? 'text-green-600' : 'text-red-600'}`}>
                    {row.isActive ? 'Actif' : 'Suspendu'}
                </span>
            )
        },
    ];

    if (isLoading && users.length === 0) {
        return (
            <div className="space-y-6">
                <Skeleton variant="text" className="w-48 h-8" />
                <Skeleton variant="rect" className="h-96" />
            </div>
        );
    }

    return (
        <div className="space-y-6 h-[calc(100vh-140px)] flex flex-col">
            <header className="flex justify-between items-center">
                <h1 className="text-2xl font-extrabold text-gray-900">Utilisateurs</h1>
                <Button leftIcon={<User size={18}/>}>Ajouter manuel</Button>
            </header>

            <DataTable
                columns={columns}
                data={users}
                onRowClick={setSelectedUser}
                pagination={{
                    currentPage: page,
                    totalPages,
                    onPageChange: (p: number) => loadUsers(p),
                }}
            />

            <Drawer
                isOpen={!!selectedUser}
                onClose={() => setSelectedUser(null)}
                title="Détail Utilisateur"
                position="right"
            >
                {selectedUser && (
                    <div className="space-y-8">
                        <div className="flex flex-col items-center text-center">
                            <div className="w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center text-4xl mb-4">
                                {selectedUser.name.charAt(0)}
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900">{selectedUser.name}</h2>
                            <p className="text-gray-500">{selectedUser.email}</p>
                            <div className="flex space-x-2 mt-4">
                                <Badge label={selectedUser.role} color="blue" />
                                <Badge
                                    label={selectedUser.isActive ? 'Actif' : 'Suspendu'}
                                    color={selectedUser.isActive ? 'green' : 'red'}
                                />
                            </div>
                        </div>

                        <div className="space-y-3">
                            <h3 className="font-bold text-gray-800 border-b pb-2">Actions Rapides</h3>
                            {selectedUser.isActive ? (
                                <Button fullWidth variant={ButtonVariant.DANGER} leftIcon={<Ban size={16}/>} onClick={() => handleSuspend(selectedUser.id)}>
                                    Suspendre le compte
                                </Button>
                            ) : (
                                <Button fullWidth variant={ButtonVariant.SECONDARY} leftIcon={<CheckCircle2 size={16}/>} onClick={() => handleReactivate(selectedUser.id)}>
                                    Réactiver le compte
                                </Button>
                            )}
                        </div>

                        <div className="space-y-3">
                             <h3 className="font-bold text-gray-800 border-b pb-2">Informations</h3>
                             <div className="text-sm text-gray-600 space-y-2">
                                 <p><strong>ID:</strong> {selectedUser.id}</p>
                                 {selectedUser.phone && <p><strong>Téléphone:</strong> {selectedUser.phone}</p>}
                             </div>
                        </div>
                    </div>
                )}
            </Drawer>
        </div>
    );
};
