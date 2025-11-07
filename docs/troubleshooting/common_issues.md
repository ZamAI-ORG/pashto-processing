# Common Issues and Troubleshooting

This guide helps you identify and resolve common issues when using the Pashto Dataset Pipeline.

## 📋 Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Problems](#configuration-problems)
- [Processing Errors](#processing-errors)
- [Performance Issues](#performance-issues)
- [Memory Problems](#memory-problems)
- [Encoding and Text Issues](#encoding-and-text-issues)
- [Quality Assessment Problems](#quality-assessment-problems)
- [Output and File Issues](#output-and-file-issues)
- [Network and Web Scraping Issues](#network-and-web-scraping-issues)
- [Database Connection Issues](#database-connection-issues)
- [System Requirements Issues](#system-requirements-issues)

## 🛠️ Installation Issues

### Problem: Pipeline command not found

**Symptoms:**
```bash
$ pashto-pipeline --version
bash: pashto-pipeline: command not found
```

**Solutions:**

1. **Check installation:**
```bash
pip list | grep pashto-dataset-pipeline
```

2. **Reinstall the package:**
```bash
pip uninstall pashto-dataset-pipeline
pip install pashto-dataset-pipeline
```

3. **Add to PATH (if installed in user directory):**
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

4. **Use Python module directly:**
```bash
python -m pashto_pipeline --version
```

### Problem: Python version incompatibility

**Symptoms:**
```
ERROR: Package requires a different Python: 3.7.0 not in '>=3.8'
```

**Solutions:**

1. **Check Python version:**
```bash
python --version
```

2. **Upgrade Python:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9

# macOS with Homebrew
brew install python@3.9

# Windows - download from python.org
```

3. **Use specific Python version:**
```bash
python3.9 -m pip install pashto-dataset-pipeline
```

### Problem: Permission denied during installation

**Symptoms:**
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use user installation:**
```bash
pip install --user pashto-dataset-pipeline
```

2. **Create virtual environment:**
```bash
python -m venv pashto-env
source pashto-env/bin/activate  # Linux/macOS
# pashto-env\Scripts\activate    # Windows
pip install pashto-dataset-pipeline
```

3. **Fix permissions:**
```bash
sudo chown -R $USER:$USER ~/.local
```

### Problem: Missing system dependencies

**Symptoms:**
```
ERROR: Failed building wheel for pashto-dataset-pipeline
```

**Solutions:**

1. **Install build tools:**
```bash
# Ubuntu/Debian
sudo apt install python3-dev build-essential

# CentOS/RHEL
sudo yum install python3-devel gcc

# macOS
xcode-select --install
```

2. **Install system libraries:**
```bash
# For text processing
sudo apt install libxml2-dev libxslt-dev

# For PDF processing
sudo apt install poppler-utils

# For web scraping
sudo apt install chromium-browser
```

## ⚙️ Configuration Problems

### Problem: Configuration file not found

**Symptoms:**
```
ERROR: Configuration file not found: config.yaml
```

**Solutions:**

1. **Check file path:**
```bash
ls -la config.yaml
```

2. **Use absolute path:**
```bash
pashto-pipeline process --config /full/path/to/config.yaml
```

3. **Create default config:**
```bash
pashto-pipeline create-config --output config.yaml
```

### Problem: Configuration validation errors

**Symptoms:**
```
ERROR: Configuration validation failed: Invalid value for 'max_workers'
```

**Solutions:**

1. **Validate configuration:**
```bash
pashto-pipeline validate-config --file config.yaml
```

2. **Check configuration schema:**
```yaml
# Correct format
advanced:
  max_workers: 4           # Integer
  batch_size: 100          # Integer
  memory_limit: "2GB"      # String with units
```

3. **Fix type mismatches:**
```yaml
# Wrong
max_workers: "4"           # String instead of integer
batch_size: true           # Boolean instead of integer

# Correct
max_workers: 4             # Integer
batch_size: 100            # Integer
```

### Problem: Environment variable conflicts

**Symptoms:**
```
WARNING: Environment variable overrides config value
```

**Solutions:**

1. **Check environment variables:**
```bash
env | grep PASHTOPIPELINE
```

2. **Clear conflicting variables:**
```bash
unset PASHTOPIPELINE_MAX_WORKERS
unset PASHTOPIPELINE_CONFIG_DIR
```

3. **Set correct values:**
```bash
export PASHTOPIPELINE_CONFIG_DIR="/path/to/config"
```

## 🔄 Processing Errors

### Problem: Processing stops with errors

**Symptoms:**
```
ERROR: Processing failed at file sample.txt
CRITICAL: Pipeline execution stopped
```

**Solutions:**

1. **Continue on errors:**
```yaml
# config.yaml
pipeline:
  stop_on_error: false     # Continue processing
  continue_on_warning: true
  max_retries: 3
```

2. **Check individual file:**
```bash
pashto-pipeline process-file --input sample.txt --config config.yaml
```

3. **Enable debug logging:**
```yaml
# config.yaml
logging:
  level: "DEBUG"
```

### Problem: Input files not processed

**Symptoms:**
```
INFO: Found 0 input files
WARNING: No files match the specified patterns
```

**Solutions:**

1. **Check input directory:**
```bash
ls -la data/raw/
```

2. **Verify file patterns:**
```yaml
# config.yaml
input:
  include_patterns: ["*.txt", "*.json"]  # Correct patterns
  exclude_patterns: ["*.tmp", "*.bak"]   # Exclusion patterns
```

3. **Check file permissions:**
```bash
chmod 644 data/raw/*
chmod 755 data/raw/
```

### Problem: Processing timeouts

**Symptoms:**
```
ERROR: Processing timeout after 300 seconds
```

**Solutions:**

1. **Increase timeout:**
```yaml
# config.yaml
advanced:
  timeout: 600  # 10 minutes
```

2. **Optimize batch size:**
```yaml
# config.yaml
advanced:
  batch_size: 50    # Smaller batches
  max_workers: 2    # Fewer workers
```

3. **Use streaming mode:**
```yaml
# config.yaml
advanced:
  streaming_mode: true
  stream_chunk_size: 1000
```

## ⚡ Performance Issues

### Problem: Slow processing speed

**Symptoms:**
```
INFO: Processing rate: 10 items/second (expected: 100 items/second)
```

**Solutions:**

1. **Increase workers:**
```yaml
# config.yaml
advanced:
  max_workers: 8    # Use more CPU cores
  use_multiprocessing: true
```

2. **Optimize I/O:**
```yaml
# config.yaml
advanced:
  io_buffer_size: "32MB"  # Larger buffer
  async_io: true          # Asynchronous I/O
```

3. **Disable expensive operations:**
```yaml
# config.yaml
processing:
  check_spellings: false      # Disable spell checking
  grammar_check: false        # Disable grammar check
  require_pashto: false       # Skip language detection
```

### Problem: High CPU usage

**Symptoms:**
```
CPU usage: 95% for extended periods
System becomes unresponsive
```

**Solutions:**

1. **Reduce worker count:**
```yaml
# config.yaml
advanced:
  max_workers: 2    # Fewer workers
  process_pool_size: 1
```

2. **Enable CPU throttling:**
```yaml
# config.yaml
advanced:
  cpu_throttle: true
  max_cpu_usage: 80  # Maximum 80% CPU usage
```

3. **Use lower priority:**
```bash
nice -n 10 pashto-pipeline process --config config.yaml
```

### Problem: Disk I/O bottleneck

**Symptoms:**
```
INFO: I/O wait time: 80% of processing time
Disk usage: 100%
```

**Solutions:**

1. **Use faster storage:**
```bash
# Move data to SSD
mv data/ /mnt/ssd/data/

# Use RAM disk for temporary data
sudo mount -t tmpfs -o size=10G tmpfs /tmp/pashto_cache
```

2. **Enable memory mapping:**
```yaml
# config.yaml
advanced:
  use_memory_mapping: true
  memory_mapped_io: true
```

3. **Reduce I/O operations:**
```yaml
# config.yaml
advanced:
  cache_intermediate_results: false  # Don't cache
  compress_output: true              # Compress to reduce I/O
```

## 💾 Memory Problems

### Problem: Out of memory errors

**Symptoms:**
```
ERROR: Memory allocation failed
Killed process (OOM killer)
```

**Solutions:**

1. **Reduce batch size:**
```yaml
# config.yaml
advanced:
  batch_size: 50      # Smaller batches
  memory_limit: "1GB" # Explicit memory limit
```

2. **Enable streaming:**
```yaml
# config.yaml
advanced:
  streaming_mode: true
  stream_processing: true
  garbage_collect_frequency: 10  # Frequent GC
```

3. **Use memory-efficient mode:**
```yaml
# config.yaml
processing:
  remove_duplicates: false       # Disable memory-intensive operations
  enable_caching: false          # Don't cache
```

### Problem: Memory leaks

**Symptoms:**
```
Memory usage continuously increases
System runs out of memory over time
```

**Solutions:**

1. **Enable aggressive garbage collection:**
```yaml
# config.yaml
advanced:
  aggressive_gc: true
  gc_frequency: 10      # GC every 10 items
```

2. **Restart processing periodically:**
```bash
# Process in chunks
for dir in data/batch_*/; do
    pashto-pipeline process --input "$dir" --output "processed/$(basename "$dir")"
    # Cleanup memory
    python -c "import gc; gc.collect()"
done
```

3. **Monitor memory usage:**
```bash
# Monitor memory usage
watch -n 1 'ps aux | grep pashto-pipeline | awk "{print \$4, \$11}"'
```

## 📝 Encoding and Text Issues

### Problem: Character encoding errors

**Symptoms:**
```
ERROR: Invalid UTF-8 byte sequence
WARNING: Character encoding conversion failed
```

**Solutions:**

1. **Specify encoding explicitly:**
```yaml
# config.yaml
input:
  encoding: "utf-8"           # Primary encoding
  encoding_fallback:          # Fallback encodings
    - "utf-16"
    - "cp1256"
    - "iso-8859-1"
```

2. **Fix encoding in source files:**
```bash
# Convert to UTF-8
iconv -f cp1256 -t utf-8 input.txt > input_utf8.txt

# Bulk conversion
find data/ -name "*.txt" -exec iconv -f cp1256 -t utf-8 {} -o {}.utf8 \;
```

3. **Handle encoding errors:**
```yaml
# config.yaml
input:
  encoding_errors: "ignore"   # or "replace", "strict"
```

### Problem: Pashto text not recognized

**Symptoms:**
```
WARNING: Pashto ratio below threshold: 0.3 (expected: 0.7)
```

**Solutions:**

1. **Adjust Pashto ratio threshold:**
```yaml
# config.yaml
processing:
  require_pashto: true
  min_pashto_ratio: 0.5       # Lower threshold
```

2. **Check language detection:**
```bash
# Test language detection
echo "زموږ ژبه ښه ده" | pashto-pipeline detect-language
```

3. **Update language detection model:**
```bash
pip install --upgrade pashto-dataset-pipeline[ml]
```

### Problem: Unicode normalization issues

**Symptoms:**
```
Text appears corrupted after processing
Duplicate characters or missing diacritics
```

**Solutions:**

1. **Disable normalization:**
```yaml
# config.yaml
processing:
  normalize_text: false
```

2. **Use specific normalization form:**
```yaml
# config.yaml
processing:
  normalization_form: "NFC"    # Use NFC form
```

3. **Manual normalization:**
```bash
# Install unicode normalization tools
pip install uniseg

# Normalize manually
python -c "import uniseg; print(uniseg.text.normalize('NFC', 'text'))"
```

## 🎯 Quality Assessment Problems

### Problem: Quality scores too low

**Symptoms:**
```
WARNING: Average quality score: 0.4 (threshold: 0.6)
```

**Solutions:**

1. **Lower quality threshold:**
```yaml
# config.yaml
quality:
  min_quality_score: 0.3      # Lower threshold
```

2. **Disable expensive quality checks:**
```yaml
# config.yaml
quality:
  check_spellings: false       # Disable spell checking
  grammar_check: false         # Disable grammar check
```

3. **Use approximate scoring:**
```yaml
# config.yaml
quality:
  approximate_scoring: true    # Fast approximate scoring
```

### Problem: Quality assessment takes too long

**Symptoms:**
```
INFO: Quality assessment: 45% complete (estimated 2 hours remaining)
```

**Solutions:**

1. **Enable sampling:**
```yaml
# config.yaml
quality:
  quality_sampling:
    enabled: true
    sample_rate: 0.1           # Check 10% of data
```

2. **Use fast quality checks:**
```yaml
# config.yaml
quality:
  fast_quality_check: true
  skip_deep_analysis: true
```

3. **Disable quality assessment:**
```yaml
# config.yaml
quality:
  enable_quality_scoring: false
```

## 📁 Output and File Issues

### Problem: Output files not created

**Symptoms:**
```
WARNING: Output directory is empty
ERROR: Cannot write to output directory
```

**Solutions:**

1. **Check directory permissions:**
```bash
mkdir -p data/output
chmod 755 data/output
```

2. **Verify output configuration:**
```yaml
# config.yaml
output:
  data_directory: "data/output"   # Correct path
  create_subdirs: true            # Auto-create subdirs
```

3. **Use absolute paths:**
```yaml
# config.yaml
output:
  data_directory: "/full/path/to/output"
```

### Problem: Incorrect output format

**Symptoms:**
```
Expected JSON output, got CSV
Missing metadata in output
```

**Solutions:**

1. **Check output configuration:**
```yaml
# config.yaml
output:
  format: "json"                  # Specify format
  include_metadata: true          # Include metadata
  pretty_print: false             # Minified output
```

2. **Verify file extensions:**
```bash
# Correct naming
echo '{"data": []}' > output.json
echo "text1,text2" > output.csv
```

### Problem: Large output files

**Symptoms:**
```
Output file size: 10GB (expected: 1GB)
Disk space running out
```

**Solutions:**

1. **Enable compression:**
```yaml
# config.yaml
output:
  compress_output: true
  compression_format: "gzip"
```

2. **Reduce output data:**
```yaml
# config.yaml
output:
  include_metadata: false         # Exclude metadata
  include_statistics: false       # Exclude statistics
```

3. **Use streaming output:**
```yaml
# config.yaml
advanced:
  streaming_output: true
  shard_output: true              # Split into multiple files
  shard_size: 10000               # 10k records per file
```

## 🌐 Network and Web Scraping Issues

### Problem: Web scraping timeouts

**Symptoms:**
```
ERROR: Request timeout after 30 seconds
WARNING: Skipping URL: https://example.com (timeout)
```

**Solutions:**

1. **Increase timeout:**
```yaml
# config.yaml
input:
  scraping:
    rate_limiting:
      timeout: 60                 # 1 minute timeout
      delay_between_requests: 5   # Longer delays
```

2. **Use proxy:**
```yaml
# config.yaml
input:
  scraping:
    proxy:
      enabled: true
      proxy_url: "http://proxy:8080"
```

3. **Respect robots.txt:**
```yaml
# config.yaml
input:
  scraping:
    rate_limiting:
      respect_robots_txt: true    # Be respectful
      user_agent: "PashtoBot/1.0" # Identify bot
```

### Problem: Blocked by websites

**Symptoms:**
```
ERROR: HTTP 403 Forbidden
WARNING: Access denied to target website
```

**Solutions:**

1. **Use rotating user agents:**
```yaml
# config.yaml
input:
  scraping:
    browser:
      user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      rotate_user_agents: true
```

2. **Add delays:**
```yaml
# config.yaml
input:
  scraping:
    rate_limiting:
      requests_per_second: 0.1    # Very slow
      delay_between_requests: 10  # 10 seconds between requests
```

3. **Use residential proxy:**
```yaml
# config.yaml
input:
  scraping:
    proxy:
      enabled: true
      proxy_type: "residential"    # Use residential proxies
```

### Problem: JavaScript content not loaded

**Symptoms:**
```
WARNING: JavaScript content may be missing
Extracted text appears incomplete
```

**Solutions:**

1. **Enable JavaScript:**
```yaml
# config.yaml
input:
  scraping:
    browser:
      javascript_enabled: true
      wait_time: 10               # Wait for content to load
      wait_until: "networkidle"   # Wait for network idle
```

2. **Scroll for infinite content:**
```yaml
# config.yaml
input:
  scraping:
    javascript:
      scroll_enabled: true
      scroll_pause_time: 3
      max_scrolls: 5
```

## 🗄️ Database Connection Issues

### Problem: Database connection failed

**Symptoms:**
```
ERROR: Could not connect to database
FATAL: password authentication failed
```

**Solutions:**

1. **Check connection string:**
```yaml
# config.yaml
database:
  connection_url: "postgresql://user:password@host:port/database"
```

2. **Test connection manually:**
```bash
# Test PostgreSQL
psql "postgresql://user:password@host:port/database" -c "SELECT 1;"

# Test MySQL
mysql -h host -u user -p database -e "SELECT 1;"
```

3. **Check credentials:**
```bash
# Verify user exists
psql -U postgres -c "\du"
```

### Problem: Database queries time out

**Symptoms:**
```
ERROR: Query timeout after 30 seconds
WARNING: Large table scan detected
```

**Solutions:**

1. **Add database indexes:**
```sql
-- Add indexes for better performance
CREATE INDEX idx_text_content ON pashto_dataset(text_content);
CREATE INDEX idx_quality_score ON pashto_dataset(quality_score);
```

2. **Use batch processing:**
```yaml
# config.yaml
database:
  batch_insert_size: 1000
  query_timeout: 300
```

3. **Optimize queries:**
```yaml
# config.yaml
processing:
  batch_processing: true
  chunk_size: 5000
```

## 🖥️ System Requirements Issues

### Problem: Insufficient disk space

**Symptoms:**
```
ERROR: No space left on device
WARNING: Disk space below threshold: 5%
```

**Solutions:**

1. **Clean up temporary files:**
```bash
# Clean system temp
sudo apt clean
sudo apt autoremove

# Clean pip cache
pip cache purge

# Clean project temp
rm -rf tmp/ cache/ logs/*.log
```

2. **Use compression:**
```yaml
# config.yaml
output:
  compress_output: true
  compression_format: "gzip"
```

3. **Use external storage:**
```bash
# Mount external drive
sudo mount /dev/sdb1 /mnt/external
mv data/ /mnt/external/
```

### Problem: Insufficient permissions

**Symptoms:**
```
ERROR: Permission denied: /var/log/pashto-pipeline
WARNING: Cannot create output directory
```

**Solutions:**

1. **Fix file permissions:**
```bash
# Fix ownership
sudo chown -R $USER:$USER /opt/pashto-pipeline/

# Fix permissions
chmod -R 755 /opt/pashto-pipeline/
chmod 600 /opt/pashto-pipeline/config/*.yaml
```

2. **Use user directories:**
```yaml
# config.yaml
output:
  data_directory: "/home/user/pashto_output"
logging:
  file: "/home/user/pashto.log"
```

3. **Run with sudo (temporary):**
```bash
sudo pashto-pipeline process --config config.yaml
```

### Problem: Missing system libraries

**Symptoms:**
```
ERROR: Shared library not found: libpq.so.5
ERROR: Missing dependency: libxml2.so
```

**Solutions:**

1. **Install system libraries:**
```bash
# Ubuntu/Debian
sudo apt install libpq-dev libxml2-dev

# CentOS/RHEL
sudo yum install postgresql-libs libxml2-devel

# macOS
brew install postgresql libxml2
```

2. **Set library path:**
```bash
# Add to LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
```

3. **Reinstall with system packages:**
```bash
# Use system package manager
sudo apt install python3-pashto-pipeline
```

## 🔧 Diagnostic Tools

### System Information

```bash
# Collect system information
pashto-pipeline system-info

# Check Python environment
python -c "import sys, platform; print(f'Python: {sys.version}'); print(f'Platform: {platform.platform()}')"

# Check memory usage
free -h
df -h
```

### Configuration Validation

```bash
# Validate configuration
pashto-pipeline validate-config --file config.yaml

# Test with sample data
pashto-pipeline test-config --config config.yaml --sample-data data/sample/
```

### Performance Testing

```bash
# Run benchmark
pashto-pipeline benchmark --input data/sample/ --config config.yaml

# Monitor resource usage
pashto-pipeline process --config config.yaml --monitor-resources
```

### Debug Mode

```bash
# Enable debug logging
pashto-pipeline process --config config.yaml --log-level DEBUG

# Run in verbose mode
pashto-pipeline process --config config.yaml --verbose --debug
```

## 📞 Getting Help

If you continue to experience issues:

1. **Check the logs:**
```bash
tail -f logs/pipeline.log
```

2. **Collect diagnostic information:**
```bash
pashto-pipeline system-info > system_report.txt
```

3. **Create a minimal reproduction:**
```bash
# Create minimal config and data
cp config.yaml minimal_config.yaml
# Edit to use minimal settings
echo "زموږ ژبه ښه ده" > minimal_input.txt
```

4. **Search existing issues:**
   - GitHub Issues: https://github.com/your-org/pashto-dataset-pipeline/issues
   - Documentation: https://docs.pashto-pipeline.org

5. **Create a new issue with:**
   - System information
   - Configuration file (redacted)
   - Error messages
   - Steps to reproduce
   - Expected vs actual behavior

## 📚 Additional Resources

- [Installation Guide](../guides/installation.md)
- [Configuration Guide](../guides/configuration.md)
- [Best Practices](../guides/best_practices.md)
- [API Reference](../api/README.md)
- [Examples Directory](../examples/)