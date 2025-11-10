
import React, { useState } from 'react';
import Calculator from './components/Calculator';
import ImageEditor from './components/ImageEditor';
import { CalculatorIcon, PhotoIcon, GithubIcon } from './components/Icons';

type Tab = 'calculator' | 'imageEditor';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('calculator');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'calculator':
        return <Calculator />;
      case 'imageEditor':
        return <ImageEditor />;
      default:
        return null;
    }
  };

  // FIX: Changed JSX.Element to React.ReactElement to resolve "Cannot find namespace 'JSX'" error.
  const TabButton: React.FC<{ tabName: Tab; label: string; icon: React.ReactElement }> = ({ tabName, label, icon }) => (
    <button
      onClick={() => setActiveTab(tabName)}
      className={`flex items-center justify-center w-full px-4 py-3 font-medium text-sm rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
        activeTab === tabName
          ? 'bg-blue-600 text-white shadow-lg'
          : 'bg-white text-gray-700 hover:bg-gray-200'
      }`}
    >
      {icon}
      <span className="ml-2">{label}</span>
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-blue-700">
              Dimensionador Pluvial & IA Studio
            </h1>
            <a href="https://github.com/google/genai-js" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-blue-600 transition-colors">
              <GithubIcon />
            </a>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4 sm:p-6 lg:p-8">
        <div className="mb-8 max-w-2xl mx-auto">
          <div className="grid grid-cols-2 gap-4 bg-gray-200 p-2 rounded-xl shadow-inner">
            <TabButton tabName="calculator" label="Calculadora de Calhas" icon={<CalculatorIcon />} />
            <TabButton tabName="imageEditor" label="Editor de Imagens AI" icon={<PhotoIcon />} />
          </div>
        </div>

        <div className="transition-opacity duration-500">
          {renderTabContent()}
        </div>
      </main>
      
      <footer className="text-center py-6 text-gray-500 text-sm">
        <p>Desenvolvido com React, TypeScript, Tailwind CSS e Gemini API.</p>
      </footer>
    </div>
  );
};

export default App;
