
import { CalculatorInput, CalculatorOutput } from '../types';
import { RAINFALL_INTENSITY_DATA, GUTTER_MATERIALS, STANDARD_DOWNSPOUT_DIAMETERS } from '../constants';

// Based on Plínio Tomaz, Tabela 4.5
const getInitialGutterWidth = (roofLength: number): number => {
  if (roofLength <= 5) return 0.15;
  if (roofLength <= 10) return 0.20;
  if (roofLength <= 15) return 0.30;
  if (roofLength <= 20) return 0.40;
  if (roofLength <= 25) return 0.50;
  return 0.60;
};

// NBR 10844 Tabela 3 - for semi-circular gutters (n=0.011)
const semiCircularCapacities: { [diameter: number]: { [slope: string]: number } } = {
  100: { '0.005': 130, '0.01': 183, '0.02': 256 },
  125: { '0.005': 236, '0.01': 333, '0.02': 466 },
  150: { '0.005': 384, '0.01': 541, '0.02': 757 },
  200: { '0.005': 829, '0.01': 1167, '0.02': 1634 },
};

export const calculateGutterAndDownspout = (input: CalculatorInput): CalculatorOutput | null => {
  try {
    const { roofWidth, roofLength, roofSlope, state, city, gutterMaterial, gutterShape, downspoutCount, buildingHeight } = input;

    // 1. Rainfall Intensity (I)
    const rainfallIntensity = RAINFALL_INTENSITY_DATA[state]?.[city];
    if (!rainfallIntensity) throw new Error("Dados de chuva não encontrados para a cidade selecionada.");

    // 2. Contribution Area (A)
    const h = roofWidth * (roofSlope / 100);
    const contributionArea = (roofWidth + h / 2) * roofLength;

    // 3. Project Flow Rate (Q)
    const flowRate = (rainfallIntensity * contributionArea) / 60; // L/min

    // Gutter Sizing
    let gutterWidth = 0;
    let waterDepth = 0;
    let totalGutterHeight = 0;
    const gutterSlopeValue = 0.005; // Minimum 0.5% slope as per NBR 10844

    if (gutterShape === 'semicircular') {
        const materialN = (GUTTER_MATERIALS as any)[gutterMaterial];
        if (materialN !== 0.011) {
             // For simplicity, we only use the NBR table which is for n=0.011. A full implementation would use Manning's formula for all n.
             throw new Error("Cálculo para calhas semicirculares está disponível apenas para materiais com n=0,011 (Aço, PVC, etc).");
        }
        
        const possibleDiameters = Object.keys(semiCircularCapacities).map(Number).sort((a,b)=> a-b);
        let foundDiameter = 0;

        for (const diameter of possibleDiameters) {
            if(semiCircularCapacities[diameter][String(gutterSlopeValue)] >= flowRate) {
                foundDiameter = diameter;
                break;
            }
        }

        if (foundDiameter > 0) {
            gutterWidth = foundDiameter / 1000; // in m
            waterDepth = (foundDiameter / 2) / 1000; // in m
            totalGutterHeight = waterDepth * 1.3; // 30% freeboard
        } else {
            throw new Error("Nenhuma calha semicircular padrão suporta a vazão. Considere dividir a área de captação.");
        }
    } else { // Rectangular
      gutterWidth = getInitialGutterWidth(roofLength);
      const n = (GUTTER_MATERIALS as any)[gutterMaterial];
      const Q_m3s = flowRate / 60000;

      // Iteratively find water depth 'y'
      let y = 0.001; // start with 1mm
      let calculated_Q = 0;
      while (calculated_Q < Q_m3s && y < gutterWidth * 2) { // safety break
        y += 0.001; // increment by 1mm
        const S = gutterWidth * y; // wetted area
        const P = gutterWidth + 2 * y; // wetted perimeter
        const Rh = S / P;
        calculated_Q = (1 / n) * S * Math.pow(Rh, 2/3) * Math.sqrt(gutterSlopeValue);
      }
      waterDepth = y;
      totalGutterHeight = Math.max(waterDepth * 1.3, waterDepth + 0.02); // 30% or 2cm freeboard
    }

    // Downspout Sizing
    const flowPerDownspout = flowRate / downspoutCount; // Q_duto in L/min
    const H = waterDepth * 1000; // water depth in mm
    
    let d_calc = 0;
    let downspoutWarning = null;

    // Using Frutuoso Dantas formulas
    // First, try assuming H/d > 1/3
    let d_initial = Math.sqrt(flowPerDownspout / (0.0039 * Math.pow(H, 0.5)));

    if(H / d_initial > 1/3) {
      d_calc = d_initial;
    } else {
      // Assumption was wrong, use the other formula H/d < 1/3
      d_calc = flowPerDownspout / (0.0116 * Math.pow(H, 1.5));
    }
    
    let downspoutDiameter = 0;
    for (const standard of STANDARD_DOWNSPOUT_DIAMETERS) {
      if (standard >= d_calc) {
        downspoutDiameter = standard;
        break;
      }
    }

    if (downspoutDiameter === 0) {
      downspoutWarning = "Nenhum diâmetro de duto atende a solicitação. Aumente a quantidade de dutos de descida ou revise o projeto.";
      downspoutDiameter = STANDARD_DOWNSPOUT_DIAMETERS[STANDARD_DOWNSPOUT_DIAMETERS.length-1];
    }


    return {
      contributionArea,
      rainfallIntensity,
      flowRate,
      gutterWidth: gutterWidth * 100, // cm
      waterDepth: waterDepth * 100, // cm
      totalGutterHeight: totalGutterHeight * 100, // cm
      downspoutDiameter,
      downspoutWarning,
    };

  } catch (error) {
    console.error("Calculation Error:", error);
    if (error instanceof Error) {
        return {
            contributionArea: 0, rainfallIntensity: 0, flowRate: 0, gutterWidth: 0, waterDepth: 0, 
            totalGutterHeight: 0, downspoutDiameter: 0, downspoutWarning: error.message 
        };
    }
    return null;
  }
};
