"""M2 Document → Problem ingestion: parser adapter, segmentation, orchestration.

This package is the adapter boundary. It is deliberately free of heavy runtimes at
import time — the PyMuPDF dependency is imported lazily inside ``PyMuPDFParser`` so
``import voltquery.ingest`` never pulls it in.
"""
