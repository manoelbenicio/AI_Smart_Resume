"use client";

import { useCallback, useState } from "react";
import { UploadCloud, File, X } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface DropZoneProps {
    onFileSelect: (file: File | null) => void;
    accept?: string;
    maxSizeMB?: number;
}

export function DropZone({ onFileSelect, accept = ".pdf,.docx", maxSizeMB = 5 }: DropZoneProps) {
    const [isDragActive, setIsDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setIsDragActive(true);
        } else if (e.type === "dragleave") {
            setIsDragActive(false);
        }
    }, []);

    const validateAndSetFile = (file: File) => {
        setError(null);
        const sizeMB = file.size / 1024 / 1024;

        if (sizeMB > maxSizeMB) {
            setError(`File size exceeds ${maxSizeMB}MB limit.`);
            return;
        }

        // Basic extension check
        const extension = "." + file.name.split(".").pop()?.toLowerCase();
        if (!accept.split(",").includes(extension)) {
            setError(`Only ${accept} files are supported.`);
            return;
        }

        setSelectedFile(file);
        onFileSelect(file);
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            validateAndSetFile(e.dataTransfer.files[0]);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            validateAndSetFile(e.target.files[0]);
        }
    };

    const removeFile = (e: React.MouseEvent) => {
        e.stopPropagation();
        setSelectedFile(null);
        onFileSelect(null);
        setError(null);
    };

    return (
        <div className="w-full">
            <div
                className={cn(
                    "glass-panel relative flex flex-col items-center justify-center w-full h-48 rounded-xl border-2 border-dashed transition-all duration-200 cursor-pointer overflow-hidden",
                    isDragActive
                        ? "border-primary bg-primary/5 scale-[1.01]"
                        : "border-muted-foreground/30 hover:border-primary/50 hover:bg-muted/30"
                )}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    accept={accept}
                    onChange={handleChange}
                />

                {selectedFile ? (
                    <div className="flex flex-col items-center justify-center space-y-3 z-0 w-full px-4">
                        <div className="p-3 bg-primary/20 rounded-full text-primary">
                            <File className="w-8 h-8" />
                        </div>
                        <div className="flex flex-col items-center max-w-full">
                            <p className="text-sm font-medium text-foreground truncate max-w-full">
                                {selectedFile.name}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                        </div>
                        <button
                            onClick={removeFile}
                            className="absolute top-3 right-3 p-1.5 bg-background/50 hover:bg-destructive/20 text-muted-foreground hover:text-destructive rounded-full transition-colors z-20"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center space-y-4 z-0">
                        <div className={cn(
                            "p-4 rounded-full transition-colors duration-200",
                            isDragActive ? "bg-primary/20 text-primary" : "bg-muted text-muted-foreground"
                        )}>
                            <UploadCloud className="w-8 h-8" />
                        </div>
                        <div className="flex flex-col items-center">
                            <p className="text-sm font-medium text-foreground">
                                <span className="text-primary hover:underline">Click to upload</span> or drag and drop
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                                PDF or DOCX (max {maxSizeMB}MB)
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {error && (
                <p className="text-sm text-destructive mt-2 animate-in slide-in-from-top-1">
                    {error}
                </p>
            )}
        </div>
    );
}
