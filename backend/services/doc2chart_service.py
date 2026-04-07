"""
Doc2Chart Service - Extract tables from PDF, DOCX, and images
"""

import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import io

logger = logging.getLogger(__name__)


class Doc2ChartService:
    """Extract tables from documents and images"""
    
    @staticmethod
    async def extract_from_pdf(file_path: str) -> List[pd.DataFrame]:
        """
        Extract tables from PDF using pdfplumber
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of DataFrames (one per table found)
        """
        try:
            import pdfplumber
            
            tables = []
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract tables from page
                    page_tables = page.extract_tables()
                    
                    for table_num, table in enumerate(page_tables, 1):
                        if not table or len(table) < 2:
                            continue
                        
                        # Convert to DataFrame
                        # First row as header
                        df = pd.DataFrame(table[1:], columns=table[0])
                        
                        # Clean column names
                        df.columns = [str(col).strip() if col else f"Column_{i}" 
                                     for i, col in enumerate(df.columns)]
                        
                        # Remove empty rows
                        df = df.dropna(how='all')
                        
                        if not df.empty:
                            df.attrs['source'] = f"Page {page_num}, Table {table_num}"
                            tables.append(df)
                            logger.info(f"Extracted table from PDF page {page_num}: {df.shape}")
            
            return tables
            
        except ImportError:
            logger.error("pdfplumber not installed. Install with: pip install pdfplumber")
            raise ValueError("PDF extraction requires pdfplumber")
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise
    
    @staticmethod
    async def extract_from_docx(file_path: str) -> List[pd.DataFrame]:
        """
        Extract tables from DOCX using python-docx
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            List of DataFrames (one per table found)
        """
        try:
            from docx import Document
            
            tables = []
            doc = Document(file_path)
            
            for table_num, table in enumerate(doc.tables, 1):
                # Extract table data
                data = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    data.append(row_data)
                
                if len(data) < 2:
                    continue
                
                # Convert to DataFrame
                df = pd.DataFrame(data[1:], columns=data[0])
                
                # Clean column names
                df.columns = [str(col).strip() if col else f"Column_{i}" 
                             for i, col in enumerate(df.columns)]
                
                # Remove empty rows
                df = df.dropna(how='all')
                
                if not df.empty:
                    df.attrs['source'] = f"Table {table_num}"
                    tables.append(df)
                    logger.info(f"Extracted table from DOCX: {df.shape}")
            
            return tables
            
        except ImportError:
            logger.error("python-docx not installed. Install with: pip install python-docx")
            raise ValueError("DOCX extraction requires python-docx")
        except Exception as e:
            logger.error(f"DOCX extraction failed: {str(e)}")
            raise
    
    @staticmethod
    async def extract_from_image(file_path: str) -> pd.DataFrame:
        """
        Extract table from image using OCR (pytesseract + OpenCV)
        
        Args:
            file_path: Path to image file
            
        Returns:
            DataFrame extracted from image
        """
        try:
            import pytesseract
            from PIL import Image
            import cv2
            import numpy as np
            
            # Read image
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError(f"Could not read image: {file_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR with table structure
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(thresh, config=custom_config)
            
            # Parse text into table
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if len(lines) < 2:
                raise ValueError("No table structure detected in image")
            
            # Split by whitespace (simple approach)
            data = []
            for line in lines:
                # Split by multiple spaces or tabs
                parts = [p.strip() for p in line.split('  ') if p.strip()]
                if parts:
                    data.append(parts)
            
            if not data:
                raise ValueError("Could not parse table from image")
            
            # Find max columns
            max_cols = max(len(row) for row in data)
            
            # Pad rows to same length
            for row in data:
                while len(row) < max_cols:
                    row.append('')
            
            # Convert to DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])
            df.attrs['source'] = "Image OCR"
            
            logger.info(f"Extracted table from image: {df.shape}")
            return df
            
        except ImportError as e:
            logger.error(f"Missing dependency: {str(e)}")
            raise ValueError("Image extraction requires pytesseract and opencv-python")
        except Exception as e:
            logger.error(f"Image extraction failed: {str(e)}")
            raise
    
    @staticmethod
    async def auto_detect_and_extract(file_path: str) -> List[pd.DataFrame]:
        """
        Auto-detect file type and extract tables
        
        Args:
            file_path: Path to file
            
        Returns:
            List of DataFrames extracted from file
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return await Doc2ChartService.extract_from_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return await Doc2ChartService.extract_from_docx(file_path)
        elif extension in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            df = await Doc2ChartService.extract_from_image(file_path)
            return [df]
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    @staticmethod
    async def merge_tables(tables: List[pd.DataFrame], strategy: str = 'concat') -> pd.DataFrame:
        """
        Merge multiple tables into one
        
        Args:
            tables: List of DataFrames
            strategy: 'concat' (stack vertically) or 'join' (merge on common columns)
            
        Returns:
            Merged DataFrame
        """
        if not tables:
            raise ValueError("No tables to merge")
        
        if len(tables) == 1:
            return tables[0]
        
        try:
            if strategy == 'concat':
                # Stack vertically (ignore index)
                merged = pd.concat(tables, ignore_index=True)
                logger.info(f"Concatenated {len(tables)} tables: {merged.shape}")
                return merged
            
            elif strategy == 'join':
                # Find common columns
                common_cols = set(tables[0].columns)
                for df in tables[1:]:
                    common_cols &= set(df.columns)
                
                if not common_cols:
                    # No common columns, fall back to concat
                    logger.warning("No common columns found, falling back to concat")
                    return await Doc2ChartService.merge_tables(tables, 'concat')
                
                # Merge on common columns
                merged = tables[0]
                for df in tables[1:]:
                    merged = pd.merge(merged, df, on=list(common_cols), how='outer')
                
                logger.info(f"Joined {len(tables)} tables on {common_cols}: {merged.shape}")
                return merged
            
            else:
                raise ValueError(f"Unknown merge strategy: {strategy}")
                
        except Exception as e:
            logger.error(f"Table merge failed: {str(e)}")
            raise
    
    @staticmethod
    def get_supported_formats() -> Dict[str, List[str]]:
        """Get supported file formats"""
        return {
            "documents": [".pdf", ".docx", ".doc"],
            "images": [".png", ".jpg", ".jpeg", ".bmp", ".tiff"],
            "spreadsheets": [".csv", ".xlsx", ".xls"]
        }
