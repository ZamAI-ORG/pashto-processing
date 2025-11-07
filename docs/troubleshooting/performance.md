# Performance Optimization Guide

Comprehensive guide to optimizing the Pashto Dataset Pipeline for maximum performance with different hardware configurations and use cases.

## 📋 Table of Contents

- [Performance Analysis](#performance-analysis)
- [Memory Optimization](#memory-optimization)
- [CPU Optimization](#cpu-optimization)
- [I/O Optimization](#io-optimization)
- [Network Optimization](#network-optimization)
- [Hardware-Specific Optimizations](#hardware-specific-optimizations)
- [Scalability Strategies](#scalability-strategies)
- [Monitoring and Benchmarking](#monitoring-and-benchmarking)

## 📊 Performance Analysis

### Understanding Performance Bottlenecks

Before optimizing, identify the bottlenecks in your specific use case:

#### CPU-Bound Scenarios
- Text normalization and processing
- Quality assessment algorithms
- Language detection
- Complex deduplication

#### I/O-Bound Scenarios  
- Large file reading/writing
- Network scraping
- Database operations
- Storage on slow disks

#### Memory-Bound Scenarios
- Large batch processing
- Caching enabled
- Complex in-memory operations
- Streaming disabled

### Performance Profiling

#### Built-in Profiling

```bash
# Enable profiling during processing
pashto-pipeline process \
  --input data/ \
  --output processed/ \
  --config config.yaml \
  --profile \
  --profile-output performance.prof

# Generate performance report
pashto-pipeline performance-report \
  --profile-file performance.prof \
  --output performance_report.html
```

#### Manual Profiling

```python
import cProfile
import pstats
from pashto_pipeline import Pipeline, Config

def profile_pipeline():
    """Profile pipeline execution"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run pipeline
    config = Config.from_file('config.yaml')
    pipeline = Pipeline(config)
    pipeline.run('data/', 'processed/')
    
    profiler.disable()
    
    # Save and analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
    
    # Save detailed stats
    stats.dump_stats('pipeline_profile.prof')

if __name__ == "__main__":
    profile_pipeline()
```

#### System Monitoring

```bash
# Monitor CPU, memory, and I/O during processing
htop &
iotop -a &
pashto-pipeline process --config config.yaml

# Monitor specific process
pid=$(pgrep -f "pashto-pipeline")
watch -n 1 "ps -p $pid -o pid,ppid,pcpu,pmem,vsz,rss,comm"
```

## 💾 Memory Optimization

### Memory-Efficient Configuration

#### Low-Memory Systems (2-4GB RAM)

```yaml
# config/memory_optimized.yaml
advanced:
  # Conservative memory usage
  max_workers: 1
  process_pool_size: 1
  memory_limit: "1.5GB"
  batch_size: 25
  stream_processing: true
  streaming_chunk_size: 500
  
  # Disable memory-intensive features
  enable_caching: false
  cache_intermediate_results: false
  
  # Aggressive garbage collection
  aggressive_gc: true
  gc_frequency: 5  # Every 5 items
  
  # I/O optimization
  use_memory_mapping: false
  async_io: false
  io_buffer_size: "512KB"
  
processing:
  # Skip expensive operations
  remove_duplicates: false
  check_spellings: false
  grammar_check: false
  
quality:
  # Fast quality assessment
  enable_quality_scoring: false
  approximate_scoring: true
  quality_sampling:
    enabled: true
    sample_rate: 0.05  # Check only 5%
```

#### Medium-Memory Systems (8-16GB RAM)

```yaml
# config/memory_balanced.yaml
advanced:
  # Balanced configuration
  max_workers: 4
  process_pool_size: 2
  memory_limit: "8GB"
  batch_size: 200
  stream_processing: true
  streaming_chunk_size: 2000
  
  # Moderate caching
  enable_caching: true
  cache_intermediate_results: true
  cache_ttl: 1800  # 30 minutes
  
  # Regular garbage collection
  aggressive_gc: false
  gc_frequency: 50
  
  # I/O optimization
  use_memory_mapping: true
  async_io: true
  io_buffer_size: "4MB"

processing:
  # Enable most features
  remove_duplicates: true
  duplicate_strategy: "exact"  # Faster than fuzzy
  
quality:
  # Standard quality assessment
  enable_quality_scoring: true
  quality_sampling:
    enabled: true
    sample_rate: 0.2  # Check 20%
```

#### High-Memory Systems (32GB+ RAM)

```yaml
# config/memory_optimized.yaml
advanced:
  # Aggressive memory usage
  max_workers: 16
  process_pool_size: 12
  memory_limit: "24GB"
  batch_size: 2000
  stream_processing: false  # Load everything in memory
  cache_intermediate_results: true
  enable_caching: true
  cache_ttl: 3600  # 1 hour
  
  # Minimal garbage collection
  aggressive_gc: false
  gc_frequency: 1000
  
  # Maximum I/O performance
  use_memory_mapping: true
  async_io: true
  io_buffer_size: "64MB"
  direct_io: true

processing:
  # All features enabled
  remove_duplicates: true
  duplicate_strategy: "fuzzy"
  fuzzy_threshold: 0.95
  
quality:
  # Comprehensive quality assessment
  enable_quality_scoring: true
  approximate_scoring: false
  quality_sampling:
    enabled: false  # Check everything
```

### Memory Monitoring and Management

#### Memory Usage Tracking

```python
import psutil
import gc
import time
from typing import Dict, Any

class MemoryMonitor:
    """Monitor and manage memory usage during processing"""
    
    def __init__(self, max_memory_gb: float = 8.0):
        self.max_memory_bytes = max_memory_gb * 1024**3
        self.initial_memory = psutil.Process().memory_info().rss
        self.peak_memory = self.initial_memory
        self.memory_snapshots = []
    
    def snapshot(self, label: str = ""):
        """Take memory snapshot"""
        process = psutil.Process()
        current_memory = process.memory_info().rss
        
        self.peak_memory = max(self.peak_memory, current_memory)
        
        snapshot = {
            'label': label,
            'timestamp': time.time(),
            'memory_mb': current_memory / 1024**2,
            'peak_mb': self.peak_memory / 1024**2,
            'gc_count': gc.get_count()
        }
        
        self.memory_snapshots.append(snapshot)
        
        # Log memory usage
        print(f"Memory: {snapshot['memory_mb']:.1f}MB "
              f"(Peak: {snapshot['peak_mb']:.1f}MB) "
              f"{label}")
        
        # Force garbage collection if memory usage is high
        if current_memory > self.max_memory_bytes * 0.8:
            gc.collect()
            print("Forced garbage collection")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            'initial_mb': self.initial_memory / 1024**2,
            'peak_mb': self.peak_memory / 1024**2,
            'current_mb': psutil.Process().memory_info().rss / 1024**2,
            'snapshots': self.memory_snapshots,
            'gc_collections': sum(s['gc_count'] for s in self.memory_snapshots)
        }
```

#### Memory-Efficient Processing

```python
def process_large_dataset_efficiently(data_source, output_path, config):
    """Process large dataset with memory optimization"""
    from memory_monitor import MemoryMonitor
    
    monitor = MemoryMonitor(max_memory_gb=4.0)
    
    try:
        # Process in small chunks
        chunk_size = config.get('chunk_size', 100)
        
        for chunk_num, chunk in enumerate(data_source.chunks(chunk_size)):
            monitor.snapshot(f"Processing chunk {chunk_num}")
            
            # Process chunk
            processed_chunk = process_chunk(chunk, config)
            
            # Write immediately to free memory
            write_chunk(processed_chunk, output_path, chunk_num)
            
            # Force cleanup
            del processed_chunk
            gc.collect()
            
    except MemoryError:
        print("Memory error detected, reducing chunk size")
        # Retry with smaller chunks
        process_large_dataset_efficiently(data_source, output_path, 
                                        {**config, 'chunk_size': chunk_size // 2})
```

## ⚡ CPU Optimization

### Multi-Processing Configuration

#### CPU Core-Based Worker Count

```python
import psutil
import os

def get_optimal_worker_count():
    """Determine optimal number of workers based on CPU cores"""
    cpu_count = psutil.cpu_count()
    logical_count = psutil.cpu_count(logical=True)
    
    # Consider hyperthreading
    if cpu_count * 2 == logical_count:
        # Hyperthreaded system
        return cpu_count  # Use physical cores
    else:
        # Use logical cores but leave one free
        return max(1, logical_count - 1)

# Usage in configuration
workers = get_optimal_worker_count()
print(f"Using {workers} workers for {cpu_count} CPU cores")
```

#### Process vs Thread Optimization

```yaml
# config/cpu_optimized.yaml
advanced:
  # Process-based parallelism (CPU-bound tasks)
  max_workers: 8
  use_multiprocessing: true
  process_pool_size: 6  # Leave cores for other processes
  
  # Work distribution
  dynamic_load_balancing: true
  work_stealing: true
  
  # CPU affinity (Linux)
  cpu_affinity: true
  cpu_cores: [0, 1, 2, 3, 4, 5]  # Pin to specific cores
```

#### Vectorized Operations

```python
import numpy as np
from numba import jit, vectorize

@jit(nopython=True, parallel=True)
def vectorized_text_processing(texts):
    """Vectorized text processing for better CPU performance"""
    results = np.empty(len(texts), dtype=np.float64)
    
    for i in numba.prange(len(texts)):
        # Fast processing
        results[i] = process_text_fast(texts[i])
    
    return results

def process_texts_parallel(texts, num_workers=None):
    """Process texts using all available CPU cores"""
    if num_workers is None:
        num_workers = get_optimal_worker_count()
    
    # Split texts into chunks
    chunk_size = len(texts) // num_workers
    chunks = [texts[i:i + chunk_size] for i in range(0, len(texts), chunk_size)]
    
    # Process chunks in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(vectorized_text_processing, chunks))
    
    return np.concatenate(results)
```

#### SIMD Optimization

```python
# Enable SIMD instructions for text processing
import platform

def enable_simd_optimizations():
    """Enable SIMD optimizations based on CPU capabilities"""
    processor = platform.processor().lower()
    
    if 'avx' in processor or 'sse' in processor:
        # Enable AVX/SSE optimizations
        os.environ['OPENBLAS_NUM_THREADS'] = '1'
        os.environ['MKL_NUM_THREADS'] = '1'
        os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
        os.environ['NUMEXPR_NUM_THREADS'] = '1'
        print("SIMD optimizations enabled")
    else:
        print("SIMD optimizations not available")

enable_simd_optimizations()
```

## 💽 I/O Optimization

### Storage Configuration

#### SSD Optimization

```yaml
# config/ssd_optimized.yaml
advanced:
  # I/O settings optimized for SSD
  use_memory_mapping: true
  memory_mapped_io: true
  
  # Large I/O buffer for SSD
  io_buffer_size: "64MB"
  async_io: true
  direct_io: true  # Bypass system cache
  
  # Sequential I/O optimization
  sequential_io: true
  prefetch_data: true
  prefetch_size: "128MB"
  
  # File handling
  keep_file_handles_open: true
  reuse_buffers: true
```

#### HDD Optimization

```yaml
# config/hdd_optimized.yaml
advanced:
  # I/O settings optimized for HDD
  use_memory_mapping: false  # Slower on HDD
  async_io: false           # Sequential processing
  
  # Small I/O buffer for HDD
  io_buffer_size: "1MB"
  
  # Defensive settings
  direct_io: false
  keep_file_handles_open: false
  
  # Stagger I/O operations
  io_delay_ms: 10  # 10ms delay between I/O operations
```

### File Format Optimization

#### Performance by Format

| Format | Read Speed | Write Speed | Memory Usage | Compression |
|--------|------------|-------------|--------------|-------------|
| Plain Text | Fast | Fast | Low | None |
| JSON | Medium | Slow | High | None |
| CSV | Fast | Fast | Low | None |
| Parquet | Very Fast | Very Fast | Medium | Yes |
| HDF5 | Fast | Medium | High | Yes |
| SQLite | Slow | Slow | Low | Yes |

#### Format-Specific Optimization

```yaml
# config/format_optimized.yaml
output:
  # Use Parquet for best performance
  format: "parquet"
  
  parquet_options:
    compression: "snappy"        # Fast compression
    compression_level: 1         # Low compression for speed
    row_group_size: 10000        # Large row groups
    use_dictionary: true         # Enable dictionary encoding
    write_statistics: false      # Skip statistics for speed
    
  # Alternative: CSV for maximum speed
  # format: "csv"
  # csv_options:
  #   delimiter: "\t"           # Tab-delimited
  #   lineterminator: "\n"      # Unix line endings
  #   include_header: false     # Skip header for speed
```

#### Streaming I/O

```python
import json
from typing import Iterator

def stream_process_large_file(input_file: str, output_file: str, 
                            chunk_size: int = 1000):
    """Process large file using streaming I/O"""
    
    def read_chunks(file_path: str, chunk_size: int) -> Iterator[list]:
        """Read file in chunks"""
        with open(file_path, 'r', encoding='utf-8') as f:
            chunk = []
            for line in f:
                chunk.append(json.loads(line))
                
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
            
            # Yield remaining items
            if chunk:
                yield chunk
    
    def write_chunk(chunk: list, output_path: str):
        """Write chunk to output file"""
        with open(output_path, 'a', encoding='utf-8') as f:
            for item in chunk:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # Process file in streaming fashion
    for chunk_num, chunk in enumerate(read_chunks(input_file, chunk_size)):
        processed_chunk = process_chunk(chunk)
        write_chunk(processed_chunk, output_file)
        
        # Log progress
        print(f"Processed chunk {chunk_num} ({len(chunk)} items)")
```

## 🌐 Network Optimization

### Web Scraping Performance

#### Connection Pooling

```yaml
# config/network_optimized.yaml
input:
  scraping:
    # Connection optimization
    connection_pool_size: 10
    max_connections: 50
    connection_timeout: 30
    read_timeout: 60
    
    # HTTP settings
    keep_alive: true
    max_keep_alive_requests: 100
    retry_requests: true
    max_retries: 3
    
    # Compression
    enable_compression: true
    accept_encoding: ["gzip", "deflate", "br"]
    
    # Caching
    cache_responses: true
    cache_ttl: 3600  # 1 hour
    cache_size: "100MB"
```

#### Rate Limiting and Politeness

```python
import time
import random
from typing import List, Dict

class OptimizedRateLimiter:
    """Optimized rate limiter for web scraping"""
    
    def __init__(self, requests_per_second: float = 1.0, 
                 burst_size: int = 5):
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Add tokens based on time elapsed
        elapsed = now - self.last_update
        new_tokens = elapsed * self.requests_per_second
        self.tokens = min(self.burst_size, self.tokens + new_tokens)
        
        if self.tokens < 1:
            # Need to wait
            wait_time = 1.0 / self.requests_per_second
            # Add some jitter
            wait_time += random.uniform(0.1, 0.3)
            time.sleep(wait_time)
            self.tokens = 0
        else:
            # Consume a token
            self.tokens -= 1
        
        self.last_update = now
    
    def get_optimal_delays(self, urls: List[str]) -> List[float]:
        """Calculate optimal delays for a batch of URLs"""
        base_delay = 1.0 / self.requests_per_second
        delays = []
        
        for i, url in enumerate(urls):
            # Add domain-based delays
            if i > 0 and self._same_domain(urls[i-1], url):
                delay = base_delay * 2  # Longer delay for same domain
            else:
                delay = base_delay
            
            # Add random jitter
            delay += random.uniform(0, 0.5)
            delays.append(delay)
        
        return delays
    
    def _same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain"""
        # Simple domain extraction
        domain1 = url1.split('/')[2] if '://' in url1 else url1
        domain2 = url2.split('/')[2] if '://' in url2 else url2
        return domain1 == domain2

# Usage
rate_limiter = OptimizedRateLimiter(requests_per_second=2.0, burst_size=10)

for url in urls:
    rate_limiter.wait_if_needed()
    response = fetch_url(url)
    process_response(response)
```

### Database Optimization

#### Connection Pooling

```python
import sqlalchemy
from sqlalchemy.pool import QueuePool

def create_optimized_engine(database_url: str, pool_size: int = 20):
    """Create optimized database engine"""
    
    engine = sqlalchemy.create_engine(
        database_url,
        # Connection pooling
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=0,
        pool_pre_ping=True,  # Verify connections
        pool_recycle=3600,   # Recycle connections every hour
        
        # Performance settings
        connect_args={
            "connect_timeout": 10,
            "application_name": "pashto_pipeline"
        }
    )
    
    return engine

# Usage
engine = create_optimized_engine("postgresql://user:pass@localhost/db")
```

#### Batch Operations

```python
def batch_insert_data(engine, data_chunks: List[List[Dict]], 
                     table_name: str, batch_size: int = 1000):
    """Optimized batch insertion"""
    
    with engine.begin() as connection:
        for chunk in data_chunks:
            # Process in sub-batches
            for i in range(0, len(chunk), batch_size):
                sub_batch = chunk[i:i + batch_size]
                
                # Bulk insert
                connection.execute(
                    sqlalchemy.text(f"""
                        INSERT INTO {table_name} 
                        (text, quality_score, metadata) 
                        VALUES (:text, :quality_score, :metadata)
                    """),
                    sub_batch
                )
                
                # Log progress
                print(f"Inserted {len(sub_batch)} records")
```

## 🖥️ Hardware-Specific Optimizations

### High-End Server (32+ cores, 128GB+ RAM)

```yaml
# config/server_optimized.yaml
advanced:
  # Maximum parallelism
  max_workers: 32
  process_pool_size: 24
  
  # Memory optimization
  memory_limit: "96GB"  # Leave 32GB for system
  cache_size_limit: "32GB"
  
  # I/O optimization
  io_buffer_size: "256MB"
  async_io: true
  use_memory_mapping: true
  direct_io: true
  
  # NUMA optimization
  numa_aware: true
  memory_allocation_policy: "local"
  
  # Work distribution
  dynamic_load_balancing: true
  work_stealing: true
  
  # Quality assessment
  quality:
    enable_quality_scoring: true
    quality_sampling:
      enabled: false  # Check everything
    approximate_scoring: false
    
processing:
  # All features enabled
  remove_duplicates: true
  duplicate_strategy: "semantic"  # Use ML-based deduplication
  fuzzy_threshold: 0.95
```

### Workstation (8-16 cores, 32-64GB RAM)

```yaml
# config/workstation_optimized.yaml
advanced:
  # Balanced parallelism
  max_workers: 12
  process_pool_size: 8
  
  # Memory optimization
  memory_limit: "48GB"
  cache_size_limit: "16GB"
  
  # I/O optimization
  io_buffer_size: "64MB"
  async_io: true
  use_memory_mapping: true
  
  # Quality assessment
  quality:
    enable_quality_scoring: true
    quality_sampling:
      enabled: true
      sample_rate: 0.1  # Check 10%
    approximate_scoring: false
    
processing:
  # Most features enabled
  remove_duplicates: true
  duplicate_strategy: "fuzzy"
  fuzzy_threshold: 0.9
```

### Desktop (4-8 cores, 8-16GB RAM)

```yaml
# config/desktop_optimized.yaml
advanced:
  # Conservative parallelism
  max_workers: 6
  process_pool_size: 4
  
  # Memory optimization
  memory_limit: "12GB"
  cache_size_limit: "4GB"
  
  # I/O optimization
  io_buffer_size: "16MB"
  async_io: true
  use_memory_mapping: false  # Slower on consumer SSDs
  
  # Quality assessment
  quality:
    enable_quality_scoring: true
    quality_sampling:
      enabled: true
      sample_rate: 0.05  # Check 5%
    approximate_scoring: true
    
processing:
  # Essential features only
  remove_duplicates: true
  duplicate_strategy: "exact"  # Fastest deduplication
```

### Laptop (2-4 cores, 4-8GB RAM)

```yaml
# config/laptop_optimized.yaml
advanced:
  # Minimal parallelism
  max_workers: 2
  process_pool_size: 1
  
  # Memory optimization
  memory_limit: "6GB"
  cache_size_limit: "1GB"
  
  # I/O optimization
  io_buffer_size: "4MB"
  async_io: false  # Avoid overhead
  use_memory_mapping: false
  
  # Power management
  cpu_governor: "balanced"  # Don't max out CPU
  
  # Quality assessment
  quality:
    enable_quality_scoring: false  # Disable for speed
    approximate_scoring: true
    
processing:
  # Minimal features
  remove_duplicates: false  # Disable expensive operations
  filter_min_length: 10
  require_pashto: false
```

## 📈 Scalability Strategies

### Horizontal Scaling

#### Distributed Processing

```python
import redis
import json
import hashlib
from typing import List, Dict

class DistributedProcessor:
    """Distribute processing across multiple machines"""
    
    def __init__(self, redis_config: Dict, worker_nodes: List[str]):
        self.redis_client = redis.Redict(**redis_config)
        self.worker_nodes = worker_nodes
        self.node_load = {node: 0 for node in worker_nodes}
    
    def distribute_work(self, work_items: List[Dict]) -> Dict[str, List]:
        """Distribute work items across worker nodes"""
        distributed_work = {node: [] for node in self.worker_nodes}
        
        for item in work_items:
            # Hash-based distribution for consistency
            item_hash = hashlib.md5(
                json.dumps(item, sort_keys=True).encode()
            ).hexdigest()
            
            # Select node with lowest load
            node = min(self.worker_nodes, key=lambda n: self.node_load[n])
            
            distributed_work[node].append(item)
            self.node_load[node] += 1
        
        return distributed_work
    
    def execute_distributed(self, distributed_work: Dict[str, List]) -> List[Dict]:
        """Execute work on distributed nodes"""
        import concurrent.futures
        
        results = []
        
        def execute_on_node(node: str, work_items: List) -> List:
            """Execute work on a specific node"""
            # Implementation would send work to remote node
            # For demo, we'll simulate with local execution
            return [process_item(item) for item in work_items]
        
        # Execute work on all nodes
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.worker_nodes)
        ) as executor:
            futures = {
                executor.submit(execute_on_node, node, items): node
                for node, items in distributed_work.items()
            }
            
            for future in concurrent.futures.as_completed(futures):
                node = futures[future]
                try:
                    results.extend(future.result())
                except Exception as e:
                    print(f"Node {node} failed: {e}")
        
        return results
```

#### Load Balancing

```python
class LoadBalancer:
    """Intelligent load balancing for processing tasks"""
    
    def __init__(self, workers: List[str]):
        self.workers = workers
        self.worker_stats = {w: {'load': 0, 'speed': 1.0} for w in workers}
    
    def get_optimal_worker(self, task_size: int, task_complexity: float) -> str:
        """Select optimal worker for a task"""
        
        # Calculate expected completion time for each worker
        completion_times = {}
        
        for worker in self.workers:
            stats = self.worker_stats[worker]
            
            # Expected time = (task_size * complexity) / (worker_speed * available_capacity)
            capacity = max(0.1, 1.0 - stats['load'])
            expected_time = (task_size * task_complexity) / (stats['speed'] * capacity)
            completion_times[worker] = expected_time
        
        # Return worker with shortest expected time
        return min(completion_times, key=completion_times.get)
    
    def update_worker_stats(self, worker: str, actual_time: float, 
                          task_size: int, task_complexity: float):
        """Update worker statistics after task completion"""
        stats = self.worker_stats[worker]
        
        # Update speed estimate
        estimated_time = (task_size * task_complexity)
        actual_speed = estimated_time / actual_time
        
        # Exponential moving average
        alpha = 0.1
        stats['speed'] = (1 - alpha) * stats['speed'] + alpha * actual_speed
        
        # Update load
        stats['load'] = min(1.0, stats['load'] + 0.1)
    
    def release_worker(self, worker: str):
        """Mark worker as available (load reduced)"""
        self.worker_stats[worker]['load'] = max(0, self.worker_stats[worker]['load'] - 0.2)
```

### Vertical Scaling

#### Dynamic Resource Allocation

```python
import psutil
import threading
import time
from typing import Dict, Any

class DynamicResourceManager:
    """Dynamically adjust resource allocation based on workload"""
    
    def __init__(self, pipeline, config: Dict):
        self.pipeline = pipeline
        self.config = config
        self.monitoring_active = False
        self.optimization_thread = None
        
    def start_monitoring(self):
        """Start resource monitoring and optimization"""
        self.monitoring_active = True
        self.optimization_thread = threading.Thread(target=self.optimization_loop)
        self.optimization_thread.daemon = True
        self.optimization_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        if self.optimization_thread:
            self.optimization_thread.join()
    
    def optimization_loop(self):
        """Main optimization loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                
                # Make optimization decisions
                decisions = self.make_optimization_decisions(metrics)
                
                # Apply optimizations
                for decision in decisions:
                    self.apply_optimization(decision)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Optimization error: {e}")
                time.sleep(60)
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current system and pipeline metrics"""
        return {
            # System metrics
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters(),
            'network_io': psutil.net_io_counters(),
            
            # Pipeline metrics
            'processing_rate': self.pipeline.get_processing_rate(),
            'queue_size': self.pipeline.get_queue_size(),
            'worker_utilization': self.pipeline.get_worker_utilization(),
            'error_rate': self.pipeline.get_error_rate()
        }
    
    def make_optimization_decisions(self, metrics: Dict[str, Any]) -> List[Dict]:
        """Make optimization decisions based on metrics"""
        decisions = []
        
        # CPU optimization
        if metrics['cpu_percent'] < 0.5 and metrics['worker_utilization'] < 0.8:
            decisions.append({
                'type': 'increase_workers',
                'reason': 'Low CPU usage with idle workers'
            })
        elif metrics['cpu_percent'] > 0.9:
            decisions.append({
                'type': 'decrease_workers',
                'reason': 'High CPU usage'
            })
        
        # Memory optimization
        if metrics['memory_percent'] > 0.85:
            decisions.append({
                'type': 'reduce_batch_size',
                'reason': 'High memory usage'
            })
        elif metrics['memory_percent'] < 0.6:
            decisions.append({
                'type': 'increase_batch_size',
                'reason': 'Available memory'
            })
        
        # Quality optimization
        if metrics['processing_rate'] < 50 and metrics['worker_utilization'] > 0.9:
            decisions.append({
                'type': 'skip_quality_checks',
                'reason': 'High load, skip expensive operations'
            })
        elif metrics['processing_rate'] > 200 and metrics['memory_percent'] < 0.7:
            decisions.append({
                'type': 'enable_quality_checks',
                'reason': 'Low load, enable quality assessment'
            })
        
        return decisions
    
    def apply_optimization(self, decision: Dict):
        """Apply optimization decision"""
        if decision['type'] == 'increase_workers':
            new_count = min(self.config['max_workers'], 
                          self.pipeline.get_worker_count() + 1)
            self.pipeline.set_worker_count(new_count)
            print(f"Increased workers to {new_count}")
        
        elif decision['type'] == 'decrease_workers':
            new_count = max(1, self.pipeline.get_worker_count() - 1)
            self.pipeline.set_worker_count(new_count)
            print(f"Decreased workers to {new_count}")
        
        elif decision['type'] == 'reduce_batch_size':
            new_size = max(10, self.pipeline.get_batch_size() // 2)
            self.pipeline.set_batch_size(new_size)
            print(f"Reduced batch size to {new_size}")
        
        elif decision['type'] == 'increase_batch_size':
            new_size = min(self.config['max_batch_size'], 
                         self.pipeline.get_batch_size() * 2)
            self.pipeline.set_batch_size(new_size)
            print(f"Increased batch size to {new_size}")
        
        elif decision['type'] == 'skip_quality_checks':
            self.pipeline.set_quality_scoring_enabled(False)
            print("Disabled quality scoring")
        
        elif decision['type'] == 'enable_quality_checks':
            self.pipeline.set_quality_scoring_enabled(True)
            print("Enabled quality scoring")
```

## 📊 Monitoring and Benchmarking

### Performance Monitoring

#### Real-time Monitoring

```python
import time
import psutil
from typing import Dict, List
import json

class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size  # seconds
        self.metrics_history = []
        self.start_time = time.time()
        
    def record_metrics(self, **metrics):
        """Record current performance metrics"""
        current_metrics = {
            'timestamp': time.time(),
            'uptime': time.time() - self.start_time,
            **metrics
        }
        
        self.metrics_history.append(current_metrics)
        
        # Keep only recent metrics
        cutoff_time = time.time() - self.window_size
        self.metrics_history = [
            m for m in self.metrics_history 
            if m['timestamp'] > cutoff_time
        ]
    
    def get_current_stats(self) -> Dict:
        """Get current performance statistics"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 entries
        
        return {
            'cpu_usage': {
                'current': psutil.cpu_percent(),
                'average': sum(m.get('cpu_usage', 0) for m in recent_metrics) / len(recent_metrics)
            },
            'memory_usage': {
                'current': psutil.virtual_memory().percent,
                'average': sum(m.get('memory_usage', 0) for m in recent_metrics) / len(recent_metrics)
            },
            'throughput': {
                'items_per_second': sum(m.get('items_processed', 0) for m in recent_metrics) / len(recent_metrics),
                'average': sum(m.get('throughput', 0) for m in recent_metrics) / len(recent_metrics)
            },
            'errors': {
                'rate': sum(m.get('errors', 0) for m in recent_metrics) / len(recent_metrics)
            }
        }
    
    def get_performance_report(self) -> str:
        """Generate performance report"""
        stats = self.get_current_stats()
        
        report = f"""
Performance Report
==================
Uptime: {stats.get('uptime', 0):.1f} seconds
CPU Usage: {stats['cpu_usage']['current']:.1f}% (avg: {stats['cpu_usage']['average']:.1f}%)
Memory Usage: {stats['memory_usage']['current']:.1f}% (avg: {stats['memory_usage']['average']:.1f}%)
Throughput: {stats['throughput']['items_per_second']:.1f} items/sec (avg: {stats['throughput']['average']:.1f})
Error Rate: {stats['errors']['rate']:.3f} errors/sec
        """
        
        return report.strip()
    
    def save_metrics(self, filename: str):
        """Save metrics to file"""
        with open(filename, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
```

#### Benchmark Suite

```python
import time
import statistics
from typing import List, Dict, Callable
import subprocess
import psutil

class BenchmarkSuite:
    """Comprehensive benchmarking for pipeline performance"""
    
    def __init__(self):
        self.results = {}
        
    def benchmark_processing_speed(self, pipeline, test_data: List[str], 
                                 iterations: int = 3) -> Dict:
        """Benchmark processing speed"""
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            # Run pipeline
            pipeline.run('test_input/', 'test_output/')
            
            end_time = time.time()
            processing_time = end_time - start_time
            times.append(processing_time)
        
        return {
            'mean_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'throughput': len(test_data) / statistics.mean(times)
        }
    
    def benchmark_memory_usage(self, pipeline, large_dataset: List[str]) -> Dict:
        """Benchmark memory usage"""
        process = psutil.Process()
        
        # Measure memory before
        initial_memory = process.memory_info().rss
        
        # Run pipeline
        pipeline.run('large_input/', 'large_output/')
        
        # Measure memory after
        final_memory = process.memory_info().rss
        
        return {
            'initial_memory_mb': initial_memory / 1024**2,
            'final_memory_mb': final_memory / 1024**2,
            'memory_increase_mb': (final_memory - initial_memory) / 1024**2,
            'memory_per_item_mb': (final_memory - initial_memory) / len(large_dataset) / 1024**2
        }
    
    def benchmark_scalability(self, pipeline, datasets: Dict[str, List[str]]) -> Dict:
        """Benchmark scalability with different dataset sizes"""
        scalability_results = {}
        
        for size_name, dataset in datasets.items():
            print(f"Benchmarking {size_name} dataset ({len(dataset)} items)...")
            
            start_time = time.time()
            pipeline.run(f'{size_name}_input/', f'{size_name}_output/')
            end_time = time.time()
            
            scalability_results[size_name] = {
                'size': len(dataset),
                'time': end_time - start_time,
                'throughput': len(dataset) / (end_time - start_time)
            }
        
        return scalability_results
    
    def generate_benchmark_report(self, results: Dict, output_file: str):
        """Generate comprehensive benchmark report"""
        report = f"""
# Pashto Dataset Pipeline - Benchmark Report

## System Information
- CPU Cores: {psutil.cpu_count()}
- Memory: {psutil.virtual_memory().total / 1024**3:.1f} GB
- Platform: {psutil.platform.platform()}

## Processing Speed Results
{self._format_results_table(results.get('processing_speed', {}))}

## Memory Usage Results
{self._format_memory_results(results.get('memory_usage', {}))}

## Scalability Results
{self._format_scalability_results(results.get('scalability', {}))}

## Recommendations
{self._generate_recommendations(results)}
        """
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"Benchmark report saved to {output_file}")
    
    def _format_results_table(self, results: Dict) -> str:
        """Format processing speed results as table"""
        if not results:
            return "No processing speed data available."
        
        return f"""
| Metric | Value |
|--------|-------|
| Mean Time | {results['mean_time']:.2f}s |
| Median Time | {results['median_time']:.2f}s |
| Min Time | {results['min_time']:.2f}s |
| Max Time | {results['max_time']:.2f}s |
| Std Dev | {results['std_dev']:.2f}s |
| Throughput | {results['throughput']:.1f} items/sec |
        """
    
    def _format_memory_results(self, results: Dict) -> str:
        """Format memory usage results"""
        if not results:
            return "No memory usage data available."
        
        return f"""
| Metric | Value |
|--------|-------|
| Initial Memory | {results['initial_memory_mb']:.1f} MB |
| Final Memory | {results['final_memory_mb']:.1f} MB |
| Memory Increase | {results['memory_increase_mb']:.1f} MB |
| Memory per Item | {results['memory_per_item_mb']:.3f} MB |
        """
    
    def _format_scalability_results(self, results: Dict) -> str:
        """Format scalability results"""
        if not results:
            return "No scalability data available."
        
        table = "| Dataset | Size | Time | Throughput |\n"
        table += "|---------|------|------|------------|\n"
        
        for size_name, data in results.items():
            table += f"| {size_name} | {data['size']} | {data['time']:.2f}s | {data['throughput']:.1f}/sec |\n"
        
        return table
    
    def _generate_recommendations(self, results: Dict) -> str:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Memory recommendations
        if 'memory_usage' in results:
            mem_increase = results['memory_usage']['memory_increase_mb']
            if mem_increase > 1000:  # 1GB
                recommendations.append("- Consider reducing batch size for memory efficiency")
        
        # Throughput recommendations
        if 'processing_speed' in results:
            throughput = results['processing_speed']['throughput']
            if throughput < 50:
                recommendations.append("- Consider increasing worker count for better throughput")
        
        # Scalability recommendations
        if 'scalability' in results:
            scalability_data = list(results['scalability'].values())
            if len(scalability_data) >= 2:
                # Check if processing time scales linearly
                time_ratio = scalability_data[1]['time'] / scalability_data[0]['time']
                size_ratio = scalability_data[1]['size'] / scalability_data[0]['size']
                
                if time_ratio > size_ratio * 1.5:
                    recommendations.append("- Consider parallel processing for better scalability")
        
        return "\n".join(recommendations) if recommendations else "- System is well optimized for current workload."
```

### Usage

```python
# Run comprehensive benchmark
def run_performance_benchmark():
    """Run complete performance benchmark"""
    
    # Setup
    monitor = PerformanceMonitor()
    benchmark = BenchmarkSuite()
    
    # Create test data
    test_data = create_test_dataset(size=1000)
    large_data = create_test_dataset(size=10000)
    datasets = {
        'small': create_test_dataset(size=100),
        'medium': create_test_dataset(size=1000),
        'large': create_test_dataset(size=10000)
    }
    
    # Run benchmarks
    print("Running processing speed benchmark...")
    speed_results = benchmark.benchmark_processing_speed(pipeline, test_data)
    
    print("Running memory usage benchmark...")
    memory_results = benchmark.benchmark_memory_usage(pipeline, large_data)
    
    print("Running scalability benchmark...")
    scalability_results = benchmark.benchmark_scalability(pipeline, datasets)
    
    # Generate report
    results = {
        'processing_speed': speed_results,
        'memory_usage': memory_results,
        'scalability': scalability_results
    }
    
    benchmark.generate_benchmark_report(results, 'performance_benchmark_report.md')
    
    # Display current stats
    print(monitor.get_performance_report())

if __name__ == "__main__":
    run_performance_benchmark()
```

This comprehensive performance optimization guide provides:

- **Memory optimization** strategies for different RAM configurations
- **CPU optimization** techniques for multi-core systems  
- **I/O optimization** for various storage types
- **Network optimization** for web scraping
- **Hardware-specific** configurations for different setups
- **Scalability strategies** for horizontal and vertical scaling
- **Monitoring tools** for real-time performance tracking
- **Benchmarking suite** for performance analysis

The guide includes practical code examples and configuration files that can be directly applied to optimize pipeline performance for any use case or hardware configuration.