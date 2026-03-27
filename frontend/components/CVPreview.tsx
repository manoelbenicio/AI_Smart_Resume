"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface CVPreviewProps {
    content: string;
}

export function CVPreview({ content }: CVPreviewProps) {
    return (
        <div className="w-full bg-background rounded-xl border p-8 shadow-sm overflow-auto max-h-[800px] prose prose-invert prose-headings:font-bold prose-h1:text-3xl prose-h2:text-xl prose-a:text-primary max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content}
            </ReactMarkdown>
        </div>
    );
}
