import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FormInput from '../FormInput';

describe('FormInput Component', () => {
  it('renders with label', () => {
    render(<FormInput label="Email" />);
    
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
  });

  it('renders without label', () => {
    render(<FormInput placeholder="Enter text" />);
    
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
  });

  it('shows required indicator when required', () => {
    render(<FormInput label="Required Field" required />);
    
    expect(screen.getByText('*')).toBeInTheDocument();
    expect(screen.getByText('*')).toHaveClass('form-input-required');
  });

  it('displays error message', () => {
    render(<FormInput label="Email" error="Invalid email" />);
    
    const input = screen.getByLabelText('Email');
    const errorMessage = screen.getByText('Invalid email');
    
    expect(input).toHaveClass('form-input-error');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(errorMessage).toHaveClass('form-input-error-text');
    expect(errorMessage).toHaveAttribute('role', 'alert');
  });

  it('displays helper text when no error', () => {
    render(<FormInput label="Password" helperText="At least 8 characters" />);
    
    const helperText = screen.getByText('At least 8 characters');
    expect(helperText).toHaveClass('form-input-helper-text');
  });

  it('prioritizes error over helper text', () => {
    render(
      <FormInput 
        label="Password" 
        error="Password too short" 
        helperText="At least 8 characters" 
      />
    );
    
    expect(screen.getByText('Password too short')).toBeInTheDocument();
    expect(screen.queryByText('At least 8 characters')).not.toBeInTheDocument();
  });

  it('handles input changes', async () => {
    const user = userEvent.setup();
    const handleChange = jest.fn();
    
    render(<FormInput label="Name" onChange={handleChange} />);
    
    const input = screen.getByLabelText('Name');
    await user.type(input, 'John Doe');
    
    expect(handleChange).toHaveBeenCalledTimes(8); // One for each character
    expect(input).toHaveValue('John Doe');
  });

  it('renders as full width when fullWidth prop is true', () => {
    render(<FormInput label="Full Width" fullWidth />);
    
    const input = screen.getByLabelText('Full Width');
    expect(input).toHaveClass('form-input-full-width');
  });

  it('applies custom className', () => {
    render(<FormInput label="Custom" className="custom-input" />);
    
    const input = screen.getByLabelText('Custom');
    expect(input).toHaveClass('custom-input');
  });

  it('generates unique id when not provided', () => {
    const { rerender } = render(<FormInput label="First" />);
    const firstInput = screen.getByLabelText('First');
    const firstId = firstInput.getAttribute('id');
    
    rerender(<FormInput label="Second" />);
    const secondInput = screen.getByLabelText('Second');
    const secondId = secondInput.getAttribute('id');
    
    expect(firstId).toBeTruthy();
    expect(secondId).toBeTruthy();
    expect(firstId).not.toBe(secondId);
  });

  it('uses provided id', () => {
    render(<FormInput label="Custom ID" id="custom-input-id" />);
    
    const input = screen.getByLabelText('Custom ID');
    expect(input).toHaveAttribute('id', 'custom-input-id');
  });

  it('associates label with input correctly', () => {
    render(<FormInput label="Associated" id="test-input" />);
    
    const label = screen.getByText('Associated');
    const input = screen.getByLabelText('Associated');
    
    expect(label).toHaveAttribute('for', 'test-input');
    expect(input).toHaveAttribute('id', 'test-input');
  });

  it('sets aria-describedby for error', () => {
    render(<FormInput label="Error Field" error="Error message" id="error-input" />);
    
    const input = screen.getByLabelText('Error Field');
    expect(input).toHaveAttribute('aria-describedby', 'error-input-error');
  });

  it('sets aria-describedby for helper text', () => {
    render(<FormInput label="Helper Field" helperText="Helper message" id="helper-input" />);
    
    const input = screen.getByLabelText('Helper Field');
    expect(input).toHaveAttribute('aria-describedby', 'helper-input-helper');
  });

  it('forwards additional props to input', () => {
    render(
      <FormInput 
        label="Test Input" 
        type="email" 
        placeholder="Enter email"
        disabled
        data-testid="test-input"
      />
    );
    
    const input = screen.getByTestId('test-input');
    expect(input).toHaveAttribute('type', 'email');
    expect(input).toHaveAttribute('placeholder', 'Enter email');
    expect(input).toBeDisabled();
  });

  it('supports ref forwarding', () => {
    const ref = React.createRef();
    render(<FormInput label="Ref Test" ref={ref} />);
    
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
    expect(ref.current).toBe(screen.getByLabelText('Ref Test'));
  });
});
