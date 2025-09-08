# services/zsin_ordenes_service.py

# Logging
from playwright.sync_api import Error
from data_models.zsin_ordenes_models import ZsinOrdenesFormData
from services.transaction_service import TransactionService
from pages.zsin_ordenes_page import ZsinOrdenesPage

import logging
log = logging.getLogger(__name__)

class DownloadFailureError(Exception):
    pass

class ZsinOrdenesService:
    pass