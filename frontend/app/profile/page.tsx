"use client"

import { useAuth } from '@/components/providers/auth-context';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ProfilePage() {
    const { user, isAuthenticated, isLoading, logout } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push('/login');
        }
    }, [isLoading, isAuthenticated, router]);

    if (isLoading || !user) {
        return <div className="flex h-screen items-center justify-center">Loading...</div>;
    }

    return (
        <div className="container mx-auto py-10">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">User Profile</h1>
                <Button variant="outline" onClick={logout}>Logout</Button>
            </div>

            <div className="grid gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Personal Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <div className="text-sm font-medium text-muted-foreground">Full Name</div>
                                <div className="text-lg">{user.full_name}</div>
                            </div>
                            <div>
                                <div className="text-sm font-medium text-muted-foreground">Email</div>
                                <div className="text-lg">{user.email}</div>
                            </div>
                            <div>
                                <div className="text-sm font-medium text-muted-foreground">Role</div>
                                <div className="text-lg capitalize">{user.role}</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Security Settings</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-muted-foreground">Password recovery is enabled via security questions.</p>
                        <Button variant="secondary" className="mt-4" disabled>Change Password (Coming Soon)</Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
