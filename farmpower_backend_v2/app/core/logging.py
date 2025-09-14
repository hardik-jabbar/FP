import logging
import sys
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(app_name="FarmPower", log_level=logging.INFO):
    """
    Configure logging for the application with both file and console output.
    
    Args:
        app_name (str): Name of the application for log identification
        log_level (int): Logging level (default: logging.INFO)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename=log_dir / f"{app_name.lower()}.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # JSON handler for structured logging
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            if hasattr(record, "request_id"):
                log_data["request_id"] = record.request_id
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_data)
    
    json_handler = RotatingFileHandler(
        filename=log_dir / f"{app_name.lower()}_json.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    json_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(json_handler)
    
    # Log startup message
    root_logger.info(f"=== {app_name} Logging Initialized ===")
    return root_logger

# Performance monitoring middleware
async def performance_middleware(request, call_next):
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    # Calculate request duration
    duration = time.time() - start_time
    
    # Log request details
    logging.info(
        f"Request completed",
        extra={
            "request_id": request.headers.get("X-Request-ID", "N/A"),
            "method": request.method,
            "path": request.url.path,
            "duration": f"{duration:.3f}s",
            "status_code": response.status_code
        }
    )
    
    # Add timing header
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    return response