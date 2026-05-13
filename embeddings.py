import logging
import numpy as np
from typing import List, Dict, Tuple
from io import BytesIO
import requests
from PIL import Image
import torch
import open_clip
from config import Config

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Gerador de embeddings de imagens usando CLIP"""
    
    def __init__(self, model_name: str = None):
        """
        Inicializa o gerador de embeddings
        
        Args:
            model_name: Nome do modelo CLIP (padrão: ViT-B-32)
        """
        # open-clip usa ViT-B-32 em vez de ViT-B/32
        self.model_name = (model_name or Config.EMBEDDING_MODEL).replace("/", "-")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Usando device: {self.device}")
        
        try:
            logger.info(f"Carregando modelo CLIP: {self.model_name}")
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                self.model_name,
                pretrained="openai",
                device=self.device
            )
            self.model.eval()
            logger.info("Modelo carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise
    
    def download_image(self, url: str) -> Image.Image:
        """
        Faz download de uma imagem pela URL
        
        Args:
            url: URL da imagem
        
        Returns:
            Imagem PIL
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGB")
            return image
        except Exception as e:
            logger.warning(f"Erro ao fazer download da imagem {url}: {e}")
            return None
    
    def generate_embedding(self, image: Image.Image) -> np.ndarray:
        """
        Gera embedding de uma imagem
        
        Args:
            image: Imagem PIL
        
        Returns:
            Vetor de embedding (numpy array)
        """
        try:
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                # Normalizar o embedding
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                embedding = image_features.cpu().numpy().squeeze()
            
            return embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return None
    
    def process_products_batch(self, products: List[dict]) -> Tuple[List[dict], np.ndarray]:
        """
        Processa lista de produtos e gera embeddings
        
        Args:
            products: Lista de dicts com url e dados de produto
        
        Returns:
            Tupla (lista de dicts de produto, array de embeddings)
        """
        embeddings_list = []
        products_list = []
        total = len(products)
        
        for idx, product in enumerate(products, 1):
            url = product['url']
            logger.info(f"Processando {idx}/{total}: {url}")
            
            image = self.download_image(url)
            if image is None:
                logger.warning(f"Pulando: {url}")
                continue
            
            embedding = self.generate_embedding(image)
            if embedding is not None:
                embeddings_list.append(embedding)
                products_list.append(product)
                logger.info(f"✓ OK")
            else:
                logger.warning(f"✗ Falha no embedding: {url}")
        
        logger.info(f"Total: {len(embeddings_list)}/{total}")
        return products_list, np.array(embeddings_list)
    
    def save_embeddings_with_data(self, products: List[dict], embeddings: np.ndarray, filepath: str):
        """
        Salva embeddings e dados de produto em arquivo NPZ
        
        Args:
            products: Lista de dicts com dados de produto
            embeddings: Array de embeddings
            filepath: Caminho do arquivo
        """
        try:
            import json
            np.savez(
                filepath,
                embeddings=embeddings,
                products_json=json.dumps(products)
            )
            logger.info(f"Dados salvos em: {filepath}")
        except Exception as e:
            logger.error(f"Erro ao salvar: {e}")
    
    def load_embeddings_with_data(self, filepath: str) -> Tuple[List[dict], np.ndarray]:
        """
        Carrega embeddings e dados de produto
        
        Args:
            filepath: Caminho do arquivo
        
        Returns:
            Tupla (lista de dicts de produto, array de embeddings)
        """
        try:
            import json
            data = np.load(filepath, allow_pickle=True)
            embeddings = data['embeddings']
            products = json.loads(str(data['products_json']))
            logger.info(f"Carregados: {len(products)} produtos")
            return products, embeddings
        except Exception as e:
            logger.error(f"Erro ao carregar: {e}")
            return [], np.array([])
