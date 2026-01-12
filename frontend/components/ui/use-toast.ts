export const useToast = () => {
    return {
        toast: ({ title, description, variant }: { title: string, description?: string, variant?: "default" | "destructive" | null }) => {
            console.log(`Toast: ${title} - ${description} [${variant}]`);
        }
    }
}
