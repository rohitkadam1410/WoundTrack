
export function LoginPage({ onLogin }: { onLogin: () => void }) {
    return (
        <div className="container" style={{ paddingTop: 80, paddingBottom: 60, maxWidth: 460 }}>
            <div className="card animate-fade-up text-center">
                <span style={{ fontSize: 48, display: 'block', marginBottom: 16 }}>👩🏽‍⚕️</span>
                <h2 className="section-title" style={{ fontSize: 24, marginBottom: 8 }}>ASHA Worker <span>Login</span></h2>
                <p style={{ color: '#64748b', fontSize: 14, marginBottom: 32 }}>Secure login for community health workers.</p>

                <div className="form-group mb-4" style={{ textAlign: 'left' }}>
                    <label className="form-label">Phone Number / ASHA ID</label>
                    <input className="form-input" defaultValue="9876543210" />
                </div>
                <div className="form-group mb-6" style={{ textAlign: 'left' }}>
                    <label className="form-label">OTP / Password</label>
                    <input className="form-input" type="password" defaultValue="1234" />
                </div>

                <button className="btn btn-primary w-full" style={{ padding: 14 }} onClick={onLogin}>
                    Verify & Login
                </button>
            </div>
        </div>
    )
}
