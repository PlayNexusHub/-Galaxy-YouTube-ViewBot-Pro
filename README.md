# 🌌 Galaxy YouTube ViewBot Pro

Advanced YouTube view generation tool integrated into NexusHub with AI-powered features and multi-threading capabilities.

## Features

### 🎯 Core Functionality
- **Multi-Video Queue**: Process multiple videos in sequence
- **Concurrent Views**: Generate multiple views simultaneously
- **User-Agent Spoofing**: Rotate between different browser signatures
- **Proxy Support**: Use proxy servers for IP rotation
- **Adjustable Watch Time**: Customize viewing duration
- **Headless Mode**: Run without visible browser windows
- **Incognito Mode**: Private browsing sessions

### 🚀 Advanced Features
- **Auto-Like**: Automatically like videos after viewing
- **Auto-Subscribe**: Subscribe to channels automatically
- **Auto-Comment**: Post comments on videos (requires login)
- **Random Watch Time**: Vary viewing duration for natural behavior
- **Live Stream Detection**: Identify and handle live content
- **Video Info Scraping**: Extract video metadata
- **Real-time Statistics**: Monitor performance metrics
- **Export Functionality**: Save logs and statistics

### 🛠️ Technical Features
- **Undetected ChromeDriver**: Bypass detection mechanisms
- **Multi-threading**: Handle multiple concurrent sessions
- **Resource Monitoring**: Track CPU and memory usage
- **Error Handling**: Robust error recovery and logging
- **Configuration Management**: Save and load settings
- **Queue Management**: Import/export video queues

## Usage

### Basic Operation
1. **Enter YouTube URL**: Paste any YouTube video URL
2. **Configure Settings**: Set watch time, delays, and features
3. **Start ViewBot**: Click "Start ViewBot" to begin
4. **Monitor Progress**: Watch real-time statistics and logs
5. **Stop When Done**: Click "Stop ViewBot" to end

### Advanced Usage

#### Queue Management
- **Add Single Video**: Use the main URL input
- **Bulk Import**: Add multiple URLs at once
- **Export/Import**: Save and load video queues
- **Queue Monitoring**: Track progress of queued videos

#### Settings Configuration
- **Watch Time**: Set minimum and maximum viewing duration
- **View Delay**: Configure delays between views
- **Concurrent Views**: Control number of simultaneous sessions
- **Proxy Settings**: Configure proxy server details
- **User Agent**: Select browser signature type

#### Feature Toggles
- **Headless Mode**: Run without visible browser
- **Incognito Mode**: Use private browsing sessions
- **Auto Actions**: Enable like, subscribe, comment features
- **Cache Management**: Clear cache and cookies
- **Audio Control**: Mute audio during viewing

## Installation

### Prerequisites
- Python 3.7 or higher
- Chrome browser installed
- Internet connection

### Dependencies
```bash
pip install -r requirements.txt
```

### Required Packages
- `PyQt5==5.15.9`: GUI framework
- `undetected-chromedriver==3.5.3`: Undetected browser automation

## Configuration

### Basic Settings
- **Watch Time**: 5-300 seconds (default: 15)
- **View Delay**: 1-60 seconds (default: 2)
- **Concurrent Views**: 1-20 sessions (default: 5)
- **Max Views**: 1-1000 total views (default: 100)

### Advanced Settings
- **Proxy Server**: Format: `ip:port` or `username:password@ip:port`
- **User Agent**: Random, Chrome, Firefox, Safari, Mobile
- **Min/Max Watch Time**: Range for random watch time
- **Comment Text**: Custom comment for auto-comment feature

### Feature Settings
- **Clear Cache**: Automatically clear browser cache
- **Clear Cookies**: Remove cookies between sessions
- **Mute Audio**: Disable audio during viewing
- **Minimize Window**: Hide browser windows
- **Save Logs**: Automatically save activity logs

## Statistics

### Real-time Metrics
- **Total Views**: Cumulative view count
- **Active Threads**: Currently running sessions
- **Success Rate**: Percentage of successful views
- **Queue Length**: Number of videos in queue

### Performance Metrics
- **Views Today**: Views generated today
- **Views This Week**: Weekly view count
- **Total Errors**: Number of failed attempts
- **Average Watch Time**: Mean viewing duration
- **CPU Usage**: System resource consumption
- **Memory Usage**: RAM utilization

## Safety Features

### Detection Avoidance
- **Undetected ChromeDriver**: Bypass bot detection
- **User-Agent Rotation**: Vary browser signatures
- **Random Delays**: Natural timing patterns
- **Proxy Rotation**: IP address variation
- **Session Management**: Proper cleanup between sessions

### Error Handling
- **Automatic Retry**: Retry failed operations
- **Error Logging**: Detailed error tracking
- **Graceful Degradation**: Continue on partial failures
- **Resource Cleanup**: Proper memory management

## Export Options

### Data Export
- **Queue Export**: Save video queue as JSON
- **Statistics Export**: Export performance metrics
- **Log Export**: Download activity logs
- **Settings Export**: Backup configuration

### File Formats
- **JSON**: Structured data export
- **TXT**: Plain text logs
- **CSV**: Tabular statistics

## Troubleshooting

### Common Issues
1. **Chrome Not Found**: Ensure Chrome is installed
2. **Proxy Connection Failed**: Check proxy settings
3. **Rate Limiting**: Reduce concurrent views
4. **Memory Issues**: Lower concurrent session count
5. **Detection**: Enable more randomization features

### Performance Optimization
- **Reduce Concurrent Views**: Lower for stability
- **Increase Delays**: More natural timing
- **Use Proxies**: Distribute load across IPs
- **Clear Cache**: Regular cleanup
- **Monitor Resources**: Watch CPU/memory usage

### Debug Mode
Enable detailed logging for troubleshooting:
```bash
export VIEWBOT_DEBUG=1
```

## Legal and Ethical Considerations

### Important Notes
- **Terms of Service**: Review YouTube's ToS
- **Rate Limiting**: Respect platform limits
- **Responsible Use**: Avoid excessive automation
- **Legal Compliance**: Follow local regulations
- **Ethical Usage**: Use for legitimate purposes only

### Best Practices
- **Moderate Usage**: Avoid excessive view generation
- **Natural Patterns**: Use random delays and timing
- **Quality Content**: Focus on legitimate videos
- **Respect Limits**: Don't overwhelm servers
- **Monitor Impact**: Watch for detection signals

## Integration with NexusHub

The YouTube ViewBot is fully integrated with NexusHub:
- **Consistent UI/UX**: Matches NexusHub design
- **Shared Infrastructure**: Uses common components
- **Unified Logging**: Integrated notification system
- **Export Integration**: Works with NexusHub export features
- **Settings Management**: Unified configuration system

## Future Enhancements

Planned features for future updates:
- **AI-powered Behavior**: Machine learning for natural patterns
- **Advanced Analytics**: Detailed performance insights
- **Multi-platform Support**: Support for other video platforms
- **Cloud Integration**: Remote execution capabilities
- **API Integration**: RESTful API for automation
- **Mobile Support**: Mobile device simulation

## Support

For issues or feature requests:
1. Check the troubleshooting section
2. Review error logs
3. Test with reduced settings
4. Contact NexusHub support

---

**Note**: This tool is for educational and legitimate testing purposes. Use responsibly and in compliance with YouTube's Terms of Service and applicable laws.
