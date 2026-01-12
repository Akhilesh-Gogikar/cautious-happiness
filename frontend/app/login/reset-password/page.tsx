"use client"

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import Link from 'next/link';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';

export default function ResetPasswordPage() {
    const [email, setEmail] = useState("");
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    useEffect(() => {
        const storedEmail = sessionStorage.getItem('recovery_email');
        const storedQuestion = sessionStorage.getItem('recovery_question');
        if (!storedEmail || !storedQuestion) {
            router.push('/login/forgot-password');
            return;
        }
        setEmail(storedEmail);
        setQuestion(storedQuestion);
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const res = await fetch('/api/auth/recover-verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email,
                    answer,
                    new_password: newPassword
                })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Reset failed');

            toast.success("Password reset successfully!");
            sessionStorage.removeItem('recovery_email');
            sessionStorage.removeItem('recovery_question');
            router.push('/login');
        } catch (err: any) {
            toast.error(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen">
            <Card className="w-[400px]">
                <CardHeader>
                    <CardTitle>Reset Password</CardTitle>
                    <CardDescription>Answer your security question to set a new password.</CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label>Security Question</Label>
                            <div className="p-3 bg-muted rounded-md text-sm italic">
                                {question}
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="answer">Your Answer</Label>
                            <Input
                                id="answer"
                                type="password"
                                value={answer}
                                onChange={(e) => setAnswer(e.target.value)}
                                required
                            />
                        </div>
                        <div className="space-y-2 pt-2 border-t">
                            <Label htmlFor="newPassword">New Password</Label>
                            <Input
                                id="newPassword"
                                type="password"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                required
                            />
                        </div>
                    </CardContent>
                    <CardFooter className="flex flex-col space-y-2">
                        <Button className="w-full" type="submit" disabled={isLoading}>
                            {isLoading ? "Resetting..." : "Reset Password"}
                        </Button>
                        <div className="text-sm text-center text-muted-foreground">
                            Changed your mind? <Link href="/login" className="text-primary hover:underline">Back to Login</Link>
                        </div>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
