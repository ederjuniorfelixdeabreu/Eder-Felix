
import React, { useState, useRef } from 'react';
import { editImageWithGemini, blobToBase64 } from '../services/geminiService';

const ImageEditor: React.FC = () => {
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [originalImageFile, setOriginalImageFile] = useState<File | null>(null);
  const [editedImage, setEditedImage] = useState<string | null>(null);
  const [prompt, setPrompt] = useState<string>('Adicione um filtro retrô e um ar de mistério.');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setOriginalImageFile(file);
      setOriginalImage(URL.createObjectURL(file));
      setEditedImage(null);
      setError(null);
    }
  };

  const handleGenerateClick = async () => {
    if (!originalImageFile || !prompt) {
      setError('Por favor, carregue uma imagem e insira um prompt.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setEditedImage(null);

    try {
      const base64Image = await blobToBase64(originalImageFile);
      const generatedBase64 = await editImageWithGemini(base64Image, originalImageFile.type, prompt);
      setEditedImage(`data:image/png;base64,${generatedBase64}`);
    } catch (e) {
      if (e instanceof Error) {
        setError(e.message);
      } else {
        setError('Ocorreu um erro desconhecido.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-lg">
        <div className="text-center mb-8">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-800">Editor de Imagens com Gemini AI</h2>
            <p className="text-gray-600 mt-2">Use o poder da IA para editar suas imagens com simples comandos de texto.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center mb-6">
            <div className="flex flex-col items-center">
                <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    ref={fileInputRef}
                    className="hidden"
                />
                <button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full sm:w-auto bg-blue-100 text-blue-700 font-semibold py-3 px-6 rounded-lg hover:bg-blue-200 transition duration-300 mb-4"
                >
                    {originalImage ? 'Trocar Imagem' : 'Carregar Imagem'}
                </button>
            </div>
            <div>
                 <input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Ex: Adicione um efeito de aquarela"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </div>
        </div>
         <div className="text-center mb-8">
            <button
                onClick={handleGenerateClick}
                disabled={isLoading || !originalImage}
                className="bg-blue-600 text-white font-bold py-3 px-10 rounded-lg hover:bg-blue-700 transition duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed shadow-lg"
            >
                {isLoading ? 'Gerando...' : 'Gerar Edição'}
            </button>
        </div>

        {error && <div className="text-center p-4 bg-red-100 text-red-700 rounded-lg mb-6">{error}</div>}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <ImageDisplay title="Original" imageUrl={originalImage} />
          <ImageDisplay title="Editada com Gemini" imageUrl={editedImage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
};

interface ImageDisplayProps {
  title: string;
  imageUrl: string | null;
  isLoading?: boolean;
}

const ImageDisplay: React.FC<ImageDisplayProps> = ({ title, imageUrl, isLoading }) => (
  <div className="flex flex-col items-center">
    <h3 className="text-lg font-semibold text-gray-700 mb-3">{title}</h3>
    <div className="w-full aspect-w-1 aspect-h-1 bg-gray-200 rounded-xl flex items-center justify-center overflow-hidden shadow-inner">
      {isLoading && (
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      )}
      {!isLoading && imageUrl && (
        <img src={imageUrl} alt={title} className="w-full h-full object-cover" />
      )}
      {!isLoading && !imageUrl && (
        <span className="text-gray-500">Sua imagem aparecerá aqui</span>
      )}
    </div>
  </div>
);

export default ImageEditor;
