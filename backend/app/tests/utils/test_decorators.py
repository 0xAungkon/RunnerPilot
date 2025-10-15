import time
import functools
from typing import Callable, Any
from fastapi.testclient import TestClient
from app.tests.utils.test_logger import log_api_test


def log_test_execution(method: str, endpoint_template: str = None):
    """
    Decorator to automatically log test execution data.
    
    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint_template: Template for endpoint URL (can include placeholders)
    """
    def decorator(test_func: Callable) -> Callable:
        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            test_name = test_func.__name__
            test_status = "PASSED"
            error_message = None
            
            try:
                # Execute the test
                result = test_func(*args, **kwargs)
                return result
            except Exception as e:
                test_status = "FAILED"
                error_message = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                # Log the test execution
                log_api_test(
                    test_name=test_name,
                    method=method,
                    endpoint=endpoint_template or f"/{test_name.replace('test_', '').replace('_', '/')}",
                    test_status=test_status,
                    error_message=error_message,
                    duration_ms=round(duration_ms, 2)
                )
        
        return wrapper
    return decorator


class TestAPILogger:
    """
    Context manager and utility class for logging API test calls.
    """
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = None
        self.requests = []
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000 if self.start_time else 0
        test_status = "FAILED" if exc_type else "PASSED"
        error_message = str(exc_val) if exc_val else None
        
        # Log each request made during the test
        for request_data in self.requests:
            log_api_test(
                test_name=self.test_name,
                method=request_data['method'],
                endpoint=request_data['endpoint'],
                payload=request_data.get('payload'),
                query_params=request_data.get('query_params'),
                headers=request_data.get('headers'),
                response_status=request_data.get('response_status'),
                response_body=request_data.get('response_body'),
                test_status=test_status,
                error_message=error_message,
                duration_ms=round(duration_ms, 2)
            )
    
    def log_request(
        self,
        method: str,
        endpoint: str,
        payload: dict = None,
        query_params: dict = None,
        headers: dict = None,
        response = None
    ):
        """Log a single API request within the test"""
        response_data = {
            'method': method,
            'endpoint': endpoint,
            'payload': payload,
            'query_params': query_params,
            'headers': headers
        }
        
        if response:
            response_data['response_status'] = response.status_code
            try:
                response_data['response_body'] = response.json()
            except:
                response_data['response_body'] = {"raw_content": response.text}
        
        self.requests.append(response_data)
        return response


def logged_api_call(
    client: TestClient,
    method: str,
    url: str,
    logger: TestAPILogger,
    **kwargs
) -> Any:
    """
    Make an API call and automatically log it.
    
    Args:
        client: FastAPI test client
        method: HTTP method
        url: Request URL
        logger: TestAPILogger instance
        **kwargs: Additional arguments passed to the client method
    
    Returns:
        Response object
    """
    # Extract common parameters
    json_payload = kwargs.get('json')
    headers = kwargs.get('headers')
    params = kwargs.get('params')
    
    # Make the API call
    client_method = getattr(client, method.lower())
    response = client_method(url, **kwargs)
    
    # Log the request
    logger.log_request(
        method=method.upper(),
        endpoint=url,
        payload=json_payload,
        query_params=params,
        headers=headers,
        response=response
    )
    
    return response