import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { GradientButton } from '../../components/ui/GradientButton';

describe('GradientButton', () => {
  it('renders children', () => {
    render(<GradientButton>Click me</GradientButton>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<GradientButton onClick={handleClick}>Click me</GradientButton>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<GradientButton isLoading>Click me</GradientButton>);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('is disabled when loading', () => {
    render(<GradientButton isLoading>Click me</GradientButton>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
