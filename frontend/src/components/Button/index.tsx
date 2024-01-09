import React from 'react';
import cx from 'classnames';

interface ButtonProps{
    children: React.ReactNode
    onClick(): void
    type?: 'button' | 'submit' | 'reset'
    [x: string]: any
}

const Button: React.FC<ButtonProps> = ({
  children, onClick, className,
}) => {
  const classes = cx(`
    bg-blue-100
    hover:bg-blue-200
    px-4
    py-2
    rounded-b
`,
  {
    [className]: className,
  });

  return (
    <button
      type="button"
      onClick={onClick}
      className={classes}
    >
      {children}
    </button>
  );
};

export default Button;
