import { render, screen, fireEvent } from '@testing-library/react';
import GeoControls from '../../src/components/GeoControls';

describe('GeoControls', () => {
  const defaultProps = {
    enabled: false,
    onEnabledChange: jest.fn(),
    lat: 47.6062,
    lng: -122.3321,
    radius: 50,
    onLatChange: jest.fn(),
    onLngChange: jest.fn(),
    onRadiusChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders geo controls header', () => {
    render(<GeoControls {...defaultProps} />);
    expect(screen.getByText(/Geo-Radius Search/i)).toBeInTheDocument();
  });

  it('calls onEnabledChange when checkbox is toggled', () => {
    render(<GeoControls {...defaultProps} />);
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);
    expect(defaultProps.onEnabledChange).toHaveBeenCalledWith(true);
  });

  it('shows controls when enabled', () => {
    render(<GeoControls {...defaultProps} enabled={true} />);
    expect(screen.getByText(/City Presets:/i)).toBeInTheDocument();
    expect(screen.getByText(/Latitude:/i)).toBeInTheDocument();
    expect(screen.getByText(/Longitude:/i)).toBeInTheDocument();
  });

  it('hides controls when disabled', () => {
    render(<GeoControls {...defaultProps} enabled={false} />);
    expect(screen.queryByText(/City Presets:/i)).not.toBeInTheDocument();
  });

  it('displays current coordinates and radius', () => {
    render(<GeoControls {...defaultProps} enabled={true} />);
    expect(screen.getByDisplayValue('47.6062')).toBeInTheDocument();
    expect(screen.getByDisplayValue('-122.3321')).toBeInTheDocument();
    // Check for radius - the label and value are in separate elements
    expect(screen.getByText('Radius:', { exact: false })).toBeInTheDocument();
    // Verify the radius value is displayed (will appear in multiple places)
    const radiusTexts = screen.getAllByText(/50 km/i);
    expect(radiusTexts.length).toBeGreaterThan(0);
  });

  it('calls onLatChange when latitude input changes', () => {
    render(<GeoControls {...defaultProps} enabled={true} />);
    const latInput = screen.getByDisplayValue('47.6062');
    fireEvent.change(latInput, { target: { value: '48.0' } });
    expect(defaultProps.onLatChange).toHaveBeenCalledWith(48.0);
  });

  it('calls onLngChange when longitude input changes', () => {
    render(<GeoControls {...defaultProps} enabled={true} />);
    const lngInput = screen.getByDisplayValue('-122.3321');
    fireEvent.change(lngInput, { target: { value: '-120.0' } });
    expect(defaultProps.onLngChange).toHaveBeenCalledWith(-120.0);
  });

  it('calls onRadiusChange when radius slider changes', () => {
    render(<GeoControls {...defaultProps} enabled={true} />);
    const radiusSlider = screen.getByRole('slider');
    fireEvent.change(radiusSlider, { target: { value: '75' } });
    expect(defaultProps.onRadiusChange).toHaveBeenCalledWith(75);
  });

  it('renders city preset dropdown', () => {
    render(<GeoControls {...defaultProps} enabled={true} />);
    const dropdown = screen.getByRole('combobox');
    expect(dropdown).toBeInTheDocument();
    // Check for a city in the options
    expect(screen.getByText(/Seattle, WA/i)).toBeInTheDocument();
  });

  it('renders Use My Location button', () => {
    render(<GeoControls {...defaultProps} enabled={true} />);
    expect(screen.getByRole('button', { name: /Use My Location/i })).toBeInTheDocument();
  });

  it('displays info message when enabled', () => {
    render(<GeoControls {...defaultProps} enabled={true} />);
    // Use more specific query for the info message
    expect(screen.getByText(/Searching within 50 km of/i)).toBeInTheDocument();
  });

  it('handles city preset selection', () => {
    render(<GeoControls {...defaultProps} enabled={true} />);
    const dropdown = screen.getByRole('combobox');

    // Select Seattle (index 0)
    fireEvent.change(dropdown, { target: { value: '0' } });

    // Should call onLatChange and onLngChange with Seattle coordinates
    expect(defaultProps.onLatChange).toHaveBeenCalled();
    expect(defaultProps.onLngChange).toHaveBeenCalled();
  });
});
