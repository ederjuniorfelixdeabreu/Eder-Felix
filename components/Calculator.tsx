import React, { useState, useMemo } from 'react';
import { CalculatorInput, CalculatorOutput } from '../types';
import { calculateGutterAndDownspout } from '../services/calculationService';
import { RAINFALL_INTENSITY_DATA, GUTTER_MATERIALS, STATES } from '../constants';

const initialInputs: CalculatorInput = {
  roofWidth: 10,
  roofLength: 15,
  roofSlope: 30,
  state: 'SP',
  city: 'São Paulo (Mirante Santana)',
  gutterMaterial: 'Chapa Metálica',
  gutterShape: 'rectangular',
  downspoutCount: 2,
  buildingHeight: 3,
};

const Calculator: React.FC = () => {
  const [inputs, setInputs] = useState<CalculatorInput>(initialInputs);
  const [results, setResults] = useState<CalculatorOutput | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const cities = useMemo(() => {
    return inputs.state ? Object.keys(RAINFALL_INTENSITY_DATA[inputs.state] || {}).sort() : [];
  }, [inputs.state]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setInputs(prev => {
        const newInputs = {...prev, [name]: name === 'gutterShape' ? value : parseFloat(value) || value };
        if (name === 'state') {
            const newCities = Object.keys(RAINFALL_INTENSITY_DATA[value] || {}).sort();
            newInputs.city = newCities[0] || '';
        }
        return newInputs;
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setResults(null);
    setTimeout(() => { // Simulate processing time for better UX
      const output = calculateGutterAndDownspout(inputs);
      setResults(output);
      setIsLoading(false);
    }, 500);
  };
  
  const roofHeight = (inputs.roofWidth * (inputs.roofSlope / 100));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
      <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-lg">
        <h2 className="text-2xl font-bold mb-6 text-gray-800 border-b pb-4">Parâmetros de Entrada</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          
          {/* Input Fields */}
          <InputField label="Largura do Telhado (m)" name="roofWidth" type="number" value={inputs.roofWidth} onChange={handleInputChange} />
          <InputField label="Comprimento do Telhado (m)" name="roofLength" type="number" value={inputs.roofLength} onChange={handleInputChange} />
          <InputField label="Inclinação do Telhado (%)" name="roofSlope" type="number" value={inputs.roofSlope} onChange={handleInputChange} />
          <SelectField label="Estado (UF)" name="state" value={inputs.state} onChange={handleInputChange} options={STATES} />
          <SelectField label="Cidade" name="city" value={inputs.city} onChange={handleInputChange} options={cities} />
          <SelectField label="Material da Calha" name="gutterMaterial" value={inputs.gutterMaterial} onChange={handleInputChange} options={Object.keys(GUTTER_MATERIALS)} />
          <SelectField label="Formato da Calha" name="gutterShape" value={inputs.gutterShape} onChange={handleInputChange} options={[{value: 'rectangular', label: 'Retangular'}, {value: 'semicircular', label: 'Semicircular'}]} />
          <InputField label="Nº de Dutos de Descida" name="downspoutCount" type="number" value={inputs.downspoutCount} onChange={handleInputChange} min={2} />

          <button type="submit" className="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition duration-300 shadow-md disabled:bg-blue-300" disabled={isLoading}>
            {isLoading ? 'Calculando...' : 'Calcular Dimensionamento'}
          </button>
        </form>
      </div>

      <div className="lg:col-span-3">
        {isLoading && <div className="flex justify-center items-center h-full"><div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div></div>}
        {results && (
          <div className="space-y-8">
            {results.downspoutWarning && <div className="p-4 bg-red-100 border-l-4 border-red-500 text-red-700 rounded-lg shadow-md"><p className="font-bold">Aviso!</p><p>{results.downspoutWarning}</p></div>}
            
            <div className="bg-white p-6 rounded-2xl shadow-lg">
              <h2 className="text-2xl font-bold mb-4 text-gray-800 border-b pb-4">Resultados</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-center">
                <ResultCard label="Vazão de Projeto" value={results.flowRate.toFixed(2)} unit="L/min" />
                <ResultCard label="Área de Contribuição" value={results.contributionArea.toFixed(2)} unit="m²" />
                <ResultCard label="Intensidade Pluviométrica" value={results.rainfallIntensity.toFixed(2)} unit="mm/h" />
                <ResultCard label="Largura da Calha" value={results.gutterWidth.toFixed(2)} unit="cm" />
                <ResultCard label="Altura da Água (Útil)" value={results.waterDepth.toFixed(2)} unit="cm" />
                <ResultCard label="Altura Total da Calha" value={results.totalGutterHeight.toFixed(2)} unit="cm" />
                <ResultCard label="Diâmetro do Duto" value={results.downspoutDiameter.toFixed(0)} unit="mm" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Roof Diagram */}
                <div className="bg-white p-6 rounded-2xl shadow-lg">
                    <h3 className="font-bold text-lg mb-4 text-center">Esquema do Telhado</h3>
                    <div className="relative aspect-video bg-gray-100 rounded-lg p-4 flex flex-col justify-center items-center font-mono text-sm">
                        <div className="relative border-2 border-dashed border-gray-400 w-full" style={{paddingBottom: '80%'}}>
                             <div className="absolute top-1/2 left-0 w-full border-t border-gray-400"></div>
                             <div className="absolute top-0 left-0 w-1/2 h-full bg-blue-200/50 -skew-y-6 origin-bottom-left"></div>
                             <div className="absolute top-0 right-0 w-1/2 h-full bg-blue-300/50 skew-y-6 origin-bottom-right"></div>
                        </div>
                         <div className="absolute -bottom-2 text-blue-700">{inputs.roofWidth.toFixed(2)} m (largura)</div>
                         <div className="absolute top-1/2 -right-12 text-blue-700 rotate-90">{inputs.roofLength.toFixed(2)} m (compr.)</div>
                         <div className="absolute top-1 right-1 text-blue-700">{inputs.roofSlope}% incl.</div>
                    </div>
                </div>

                {/* Gutter Diagram */}
                <div className="bg-white p-6 rounded-2xl shadow-lg">
                    <h3 className="font-bold text-lg mb-4 text-center">Esquema da Calha</h3>
                    <div className="relative aspect-video bg-gray-100 rounded-lg p-4 flex justify-center items-end font-mono text-sm">
                        {inputs.gutterShape === 'rectangular' ? (
                            (() => {
                                const maxDimension = 160; // max dimension in pixels
                                let displayWidth, displayHeight;

                                if (results.gutterWidth <= 0 || results.totalGutterHeight <= 0) {
                                    displayWidth = 120;
                                    displayHeight = 60;
                                } else if (results.gutterWidth >= results.totalGutterHeight) {
                                    displayWidth = maxDimension;
                                    displayHeight = (results.totalGutterHeight / results.gutterWidth) * maxDimension;
                                } else {
                                    displayHeight = maxDimension;
                                    displayWidth = (results.gutterWidth / results.totalGutterHeight) * maxDimension;
                                }

                                return (
                                    <div className="relative border-l-4 border-r-4 border-b-4 border-gray-600" style={{ width: `${displayWidth}px`, height: `${displayHeight}px` }}>
                                        <div className="absolute bottom-0 left-0 w-full bg-blue-400" style={{ height: `${(results.waterDepth / results.totalGutterHeight * 100).toFixed(2)}%` }}></div>
                                        <span className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-blue-700 whitespace-nowrap">{results.gutterWidth.toFixed(1)}cm</span>
                                        <span className="absolute top-1/2 -right-12 -translate-y-1/2 text-blue-700 whitespace-nowrap">{results.totalGutterHeight.toFixed(1)}cm</span>
                                        <span className="absolute text-white text-xs left-1/2 -translate-x-1/2" style={{bottom: `${(results.waterDepth / results.totalGutterHeight * 50).toFixed(2)}%`}}>{results.waterDepth.toFixed(1)}cm</span>
                                    </div>
                                );
                            })()
                        ) : (
                             <div className="relative w-48 h-24 border-b-4 border-l-4 border-r-4 border-gray-600 rounded-b-full flex justify-center items-end">
                                <div className="absolute bottom-0 w-full h-full bg-blue-400 rounded-b-full overflow-hidden">
                                     <div className="absolute bottom-0 w-full bg-gray-100" style={{height: `${(1 - (results.waterDepth / (results.gutterWidth/2) ))*100}%`}}></div>
                                </div>
                                <span className="absolute -bottom-5 text-blue-700">{results.gutterWidth.toFixed(1)}cm (diâmetro)</span>
                                <span className="absolute text-white text-xs bottom-1">{results.waterDepth.toFixed(1)}cm (altura)</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Sub-components for inputs and results
const InputField: React.FC<{label: string, name: string, type: string, value: string | number, onChange: (e: React.ChangeEvent<HTMLInputElement>) => void, min?: number}> = 
({ label, name, type, value, onChange, min }) => (
  <div>
    <label htmlFor={name} className="block text-sm font-medium text-gray-700">{label}</label>
    <input type={type} id={name} name={name} value={value} onChange={onChange} min={min} step="any" required
           className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
  </div>
);

const SelectField: React.FC<{label: string, name: string, value: string, onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void, options: (string | {value: string, label: string})[]}> = 
({ label, name, value, onChange, options }) => (
    <div>
        <label htmlFor={name} className="block text-sm font-medium text-gray-700">{label}</label>
        <select id={name} name={name} value={value} onChange={onChange} required
                className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
            {options.map(opt => (
                typeof opt === 'string' ? 
                <option key={opt} value={opt}>{opt}</option> :
                <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
        </select>
    </div>
);

const ResultCard: React.FC<{label: string, value: string, unit: string}> = ({ label, value, unit }) => (
  <div className="bg-gray-100 p-4 rounded-lg">
    <p className="text-sm text-gray-500">{label}</p>
    <p className="text-2xl font-bold text-blue-600">{value} <span className="text-base font-normal text-gray-600">{unit}</span></p>
  </div>
);

export default Calculator;