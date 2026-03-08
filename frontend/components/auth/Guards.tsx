import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { UserRole } from '../../types';
import { Skeleton } from '../ui/Skeleton';

interface RoleRouteProps {
  allowedRoles: UserRole[];
}

export const ProtectedRoute: React.FC = () => {
  const { user, isLoading } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return <div className="p-10 text-center"><Skeleton variant="text" className="w-1/2 mx-auto"/></div>;
  }

  if (!user) {
    // Redirect to login while saving the attempted location
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
};

export const RoleRoute: React.FC<RoleRouteProps> = ({ allowedRoles }) => {
  const { user, activeProfile, isLoading } = useAuthStore();

  if (isLoading) {
    return <div className="p-10 text-center"><Skeleton variant="text" className="w-1/2 mx-auto"/></div>;
  }

  if (!user) {
    return <Navigate to="/unauthorized" replace />;
  }

  // Allow parent users accessing student routes when they have an active child profile
  const isParentWithChildProfile = user.role === UserRole.PARENT && activeProfile != null;
  if (!allowedRoles.includes(user.role) && !isParentWithChildProfile) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
};

/**
 * RequireProfile guard: redirects to /select-profile if no activeProfile is set.
 * Used for student routes that need a profile context.
 */
export const RequireProfile: React.FC = () => {
  const { activeProfile, profiles, isLoading } = useAuthStore();

  if (isLoading) {
    return <div className="p-10 text-center"><Skeleton variant="text" className="w-1/2 mx-auto"/></div>;
  }

  // If no active profile and more than 1 profile → go to selector
  if (!activeProfile && profiles.length !== 1) {
    return <Navigate to="/select-profile" replace />;
  }

  return <Outlet />;
};

export const GuestRoute: React.FC = () => {
    const { user, isLoading } = useAuthStore();

    if (isLoading) return null;

    if (user) {
        // Redirect authenticated users based on profiles
        const { profiles, activeProfile } = useAuthStore.getState();

        // If parent or student with 2+ profiles and no active profile → go to selector
        if (profiles.length > 1 && !activeProfile) {
            return <Navigate to="/select-profile" replace />;
        }

        const home = user.role === UserRole.ADMIN
            ? '/app/admin/dashboard'
            : (!activeProfile ? '/select-profile' : '/app/student/dashboard');
        return <Navigate to={home} replace />;
    }
    return <Outlet />;
};
