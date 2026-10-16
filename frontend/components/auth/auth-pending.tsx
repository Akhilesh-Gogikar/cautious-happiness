/** Shown while the session resolves or a sign-in redirect is on its way. */
export function AuthPending() {
    return (
        <div className="min-h-screen bg-background flex items-center justify-center">
            <div className="w-8 h-8 rounded-full border-t-2 border-primary animate-spin" />
        </div>
    );
}
