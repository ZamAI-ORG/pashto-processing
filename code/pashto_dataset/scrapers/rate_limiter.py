"""
Rate Limiter Module
==================

This module provides sophisticated rate limiting and request throttling
for respectful web scraping operations.
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from dataclasses import dataclass
from threading import RLock
import random

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting rules."""
    requests_per_second: float = 1.0
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    max_concurrent: int = 5
    backoff_factor: float = 1.5
    max_retries: int = 3
    retry_delay: float = 1.0


class RateLimiter:
    """
    Advanced rate limiter with domain-specific rules and intelligent backoff.
    
    Features:
    - Domain-specific rate limiting
    - Intelligent backoff strategies
    - Request prioritization
    - Retry mechanism
    - Async/thread-safe operations
    """
    
    def __init__(self):
        self.domains: Dict[str, RateLimitConfig] = {}
        self.request_history: Dict[str, List[float]] = defaultdict(list)
        self.concurrent_requests: Dict[str, int] = defaultdict(int)
        self.locks: Dict[str, RLock] = defaultdict(RLock)
        self.default_config = RateLimitConfig()
        self._setup_default_domains()
    
    def _setup_default_domains(self):
        """Set up default rate limiting configurations for common domains."""
        # Conservative defaults for news sites
        self.set_domain_config('news_sites', RateLimitConfig(
            requests_per_second=0.5,
            requests_per_minute=30,
            max_concurrent=2
        ))
        
        # More conservative for government/official sites
        self.set_domain_config('gov_sites', RateLimitConfig(
            requests_per_second=0.2,
            requests_per_minute=10,
            max_concurrent=1
        ))
        
        # Standard for general sites
        self.set_domain_config('general_sites', RateLimitConfig(
            requests_per_second=1.0,
            requests_per_minute=60,
            max_concurrent=5
        ))
        
        # Aggressive for archives and libraries
        self.set_domain_config('archives', RateLimitConfig(
            requests_per_second=0.3,
            requests_per_minute=20,
            max_concurrent=2
        ))
    
    def set_domain_config(self, domain: str, config: RateLimitConfig):
        """Set rate limiting configuration for a specific domain."""
        self.domains[domain] = config
        logger.info(f"Set rate limit for domain '{domain}': "
                   f"{config.requests_per_second} req/sec, "
                   f"{config.max_concurrent} concurrent")
    
    def get_domain_from_url(self, url: str) -> str:
        """Extract domain type from URL to determine appropriate rate limits."""
        if not url:
            return 'general_sites'
        
        url_lower = url.lower()
        
        # Check for specific domain types
        if any(indicator in url_lower for indicator in 
               ['news', 'afp', 'reuters', 'bbc', 'cnn', 'aljazeera']):
            return 'news_sites'
        elif any(indicator in url_lower for indicator in 
                ['.gov', '.gov.', 'government', 'official']):
            return 'gov_sites'
        elif any(indicator in url_lower for indicator in 
                ['archive', 'library', 'museum', 'digital']):
            return 'archives'
        else:
            return 'general_sites'
    
    def acquire(self, url: str, priority: int = 0) -> bool:
        """
        Acquire permission to make a request.
        
        Args:
            url: URL to make request to
            priority: Request priority (higher numbers = higher priority)
            
        Returns:
            True if request is allowed, False if rate limited
        """
        domain_type = self.get_domain_from_url(url)
        config = self.domains.get(domain_type, self.default_config)
        
        with self.locks[domain_type]:
            current_time = time.time()
            
            # Check concurrent requests limit
            if self.concurrent_requests[domain_type] >= config.max_concurrent:
                logger.debug(f"Rate limit: max concurrent requests reached for {domain_type}")
                return False
            
            # Clean old requests from history
            self._clean_history(domain_type, current_time)
            
            # Check per-second limit
            recent_requests = [t for t in self.request_history[domain_type] 
                             if current_time - t < 1.0]
            if len(recent_requests) >= config.requests_per_second:
                logger.debug(f"Rate limit: per-second limit reached for {domain_type}")
                return False
            
            # Check per-minute limit
            minute_requests = [t for t in self.request_history[domain_type] 
                              if current_time - t < 60.0]
            if len(minute_requests) >= config.requests_per_minute:
                logger.debug(f"Rate limit: per-minute limit reached for {domain_type}")
                return False
            
            # Check per-hour limit
            hour_requests = [t for t in self.request_history[domain_type] 
                            if current_time - t < 3600.0]
            if len(hour_requests) >= config.requests_per_hour:
                logger.debug(f"Rate limit: per-hour limit reached for {domain_type}")
                return False
            
            # All checks passed, allow request
            self.concurrent_requests[domain_type] += 1
            self.request_history[domain_type].append(current_time)
            
            logger.debug(f"Request allowed for {domain_type} ({len(recent_requests)+1}/sec)")
            return True
    
    def release(self, url: str):
        """Release a request slot after completion."""
        domain_type = self.get_domain_from_url(url)
        with self.locks[domain_type]:
            if self.concurrent_requests[domain_type] > 0:
                self.concurrent_requests[domain_type] -= 1
    
    def wait_time(self, url: str) -> float:
        """
        Calculate waiting time before next request is allowed.
        
        Args:
            url: URL to check
            
        Returns:
            Time to wait in seconds
        """
        domain_type = self.get_domain_from_url(url)
        config = self.domains.get(domain_type, self.default_config)
        
        with self.locks[domain_type]:
            current_time = time.time()
            self._clean_history(domain_type, current_time)
            
            wait_times = []
            
            # Check concurrent requests
            if self.concurrent_requests[domain_type] >= config.max_concurrent:
                # This is approximate - we'd need to track when slots will free up
                wait_times.append(config.retry_delay)
            
            # Check per-second limit
            recent_requests = [t for t in self.request_history[domain_type] 
                             if current_time - t < 1.0]
            if len(recent_requests) >= config.requests_per_second:
                if recent_requests:
                    oldest_recent = min(recent_requests)
                    wait_times.append(1.0 - (current_time - oldest_recent) + 0.1)
            
            # Check per-minute limit
            minute_requests = [t for t in self.request_history[domain_type] 
                              if current_time - t < 60.0]
            if len(minute_requests) >= config.requests_per_minute:
                if minute_requests:
                    oldest_minute = min(minute_requests)
                    wait_times.append(60.0 - (current_time - oldest_minute) + 1.0)
            
            return max(wait_times) if wait_times else 0.0
    
    def _clean_history(self, domain_type: str, current_time: float):
        """Clean old requests from history to prevent memory bloat."""
        cutoff_time = current_time - 3600  # Keep 1 hour of history
        self.request_history[domain_type] = [
            t for t in self.request_history[domain_type] 
            if t > cutoff_time
        ]
    
    def get_status(self, url: str = None) -> Dict[str, Any]:
        """
        Get current rate limiting status.
        
        Args:
            url: Optional URL to get specific domain status
            
        Returns:
            Status information
        """
        if url:
            domain_type = self.get_domain_from_url(url)
            config = self.domains.get(domain_type, self.default_config)
            
            current_time = time.time()
            self._clean_history(domain_type, current_time)
            
            recent_requests = [t for t in self.request_history[domain_type] 
                             if current_time - t < 1.0]
            minute_requests = [t for t in self.request_history[domain_type] 
                              if current_time - t < 60.0]
            
            return {
                'domain_type': domain_type,
                'config': config.__dict__,
                'current_concurrent': self.concurrent_requests[domain_type],
                'recent_requests_per_second': len(recent_requests),
                'requests_per_minute': len(minute_requests),
                'max_per_second': config.requests_per_second,
                'max_per_minute': config.requests_per_minute,
                'max_concurrent': config.max_concurrent,
                'wait_time': self.wait_time(url)
            }
        else:
            # Return status for all domains
            status = {}
            for domain_type in list(self.domains.keys()) + ['general_sites']:
                config = self.domains.get(domain_type, self.default_config)
                current_time = time.time()
                self._clean_history(domain_type, current_time)
                
                status[domain_type] = {
                    'config': config.__dict__,
                    'current_concurrent': self.concurrent_requests[domain_type],
                    'recent_requests': len(self.request_history[domain_type])
                }
            return status


class AdaptiveRateLimiter(RateLimiter):
    """
    Rate limiter that adapts to server responses and network conditions.
    
    Features:
    - Automatic adjustment based on response codes
    - Error rate monitoring
    - Network latency awareness
    - Dynamic backoff strategies
    """
    
    def __init__(self):
        super().__init__()
        self.error_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        self.last_adjustment: Dict[str, float] = {}
        self.adjustment_cooldown = 60  # Don't adjust more than once per minute per domain
    
    def record_response(self, url: str, response_code: int, response_time: float):
        """
        Record response information for adaptive rate limiting.
        
        Args:
            url: URL that was requested
            response_code: HTTP response code
            response_time: Time taken for request in seconds
        """
        domain_type = self.get_domain_from_url(url)
        current_time = time.time()
        
        # Record response time
        self.response_times[domain_type].append(response_time)
        if len(self.response_times[domain_type]) > 100:  # Keep last 100 measurements
            self.response_times[domain_type] = self.response_times[domain_type][-100:]
        
        # Record errors
        if response_code >= 400:
            self.error_counts[domain_type][str(response_code)] += 1
        
        # Trigger adaptive adjustment if needed
        self._maybe_adjust_limits(domain_type, current_time)
    
    def _maybe_adjust_limits(self, domain_type: str, current_time: float):
        """Maybe adjust rate limits based on recent performance."""
        # Check cooldown
        if (domain_type in self.last_adjustment and 
            current_time - self.last_adjustment[domain_type] < self.adjustment_cooldown):
            return
        
        config = self.domains.get(domain_type, self.default_config)
        errors = self.error_counts[domain_type]
        response_times = self.response_times[domain_type]
        
        # Adjust based on error rates
        total_requests = sum(errors.values()) + 100  # Estimate successful requests
        error_rate = sum(errors.values()) / total_requests if total_requests > 0 else 0
        
        # Adjust based on response times
        avg_response_time = sum(response_times) / len(response_times) if response_times else 1.0
        
        should_adjust = False
        new_config = config
        
        # If high error rate, slow down
        if error_rate > 0.1:  # 10% error rate
            new_config.requests_per_second *= 0.8
            new_config.max_concurrent = max(1, int(new_config.max_concurrent * 0.8))
            should_adjust = True
            logger.info(f"Rate limit reduced for {domain_type} due to high error rate ({error_rate:.2%})")
        
        # If slow response times, slow down
        elif avg_response_time > 5.0:  # 5 second average
            new_config.requests_per_second *= 0.9
            should_adjust = True
            logger.info(f"Rate limit reduced for {domain_type} due to slow responses ({avg_response_time:.2f}s avg)")
        
        # If very low error rate and fast responses, speed up
        elif error_rate < 0.01 and avg_response_time < 1.0:  # 1% error rate, 1s response
            new_config.requests_per_second *= 1.1
            new_config.max_concurrent = min(10, int(new_config.max_concurrent * 1.1))
            should_adjust = True
            logger.info(f"Rate limit increased for {domain_type} due to good performance")
        
        if should_adjust:
            # Clamp to reasonable bounds
            new_config.requests_per_second = max(0.1, min(5.0, new_config.requests_per_second))
            new_config.max_concurrent = max(1, min(20, int(new_config.max_concurrent)))
            
            self.domains[domain_type] = new_config
            self.last_adjustment[domain_type] = current_time
    
    def get_error_rate(self, domain_type: str) -> float:
        """Get current error rate for a domain."""
        errors = self.error_counts[domain_type]
        total_errors = sum(errors.values())
        # This is a rough estimate - we'd need to track total requests for accuracy
        estimated_requests = total_errors * 20  # Rough estimate
        return total_errors / estimated_requests if estimated_requests > 0 else 0.0