import * as React from "react"

const AlertDialog = ({ children }: any) => <div>{children}</div>
const AlertDialogTrigger = ({ children }: any) => <button>{children}</button>
const AlertDialogContent = ({ children }: any) => <div>{children}</div>
const AlertDialogHeader = ({ children }: any) => <div>{children}</div>
const AlertDialogTitle = ({ children }: any) => <h3>{children}</h3>
const AlertDialogDescription = ({ children }: any) => <p>{children}</p>
const AlertDialogFooter = ({ children }: any) => <div>{children}</div>
const AlertDialogAction = ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>
const AlertDialogCancel = ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>

export {
    AlertDialog,
    AlertDialogTrigger,
    AlertDialogContent,
    AlertDialogHeader,
    AlertDialogFooter,
    AlertDialogTitle,
    AlertDialogDescription,
    AlertDialogAction,
    AlertDialogCancel,
}
