import React from 'react';
import { InlineMath, BlockMath } from 'react-katex';

const MathDisplay = ({ 
  expression, 
  displayMode = false, 
  errorColor = '#cc0000',
  className = '',
  style = {}
}) => {
  if (!expression) return null;

  const MathComponent = displayMode ? BlockMath : InlineMath;
  
  return (
    <div className={`math-display ${className}`} style={style}>
      <MathComponent 
        math={expression} 
        errorColor={errorColor}
        renderError={(error) => (
          <span style={{ color: errorColor, fontSize: '0.9em' }}>
            [Math Error: {error.message}]
          </span>
        )}
      />
    </div>
  );
};

export default MathDisplay;
