"""
OCR Handler for Pashto Documents

This module provides OCR capabilities specifically for Pashto scanned documents
using Tesseract OCR engine.
"""

import io
import base64
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import fitz  # PyMuPDF
import logging


class OCRHandler:
    """
    OCR handler for processing scanned Pashto PDF documents.
    """
    
    def __init__(self, languages: str = "eng+pus", config: str = None):
        """
        Initialize OCR handler.
        
        Args:
            languages: Tesseract languages to use (eng+pus for English+Pashto)
            config: Additional Tesseract configuration
        """
        self.languages = languages
        self.config = config or "--psm 6 -l " + languages
        self.logger = logging.getLogger(__name__)
        
        # OCR preprocessing parameters
        self.preprocess_params = {
            'resize_factor': 2.0,
            'denoise': True,
            'enhance_contrast': True,
            'binarize': False,  # Let Tesseract handle this
            'median_blur_kernel': 3,
            'gaussian_blur_kernel': 1,
        }
        
        # Supported image formats for OCR
        self.supported_formats = ['PNG', 'JPEG', 'TIFF', 'BMP']
    
    def extract_text_from_page(self, page: fitz.Page, 
                              preprocessing: bool = True) -> Dict[str, Any]:
        """
        Extract text from a PDF page using OCR.
        
        Args:
            page: PyMuPDF page object
            preprocessing: Whether to apply image preprocessing
            
        Returns:
            Dictionary containing OCR results
        """
        try:
            # Convert page to image
            image = self._page_to_image(page)
            
            if image is None:
                return {
                    'text': '',
                    'confidence': 0.0,
                    'method': 'ocr',
                    'error': 'Failed to convert page to image'
                }
            
            # Preprocess image if requested
            if preprocessing:
                image = self._preprocess_image(image)
            
            # Perform OCR
            result = self._perform_ocr(image)
            
            return result
            
        except Exception as e:
            self.logger.error(f"OCR error: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'ocr',
                'error': str(e)
            }
    
    def _page_to_image(self, page: fitz.Page, 
                      dpi: int = 300) -> Optional[np.ndarray]:
        """
        Convert PDF page to image array.
        
        Args:
            page: PyMuPDF page object
            dpi: Resolution for rendering
            
        Returns:
            Image as numpy array
        """
        try:
            # Render page to pixmap
            mat = fitz.Matrix(dpi/72, dpi/72)  # 72 DPI is PDF default
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Convert to numpy array
            return np.array(img)
            
        except Exception as e:
            self.logger.error(f"Error converting page to image: {str(e)}")
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert BGR to RGB if necessary
            if len(image.shape) == 3 and image.shape[2] == 3:
                # OpenCV uses BGR, PIL uses RGB
                if isinstance(image, np.ndarray):
                    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    img_rgb = image
            else:
                img_rgb = image
            
            # Convert to PIL Image for easier manipulation
            pil_image = Image.fromarray(img_rgb)
            
            # Resize if image is too small
            if min(pil_image.size) < 1000:
                scale_factor = 1000 / min(pil_image.size)
                new_size = (int(pil_image.width * scale_factor), 
                           int(pil_image.height * scale_factor))
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Apply noise reduction
            if self.preprocess_params['denoise']:
                # Convert to OpenCV format for noise reduction
                cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                
                # Apply median filter
                if self.preprocess_params['median_blur_kernel'] > 0:
                    kernel = self.preprocess_params['median_blur_kernel']
                    cv_image = cv2.medianBlur(cv_image, kernel)
                
                # Apply Gaussian blur
                if self.preprocess_params['gaussian_blur_kernel'] > 0:
                    kernel = self.preprocess_params['gaussian_blur_kernel']
                    cv_image = cv2.GaussianBlur(cv_image, (kernel, kernel), 0)
                
                # Convert back to PIL
                pil_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            
            # Enhance contrast
            if self.preprocess_params['enhance_contrast']:
                enhancer = ImageEnhance.Contrast(pil_image)
                pil_image = enhancer.enhance(1.5)  # Increase contrast by 50%
            
            # Convert back to numpy array
            processed_image = np.array(pil_image)
            
            return processed_image
            
        except Exception as e:
            self.logger.error(f"Error in image preprocessing: {str(e)}")
            return image  # Return original if preprocessing fails
    
    def _perform_ocr(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Perform OCR on preprocessed image.
        
        Args:
            image: Preprocessed image as numpy array
            
        Returns:
            Dictionary containing OCR results
        """
        try:
            # Convert to PIL Image for Tesseract
            pil_image = Image.fromarray(image)
            
            # Perform OCR with confidence data
            data = pytesseract.image_to_data(
                pil_image, 
                output_type=pytesseract.Output.DICT,
                config=self.config
            )
            
            # Extract text and confidence
            text_parts = []
            confidences = []
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = data['conf'][i]
                
                if text and conf > 0:  # Only include non-empty text with positive confidence
                    text_parts.append(text)
                    confidences.append(int(conf))
            
            extracted_text = ' '.join(text_parts)
            average_confidence = np.mean(confidences) if confidences else 0.0
            
            # Get detailed confidence information
            confidence_stats = {
                'average': average_confidence,
                'min': min(confidences) if confidences else 0,
                'max': max(confidences) if confidences else 0,
                'low_confidence_count': sum(1 for c in confidences if c < 50),
                'high_confidence_count': sum(1 for c in confidences if c >= 80)
            }
            
            return {
                'text': extracted_text,
                'confidence': average_confidence,
                'method': 'ocr',
                'confidence_stats': confidence_stats,
                'word_count': len(text_parts),
                'character_count': len(extracted_text)
            }
            
        except Exception as e:
            self.logger.error(f"OCR execution error: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'ocr',
                'error': str(e)
            }
    
    def extract_text_from_image_file(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from an image file using OCR.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary containing OCR results
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Preprocess image
            image_array = np.array(image)
            preprocessed_image = self._preprocess_image(image_array)
            
            # Perform OCR
            result = self._perform_ocr(preprocessed_image)
            result['source_file'] = image_path
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing image file {image_path}: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'ocr',
                'error': str(e),
                'source_file': image_path
            }
    
    def batch_ocr(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Perform OCR on multiple image files.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of OCR results
        """
        results = []
        
        self.logger.info(f"Starting batch OCR for {len(image_paths)} images")
        
        for i, image_path in enumerate(image_paths):
            try:
                self.logger.info(f"Processing image {i+1}/{len(image_paths)}: {image_path}")
                result = self.extract_text_from_image_file(image_path)
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing image {image_path}: {str(e)}")
                results.append({
                    'text': '',
                    'confidence': 0.0,
                    'method': 'ocr',
                    'error': str(e),
                    'source_file': image_path
                })
        
        self.logger.info(f"Completed batch OCR for {len(results)} images")
        return results
    
    def test_ocr_quality(self, test_images: List[str]) -> Dict[str, Any]:
        """
        Test OCR quality on sample images.
        
        Args:
            test_images: List of test image paths
            
        Returns:
            Quality assessment results
        """
        results = []
        total_confidence = 0.0
        total_words = 0
        
        for image_path in test_images:
            result = self.extract_text_from_image_file(image_path)
            results.append(result)
            
            if 'confidence' in result and result['confidence'] > 0:
                total_confidence += result['confidence']
                total_words += result.get('word_count', 0)
        
        # Calculate overall statistics
        successful_ocrs = [r for r in results if r.get('confidence', 0) > 0]
        
        quality_report = {
            'total_images': len(test_images),
            'successful_ocrs': len(successful_ocrs),
            'success_rate': len(successful_ocrs) / len(test_images) if test_images else 0,
            'average_confidence': total_confidence / len(successful_ocrs) if successful_ocrs else 0,
            'total_words_extracted': total_words,
            'results': results
        }
        
        return quality_report
    
    def optimize_for_pashto(self) -> None:
        """
        Optimize OCR settings specifically for Pashto text.
        """
        # Update Tesseract configuration for Pashto
        self.config = "--psm 6 -l " + self.languages + " --oem 3"
        
        # Update preprocessing parameters for Pashto
        self.preprocess_params.update({
            'resize_factor': 2.5,  # Higher resolution for better Pashto character recognition
            'denoise': True,
            'enhance_contrast': True,
            'median_blur_kernel': 3,
            'gaussian_blur_kernel': 1,
        })
        
        self.logger.info("OCR settings optimized for Pashto text")
    
    def get_tesseract_info(self) -> Dict[str, Any]:
        """
        Get information about Tesseract installation and capabilities.
        
        Returns:
            Dictionary with Tesseract information
        """
        try:
            # Get Tesseract version
            version = pytesseract.get_tesseract_version()
            
            # Get available languages
            languages = pytesseract.get_languages()
            
            # Get default config
            config = pytesseract.image_to_string.__defaults__
            
            return {
                'tesseract_version': str(version),
                'available_languages': languages,
                'current_languages': self.languages,
                'config': self.config,
                'is_pashto_available': 'pus' in languages,
                'default_config': config
            }
            
        except Exception as e:
            self.logger.error(f"Error getting Tesseract info: {str(e)}")
            return {
                'error': str(e),
                'available': False
            }