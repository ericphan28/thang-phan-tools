#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration: Add OCR Analytics Tables
Adds 3 tables for OCR usage tracking and sales analytics
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.models.ocr_analytics import OCRUsageLog, OCRUserAction, OCRConversionFunnel
from app.models.auth_models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Add OCR analytics tables"""
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    logger.info("🔧 Creating OCR analytics tables...")
    
    try:
        # Create all tables (will skip existing ones)
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        logger.info("✅ OCR analytics tables created successfully!")
        logger.info("   - ocr_usage_logs (OCR processing logs)")
        logger.info("   - ocr_user_actions (User behavior tracking)")
        logger.info("   - ocr_conversion_funnel (Sales metrics)")
        
        # Verify tables exist
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Test query
            count = session.query(OCRUsageLog).count()
            logger.info(f"✅ Verification: ocr_usage_logs table has {count} records")
            
            count2 = session.query(OCRUserAction).count()
            logger.info(f"✅ Verification: ocr_user_actions table has {count2} records")
            
            count3 = session.query(OCRConversionFunnel).count()
            logger.info(f"✅ Verification: ocr_conversion_funnel table has {count3} records")
            
        finally:
            session.close()
        
        logger.info("\n✅ Migration completed successfully!")
        logger.info("   You can now use OCR analytics for sales tracking.")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    run_migration()
