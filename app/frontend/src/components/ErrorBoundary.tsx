import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
    children?: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="container" style={{ paddingTop: 80, textAlign: 'center' }}>
                    <div className="card" style={{ maxWidth: 500, margin: '0 auto', background: '#fef2f2', borderColor: '#f87171' }}>
                        <h2 style={{ color: '#b91c1c', marginBottom: 16 }}>Something went wrong.</h2>
                        <p style={{ color: '#7f1d1d', fontSize: 14 }}>
                            The application encountered an unexpected error.
                        </p>
                        <button
                            className="btn btn-primary"
                            style={{ marginTop: 24 }}
                            onClick={() => {
                                this.setState({ hasError: false });
                                window.location.href = '/';
                            }}
                        >
                            Reload Application
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
