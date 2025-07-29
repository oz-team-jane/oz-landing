"""
파일 처리 서비스
PDF 및 이미지 파일에서 텍스트 추출
"""

import structlog
import io
from typing import List, Optional
from fastapi import UploadFile
import PyPDF2
from PIL import Image
import pytesseract
import re

logger = structlog.get_logger(__name__)


class FileProcessingService:
    """파일 처리 서비스"""
    
    def __init__(self):
        self.logger = logger.bind(service="FileProcessingService")
        # Tesseract가 설치되어 있는지 확인
        try:
            pytesseract.get_tesseract_version()
            self.ocr_available = True
            self.logger.info("OCR 엔진 사용 가능")
        except Exception as e:
            self.ocr_available = False
            self.logger.warning("OCR 엔진 사용 불가", error=str(e))
    
    async def process_files(self, files: List[UploadFile]) -> str:
        """
        업로드된 파일들에서 텍스트를 추출합니다.
        
        Args:
            files: 업로드된 파일들
            
        Returns:
            str: 추출된 텍스트
        """
        extracted_texts = []
        
        for file in files:
            try:
                # 파일 크기 확인 (10MB 제한)
                content = await file.read()
                if len(content) > 10 * 1024 * 1024:  # 10MB
                    self.logger.warning("파일 크기 초과", filename=file.filename, size=len(content))
                    continue
                
                # 파일 타입에 따라 처리
                if file.content_type == 'application/pdf':
                    text = await self._extract_text_from_pdf(content, file.filename)
                elif file.content_type and file.content_type.startswith('image/'):
                    text = await self._extract_text_from_image(content, file.filename)
                else:
                    self.logger.warning("지원하지 않는 파일 타입", 
                                      filename=file.filename, 
                                      content_type=file.content_type)
                    continue
                
                if text and text.strip():
                    extracted_texts.append(f"[{file.filename}]\n{text}")
                    self.logger.info("텍스트 추출 완료", 
                                   filename=file.filename, 
                                   length=len(text))
                
            except Exception as e:
                self.logger.error("파일 처리 실패", 
                                filename=file.filename, 
                                error=str(e))
                continue
        
        return "\n\n".join(extracted_texts)
    
    async def _extract_text_from_pdf(self, content: bytes, filename: str) -> str:
        """PDF 파일에서 텍스트 추출"""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(page_text)
                        self.logger.debug("PDF 페이지 처리 완료", 
                                        filename=filename, 
                                        page=page_num + 1)
                except Exception as e:
                    self.logger.warning("PDF 페이지 처리 실패", 
                                      filename=filename, 
                                      page=page_num + 1, 
                                      error=str(e))
                    continue
            
            extracted_text = "\n\n".join(text_parts)
            
            # 텍스트 정리
            extracted_text = self._clean_extracted_text(extracted_text)
            
            return extracted_text
            
        except Exception as e:
            self.logger.error("PDF 텍스트 추출 실패", filename=filename, error=str(e))
            return ""
    
    async def _extract_text_from_image(self, content: bytes, filename: str) -> str:
        """이미지 파일에서 텍스트 추출 (OCR)"""
        if not self.ocr_available:
            self.logger.warning("OCR 엔진 사용 불가", filename=filename)
            return ""
        
        try:
            # 이미지 열기
            image = Image.open(io.BytesIO(content))
            
            # 이미지가 너무 크면 리사이즈
            max_size = (2000, 2000)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                self.logger.info("이미지 리사이즈 완료", filename=filename, new_size=image.size)
            
            # OCR 실행 (한국어와 영어 지원)
            try:
                # 한국어 + 영어 OCR 시도
                text = pytesseract.image_to_string(image, lang='kor+eng')
            except:
                try:
                    # 영어만 OCR 시도
                    text = pytesseract.image_to_string(image, lang='eng')
                except:
                    # 기본 OCR 시도
                    text = pytesseract.image_to_string(image)
            
            # 텍스트 정리
            text = self._clean_extracted_text(text)
            
            return text
            
        except Exception as e:
            self.logger.error("이미지 텍스트 추출 실패", filename=filename, error=str(e))
            return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """추출된 텍스트 정리"""
        if not text:
            return ""
        
        # 여러 줄바꿈을 하나로 변경
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        # 너무 짧은 텍스트는 의미 없을 수 있음
        if len(text) < 10:
            return ""
        
        return text
    
    def is_valid_file_type(self, content_type: str) -> bool:
        """지원하는 파일 타입인지 확인"""
        supported_types = [
            'application/pdf',
            'image/jpeg',
            'image/jpg', 
            'image/png'
        ]
        return content_type in supported_types
    
    def is_valid_file_size(self, size: int, max_size_mb: int = 10) -> bool:
        """파일 크기가 유효한지 확인"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return size <= max_size_bytes