import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatusBadge } from '../../components/ui/StatusBadge';

describe('StatusBadge', () => {
  it('renders pending status', () => {
    render(<StatusBadge status="pending" />);
    expect(screen.getByText('Pending')).toBeInTheDocument();
  });

  it('renders complete status', () => {
    render(<StatusBadge status="complete" />);
    expect(screen.getByText('Complete')).toBeInTheDocument();
  });

  it('renders failed status', () => {
    render(<StatusBadge status="failed" />);
    expect(screen.getByText('Failed')).toBeInTheDocument();
  });

  it('renders generating status', () => {
    render(<StatusBadge status="generating" />);
    expect(screen.getByText('Generating...')).toBeInTheDocument();
  });
});
