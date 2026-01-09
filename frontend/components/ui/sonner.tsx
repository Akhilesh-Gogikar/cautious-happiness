"use client";

import { Toaster as Sonner } from "sonner";

type ToasterProps = React.ComponentProps<typeof Sonner>;

const Toaster = ({ ...props }: ToasterProps) => {
    return (
        <Sonner
            theme="dark"
            className="toaster group"
            toastOptions={{
                classNames: {
                    toast:
                        "group toast group-[.toaster]:bg-green-950 group-[.toaster]:text-green-500 group-[.toaster]:border-green-900 group-[.toaster]:shadow-lg group-[.toaster]:font-mono",
                    description: "group-[.toast]:text-green-600",
                    actionButton:
                        "group-[.toast]:bg-green-500 group-[.toast]:text-black",
                    cancelButton:
                        "group-[.toast]:bg-green-100 group-[.toast]:text-green-500",
                },
            }}
            {...props}
        />
    );
};

export { Toaster };
