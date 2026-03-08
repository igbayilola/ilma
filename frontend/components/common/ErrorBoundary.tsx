
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { telemetry } from '../../services/telemetry';
import { Button } from '../ui/Button';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  declare props: Readonly<Props>;
  declare state: State;

  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    telemetry.logError(error, { componentStack: errorInfo.componentStack }, 'ErrorBoundary');
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gray-50 text-center">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mb-6">
            <AlertTriangle size={40} className="text-red-600" />
          </div>
          <h1 className="text-2xl font-extrabold text-gray-900 mb-2">Oups ! Une erreur est survenue.</h1>
          <p className="text-gray-500 mb-8 max-w-sm">
            Ne t'inquiète pas, nous avons été notifiés. Essaie de rafraîchir la page.
          </p>
          
          <div className="bg-white p-4 rounded-xl border border-gray-200 mb-8 w-full max-w-md text-left overflow-auto max-h-40">
            <code className="text-xs text-red-500 font-mono">
                {this.state.error?.message}
            </code>
          </div>

          <Button onClick={this.handleReload} leftIcon={<RefreshCw size={18}/>}>
            Rafraîchir l'application
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
