const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3001;

// Serve static files
app.use(express.static(path.join(__dirname)));
app.use(express.json());

// Tool metadata
const toolInfo = {
    name: "YouTube ViewBot Pro",
    description: "Advanced YouTube view generation with AI-powered features",
    version: "3.0.0",
    author: "NexusHub",
    category: "Social Media",
    icon: "🌌",
    tags: ["youtube", "views", "automation", "social media"],
    features: [
        "Multi-video queue processing",
        "Concurrent view generation",
        "User-agent spoofing",
        "Proxy support",
        "Real-time statistics",
        "Export functionality"
    ]
};

// API Routes
app.get('/api/info', (req, res) => {
    res.json(toolInfo);
});

app.get('/api/status', (req, res) => {
    // Check if Python backend is running
    const isRunning = global.viewbotProcess && !global.viewbotProcess.killed;
    res.json({
        status: isRunning ? 'running' : 'stopped',
        timestamp: new Date().toISOString()
    });
});

app.post('/api/start', (req, res) => {
    const { url, settings } = req.body;
    
    if (!url) {
        return res.status(400).json({ error: 'YouTube URL is required' });
    }

    try {
        // Start Python backend process
        const pythonProcess = spawn('python', ['main.py'], {
            cwd: __dirname,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        global.viewbotProcess = pythonProcess;

        // Send configuration to Python process
        const config = {
            url: url,
            settings: settings || {}
        };

        pythonProcess.stdin.write(JSON.stringify(config) + '\n');

        // Handle process output
        pythonProcess.stdout.on('data', (data) => {
            console.log('ViewBot Output:', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error('ViewBot Error:', data.toString());
        });

        pythonProcess.on('close', (code) => {
            console.log(`ViewBot process exited with code ${code}`);
            global.viewbotProcess = null;
        });

        res.json({ 
            success: true, 
            message: 'ViewBot started successfully',
            pid: pythonProcess.pid
        });

    } catch (error) {
        console.error('Error starting ViewBot:', error);
        res.status(500).json({ 
            error: 'Failed to start ViewBot',
            details: error.message 
        });
    }
});

app.post('/api/stop', (req, res) => {
    try {
        if (global.viewbotProcess && !global.viewbotProcess.killed) {
            global.viewbotProcess.kill('SIGTERM');
            global.viewbotProcess = null;
            res.json({ 
                success: true, 
                message: 'ViewBot stopped successfully' 
            });
        } else {
            res.json({ 
                success: true, 
                message: 'ViewBot was not running' 
            });
        }
    } catch (error) {
        console.error('Error stopping ViewBot:', error);
        res.status(500).json({ 
            error: 'Failed to stop ViewBot',
            details: error.message 
        });
    }
});

app.post('/api/queue', (req, res) => {
    const { action, data } = req.body;
    
    try {
        switch (action) {
            case 'add':
                // Add video to queue
                if (!data.url) {
                    return res.status(400).json({ error: 'URL is required' });
                }
                // Implementation for adding to queue
                res.json({ success: true, message: 'Video added to queue' });
                break;
                
            case 'remove':
                // Remove video from queue
                if (!data.index && data.index !== 0) {
                    return res.status(400).json({ error: 'Index is required' });
                }
                // Implementation for removing from queue
                res.json({ success: true, message: 'Video removed from queue' });
                break;
                
            case 'clear':
                // Clear entire queue
                // Implementation for clearing queue
                res.json({ success: true, message: 'Queue cleared' });
                break;
                
            default:
                res.status(400).json({ error: 'Invalid action' });
        }
    } catch (error) {
        console.error('Queue operation error:', error);
        res.status(500).json({ 
            error: 'Queue operation failed',
            details: error.message 
        });
    }
});

app.get('/api/stats', (req, res) => {
    // Return current statistics
    const stats = {
        totalViews: global.totalViews || 0,
        activeThreads: global.activeThreads || 0,
        successRate: global.successRate || 0,
        queueLength: global.queueLength || 0,
        viewsToday: global.viewsToday || 0,
        viewsWeek: global.viewsWeek || 0,
        totalErrors: global.totalErrors || 0,
        avgWatchTime: global.avgWatchTime || 0,
        cpuUsage: global.cpuUsage || 0,
        memoryUsage: global.memoryUsage || 0,
        timestamp: new Date().toISOString()
    };
    
    res.json(stats);
});

app.post('/api/settings', (req, res) => {
    const { action, settings } = req.body;
    
    try {
        const settingsFile = path.join(__dirname, 'settings.json');
        
        switch (action) {
            case 'save':
                fs.writeFileSync(settingsFile, JSON.stringify(settings, null, 2));
                res.json({ success: true, message: 'Settings saved' });
                break;
                
            case 'load':
                if (fs.existsSync(settingsFile)) {
                    const savedSettings = JSON.parse(fs.readFileSync(settingsFile, 'utf8'));
                    res.json({ success: true, settings: savedSettings });
                } else {
                    res.json({ success: true, settings: {} });
                }
                break;
                
            default:
                res.status(400).json({ error: 'Invalid action' });
        }
    } catch (error) {
        console.error('Settings operation error:', error);
        res.status(500).json({ 
            error: 'Settings operation failed',
            details: error.message 
        });
    }
});

app.post('/api/export', (req, res) => {
    const { type, data } = req.body;
    
    try {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        let filename, content;
        
        switch (type) {
            case 'logs':
                filename = `viewbot-logs-${timestamp}.txt`;
                content = data.logs.join('\n');
                break;
                
            case 'stats':
                filename = `viewbot-stats-${timestamp}.json`;
                content = JSON.stringify(data.stats, null, 2);
                break;
                
            case 'queue':
                filename = `viewbot-queue-${timestamp}.json`;
                content = JSON.stringify(data.queue, null, 2);
                break;
                
            default:
                return res.status(400).json({ error: 'Invalid export type' });
        }
        
        const exportPath = path.join(__dirname, 'exports', filename);
        
        // Ensure exports directory exists
        const exportsDir = path.join(__dirname, 'exports');
        if (!fs.existsSync(exportsDir)) {
            fs.mkdirSync(exportsDir, { recursive: true });
        }
        
        fs.writeFileSync(exportPath, content);
        
        res.json({ 
            success: true, 
            message: 'Export completed',
            filename: filename,
            path: exportPath
        });
        
    } catch (error) {
        console.error('Export error:', error);
        res.status(500).json({ 
            error: 'Export failed',
            details: error.message 
        });
    }
});

// Serve the main tool interface
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'tool.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        tool: toolInfo.name,
        version: toolInfo.version,
        timestamp: new Date().toISOString()
    });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Server error:', error);
    res.status(500).json({
        error: 'Internal server error',
        message: error.message
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🌌 YouTube ViewBot Pro server running on port ${PORT}`);
    console.log(`📊 Tool: ${toolInfo.name} v${toolInfo.version}`);
    console.log(`🌐 Access: http://localhost:${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down YouTube ViewBot Pro...');
    
    if (global.viewbotProcess && !global.viewbotProcess.killed) {
        global.viewbotProcess.kill('SIGTERM');
    }
    
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Received SIGTERM, shutting down...');
    
    if (global.viewbotProcess && !global.viewbotProcess.killed) {
        global.viewbotProcess.kill('SIGTERM');
    }
    
    process.exit(0);
});

module.exports = app; 