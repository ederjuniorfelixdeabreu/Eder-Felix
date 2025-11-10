
export interface CalculatorInput {
  roofWidth: number;
  roofLength: number;
  roofSlope: number;
  state: string;
  city: string;
  gutterMaterial: string;
  gutterShape: 'rectangular' | 'semicircular';
  downspoutCount: number;
  buildingHeight: number;
}

export interface CalculatorOutput {
  flowRate: number;
  contributionArea: number;
  rainfallIntensity: number;
  gutterWidth: number;
  waterDepth: number;
  totalGutterHeight: number;
  downspoutDiameter: number;
  downspoutWarning: string | null;
}

export interface RainfallData {
  [state: string]: {
    [city: string]: number;
  };
}
