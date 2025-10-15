import React from "react";
import type { ReactNode } from "react";
import { Toaster } from "sonner";

interface ToastProviderProps {
    children: ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => (
    <>
        <Toaster />
        {children}
    </>
);