import React from 'react';
import './CodeBlock.css';

interface CodeBlockProps {
  code: string;
  language?: string;
  label?: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ code, language = 'text', label }) => {
  return (
    <div className="code-block-wrapper">
      {label && <div className="code-block-label">{label}:</div>}
      <pre className={`code-block code-block-${language}`}>
        <code>{code}</code>
      </pre>
    </div>
  );
};
