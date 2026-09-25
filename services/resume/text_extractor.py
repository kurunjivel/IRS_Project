"""
Text Extractor for Resume/CV Parser.
Supports PDF (pypdf), DOCX (python-docx), and TXT files.
"""

import io
import logging

logger = logging.getLogger(__name__)


class UnextractableTextError(Exception):
    """Raised when text cannot be extracted from a document (e.g. scanned image PDF)."""
    pass


class TextExtractor:
    """Extracts raw text from PDF, DOCX, or TXT binary streams."""

    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> str:
        """
        Extract raw text based on file extension.

        Args:
            file_bytes: Raw file content bytes.
            filename: File name including extension.

        Returns:
            Extracted text string.

        Raises:
            UnextractableTextError: If text extraction fails or yields no text.
            ValueError: If file type is unsupported.
        """
        ext = filename.lower().split(".")[-1]

        if ext == "pdf":
            return TextExtractor._extract_pdf(file_bytes)
        elif ext in ["docx", "doc"]:
            return TextExtractor._extract_docx(file_bytes)
        elif ext == "txt":
            return TextExtractor._extract_txt(file_bytes)
        else:
            raise ValueError(f"Unsupported file format '.{ext}'. Please upload a PDF, DOCX, or TXT file.")

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text_pages = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text_pages.append(page_text)

            full_text = "\n".join(text_pages).strip()
            if not full_text:
                raise UnextractableTextError(
                    "Text could not be extracted from this document. Please upload a text-based PDF or DOCX."
                )
            return full_text
        except UnextractableTextError:
            raise
        except Exception as e:
            logger.error("PDF text extraction failed: %s", e)
            raise UnextractableTextError(
                "Text could not be extracted from this document. Please upload a text-based PDF or DOCX."
            )

    @staticmethod
    def _extract_docx(file_bytes: bytes) -> str:
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n".join(paragraphs).strip()
            if not full_text:
                raise UnextractableTextError(
                    "Text could not be extracted from this document. Please upload a text-based PDF or DOCX."
                )
            return full_text
        except UnextractableTextError:
            raise
        except Exception as e:
            logger.error("DOCX text extraction failed: %s", e)
            raise UnextractableTextError(
                "Text could not be extracted from this document. Please upload a text-based PDF or DOCX."
            )

    @staticmethod
    def _extract_txt(file_bytes: bytes) -> str:
        try:
            full_text = file_bytes.decode("utf-8", errors="ignore").strip()
            if not full_text:
                raise UnextractableTextError("Text file is empty.")
            return full_text
        except Exception as e:
            logger.error("TXT text extraction failed: %s", e)
            raise UnextractableTextError("Text could not be extracted from this document.")
