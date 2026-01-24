"use client"

import { useState } from 'react';
import { useAuth } from '@/components/providers/auth-context';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import Link from 'next/link';
import { toast } from 'sonner';
import { register } from '@/lib/api';

export default function RegisterPage() {
    const { login } = useAuth();
    const [formData, setFormData] = useState({
        email: "",
        password: "",
        full_name: "",
        security_question: "",
        security_answer: ""
    });
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            // 1. Register User
            await register(formData);
            toast.success("Account created!");

            // 2. Auto Login
            await login({
                email: formData.email,
                password: formData.password
            });
            // Redirect handled in login()
        } catch (err: any) {
            toast.error(err.message || "Registration failed");
            setIsLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.id]: e.target.value });
    }

    return (
        <div className="flex items-center justify-center min-h-screen py-10">
            <Card className="w-[400px]">
                <CardHeader>
                    <CardTitle>Sign Up</CardTitle>
                    <CardDescription>Create your account to start trading.</CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="full_name">Full Name</Label>
                            <Input id="full_name" value={formData.full_name} onChange={handleChange} required />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input id="email" type="email" placeholder="m@example.com" value={formData.email} onChange={handleChange} required />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input id="password" type="password" value={formData.password} onChange={handleChange} required />
                        </div>
                        <div className="pt-4 border-t">
                            <p className="text-sm font-medium mb-2">Security Question (For Recovery)</p>
                            <div className="space-y-2">
                                <Label htmlFor="security_question">Question</Label>
                                <Input id="security_question" placeholder="e.g. First pet's name" value={formData.security_question} onChange={handleChange} required />
                            </div>
                            <div className="space-y-2 mt-2">
                                <Label htmlFor="security_answer">Answer</Label>
                                <Input id="security_answer" type="password" value={formData.security_answer} onChange={handleChange} required />
                            </div>
                        </div>
                    </CardContent>
                    <CardFooter className="flex flex-col space-y-2 mt-2">
                        <Button className="w-full" type="submit" disabled={isLoading}>
                            {isLoading ? "Creating Account..." : "Sign Up"}
                        </Button>
                        <div className="text-sm text-center text-muted-foreground">
                            Already have an account? <Link href="/login" className="text-primary hover:underline">Login</Link>
                        </div>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
